import json
import re

class Orchestrator:
    def __init__(self, re_agents, user_agents, helper_agent, logger, shared_memory, max_turns=3):
        self.re_agents = re_agents
        self.user_agents = user_agents
        self.helper = helper_agent
        self.shared_memory = shared_memory
        self.max_turns = max_turns
        self.logger = logger
        self.turn_counter = 1
        
    def start(self, type):
        if type == "one_to_one":
            self.one_to_one_conversation()
        elif type == "dynamic":
            self.dynamic_conversation()

    def one_to_one_conversation(self):
        re_agent = self.re_agents[list(self.re_agents.keys())[0]]
        user_agent = self.user_agents[list(self.user_agents.keys())[0]]

        last_message = None
        role = None

        while self.turn_counter <= self.max_turns:
            re_agent_reply = re_agent.speak(last_message, role)
            self.shared_memory.write(re_agent.name, re_agent_reply, self.turn_counter, re_agent.role)
            user_agent_reply = user_agent.speak(re_agent_reply, re_agent.role)
            self.shared_memory.write(user_agent.name, user_agent_reply, self.turn_counter, user_agent.role)


            print(f"[Orchestrator] Turn {self.turn_counter} Finished")
            last_message = user_agent_reply
            role = user_agent.role

            self.turn_counter += 1

        self.logger.store(self.shared_memory.get_all_messages())

    def dynamic_conversation(self):
        reply = self.re_agents[list(self.re_agents.keys())[0]].speak(None, None)
        print(f"[Orchestrator] Initial message from {list(self.re_agents.keys())[0]}")
        
        self.shared_memory.write(
            name = self.re_agents[list(self.re_agents.keys())[0]].name,
            message = reply,
            turn = self.turn_counter,
            role = self.re_agents[list(self.re_agents.keys())[0]].role
        )
        self.turn_counter += 1

        while self.turn_counter <= self.max_turns:
            next_speaker = self.select_next_speaker()
            
            if next_speaker is None:
                print("[Orchestrator] No more speakers, ending conversation")
                break
            
            last_message = self.shared_memory.read()

            print(f"[Orchestrator] NEXT SPEAKER: {next_speaker.name}")
            
            try:
                if next_speaker.role == 1: 
                    response = next_speaker.speak(
                        last_message.get('message', ''),
                        last_message['role'], 
                        conversation_history=json.dumps(self.shared_memory.get_all_messages()), 
                        analyst_output=json.dumps(self.shared_memory.get_requirements() + self.shared_memory.get_issues())
                    )
                elif next_speaker.role == 2:
                    response = next_speaker.speak(
                        last_message.get('message', ''), 
                        last_message['role'], 
                        conversation_history=json.dumps(self.shared_memory.get_all_messages())
                )
            except Exception as e:
                print(f"[Orchestrator] ERROR during agent speak: {e}")
                response = "I'm sorry, I encountered an error and cannot respond at this time."

            self.shared_memory.write(
                name = next_speaker.name,
                message = response,
                turn = self.turn_counter,
                role = next_speaker.role
            )
            self.turn_counter += 1
        self.finish_conversation()

    def ordered_conversation(self):
        agents = {self.re_agents, self.user_agents}
        last_message = None
        role = None

        while self.turn_counter <= self.max_turns: 
            agent = agents[list(agents.keys())[(self.turn_counter - 1) % len(agents)]]
            last_message = self.shared_memory.read()
                
            last_message_text = None
            last_agent_role = None
            if last_message is not None:
                last_message_text = last_message.get('message', '')
                last_agent_role = last_message['role']
                
            reply = agent.speak(last_message_text, last_agent_role)

            self.shared_memory.write(agent.name, reply, self.turn_counter, agent.role)
            
            print(f"[Turn {self.turn_counter}] Finished")
            self.turn_counter += 1

        self.logger.store(self.shared_memory.get_all_messages())

    def select_next_speaker(self):
        last_message = self.shared_memory.read()
        
        print(f"[Orchestrator] Selecting next speaker based on last message: {last_message}")
        if last_message is None:
            return self.re_agents[list(self.re_agents.keys())[0]]
        
        last_role = last_message['role']
        print(f"[Orchestrator] Last message role: {last_role}")

        if last_role == 1:
            return self.select_stakeholder()
        
        elif last_role == 2:
            message_content = last_message.get('message', '')
            self.information_extraction(message_content, self.turn_counter, last_message['agent'], last_message['id'])

            return self.re_agents[list(self.re_agents.keys())[0]]
        
        return self.re_agents[list(self.re_agents.keys())[0]]
    
    def select_stakeholder(self):
        if len(self.user_agents) == 1:
            return list(self.user_agents.values())[0]
        
        stakeholder_names = list(self.user_agents.keys())
        last_stakeholder_turn = None
        
        for message in reversed(self.shared_memory.get_all_messages()):
            if message['role'] == 2:
                last_stakeholder_turn = message['agent']
                break
        
        if last_stakeholder_turn and last_stakeholder_turn in stakeholder_names:
            current_index = stakeholder_names.index(last_stakeholder_turn)
            next_index = (current_index + 1) % len(stakeholder_names)
            
            return self.user_agents[stakeholder_names[next_index]]
        
        print(f"[Orchestrator] I got here {stakeholder_names[0]}")
        return self.user_agents[stakeholder_names[0]]

    def information_extraction(self, message, turn_number, stakeholder_name, message_id):
        if not self.helper:
            return
        
        print(f"\n[Orchestrator] Running extraction on turn {turn_number}...")
        
        req_result_str = self.helper.speak(
            message=message,
            type="REQUIREMENT",
            existing_requirements=json.dumps(self.shared_memory.get_requirements())
        )

        print(f"[Orchestrator] Extraction result: {req_result_str}")
        
        try:
            print(f"[Orchestrator] Parsing requirement extraction result...\n{req_result_str}")
            req_result = parse_json_response(req_result_str)
            if req_result is None:
                req_result = {"requirements": []}
        except Exception as e:
            print(f"[Orchestrator] ERROR during requirements extraction: {e}")
            req_result = {"requirements": []}

    #saving requirements to shared memory
        self.shared_memory.save_requirements(
            stakeholder_name=stakeholder_name,
            trace_message_id=message_id,
            turn_id=turn_number,
            requirements=req_result.get('requirements', [])
        )

        issue_result_str = self.helper.speak(
            message=message,
            type="ISSUE",
            existing_requirements=json.dumps(self.shared_memory.get_requirements()),
            existing_issues=json.dumps(self.shared_memory.get_issues())
        )

        print(f"[Orchestrator] Issue detection result: {issue_result_str}")
        
        try:
            issue_result = parse_json_response(issue_result_str)
            if issue_result is None:
                issue_result = {"issues": []}
        except Exception as e:
            print(f"[Orchestrator] ERROR during issues extraction: {e}")
            issue_result = {"issues": []}
        
        self.shared_memory.save_issues(
            stakeholder_name=stakeholder_name,
            trace_message_id=message_id,
            turn_id=turn_number,
            issues=issue_result.get('issues', []),
        )

    def finish_conversation(self):
        print("\n[Orchestrator] Finalising conversation...")
        
        all_requirements = self.shared_memory.get_requirements()
        all_issues = self.shared_memory.get_issues()
        all_transcript = self.shared_memory.get_all_messages()
        
        self.logger.store(
            memory=all_transcript,
            requirements=all_requirements,
            issues=all_issues,
        )
        
        print(f"[Orchestrator] Conversation completed with summary:")
        print(f"  - Total turns: {self.turn_counter - 1}")
        print(f"  - RE Agents: {len(self.re_agents)}")
        print(f"  - Stakeholders: {len(self.user_agents)}")
        print(f"  - Requirements: {len(all_requirements)}")
        print(f"  - Issues: {len(all_issues)}")

def parse_json_response(raw: str) -> dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    print(f"[Orchestrator] Extracted JSON string: {match.group() if match else 'No match found'}")
    if not match:
        raise ValueError("No JSON found in response")
    
    return json.loads(match.group())