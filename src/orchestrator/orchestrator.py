import json
import re
from ..agents.agent_types import AgentRole

STOP_SIMULATION = "STOP_SIMULATION"
MAX_VALIDATION_RETRIES = 3

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

        agents = [re_agent, user_agent]
        last_message = None

        while self.turn_counter <= self.max_turns:
            select_agent = agents[(self.turn_counter - 1) % len(agents)]    

            response = None
            if select_agent.role == AgentRole.RE_AGENT: 
                response = select_agent.speak(
                    message = last_message.get('message', '') if last_message else None, 
                    role=last_message['role'] if last_message else None,
                    conversation_history=self.shared_memory.get_messages_formatted(exclude_last=True),
                    saved_context=self.shared_memory.get_requirements_formatted() 
                                + self.shared_memory.get_issues_formatted()
                    
                )
            elif select_agent.role == AgentRole.USER_AGENT:
                response = select_agent.speak(
                    message=last_message.get('message', '') if last_message else None,
                    role=last_message['role'] if last_message else None,
                    conversation_history=self.shared_memory.get_messages_formatted(exclude_last=True)
                )

            saved_message_id = self.shared_memory.write(
                name = select_agent.name,
                message = response,
                turn = self.turn_counter,
                role = select_agent.role
            )

            if (select_agent.role == AgentRole.USER_AGENT):
                self.information_extraction(
                    message=response,
                    turn_number=self.turn_counter,
                    stakeholder_name=select_agent.name,
                    message_id=saved_message_id
                )

            print(f"[Orchestrator] Turn {self.turn_counter} Finished")
            last_message = self.shared_memory.read()

            self.turn_counter += 1

        self.finish_conversation()

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
                        conversation_history=self.shared_memory.get_messages_formatted(exclude_last=True),
                        saved_context=self.shared_memory.get_requirements_formatted() 
                                    + self.shared_memory.get_issues_formatted()
                    )

                    if response and STOP_SIMULATION in response:
                            print(f"[Orchestrator] RE agent signalled {STOP_SIMULATION} ending simulation.")
                            self.finish_conversation()
                            return
                    
                elif next_speaker.role == 2:
                    response = next_speaker.speak(
                        last_message.get('message', ''),
                        last_message['role'],
                        conversation_history=self.shared_memory.get_messages_formatted(exclude_last=True)
                    )
            except Exception as e:
                print(f"[Orchestrator] ERROR during agent speak: {e}")
                response = "I'm sorry, I encountered an error and cannot respond at this time."

            if response is None:
                print(f"[Orchestrator] Unknown role {next_speaker.role}, skipping.")
                continue

            saved_message_id = self.shared_memory.write(
                name = next_speaker.name,
                message = response,
                turn = self.turn_counter,
                role = next_speaker.role
            )

            if next_speaker.role == 2:
                self.information_extraction(
                    message=response,
                    turn_number=self.turn_counter,
                    stakeholder_name=next_speaker.name,
                    message_id=saved_message_id
                )

            self.turn_counter += 1
        self.finish_conversation()

    def ordered_conversation(self):
        agents = {self.re_agents, self.user_agents}
        last_message = None

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
        
        print(f"[Orchestrator] Selecting next speaker based on last message...")
        if last_message is None:
            return self.re_agents[list(self.re_agents.keys())[0]]
        
        last_role = last_message['role']
        print(f"[Orchestrator] Last message role: {last_role}")

        if last_role == 1:
            return self.select_stakeholder()
        
        elif last_role == 2:
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
        
        return self.user_agents[stakeholder_names[0]]

    def information_extraction(self, message, turn_number, stakeholder_name, message_id):
        if not self.helper:
            return
        
        print(f"\n[Orchestrator] Running extraction on turn {turn_number}...")
        
        req_result_str = self.helper.speak(
            message=message,
            type="REQUIREMENT",
            existing_requirements=self.shared_memory.get_requirements_formatted(),
        )

        try:
            print(f"[Orchestrator] Parsing requirement extraction result...\n{req_result_str}")
            req_result = parse_json_response(req_result_str)
            if req_result is None:
                req_result = {"requirements": []}
        except Exception as e:
            print(f"[Orchestrator] ERROR during requirements extraction: {e}")
            req_result = {"requirements": []}

        if req_result.get("resolves_req_id"):
            self.shared_memory.resolve_requirement(
                req_id=req_result["resolves_req_id"],
                confirmed_by_turn=turn_number
            )
        elif req_result.get("requirements"): 
            validation_result = self.validate_extraction(
                message=message,
                extraction=req_result,
                extraction_type="REQUIREMENT"
            )

            print(f"[Orchestrator] Extraction result: {validation_result}")
            
            #saving requirements to shared memory
            self.shared_memory.save_requirements(
                stakeholder_name=stakeholder_name,
                trace_message_id=message_id,
                turn_id=turn_number,
                requirements=validation_result.get('requirements', [])
            )

        issue_result_str = self.helper.speak(
            message=message,
            type="ISSUE",
            existing_requirements=self.shared_memory.get_requirements_formatted(),
            existing_issues=self.shared_memory.get_issues_formatted()
        )
        try:
            issue_result = parse_json_response(issue_result_str)
            if issue_result is None:
                issue_result = {"issues": []}
        except Exception as e:
            print(f"[Orchestrator] ERROR during issues extraction: {e}")
            issue_result = {"issues": []}

        if issue_result.get("issues"):
            validation_result = self.validate_extraction(
                message=message,
                extraction=issue_result,
                extraction_type="ISSUE"
            )

            print(f"[Orchestrator] Issue detection result: {validation_result}")
            
            self.shared_memory.save_issues(
                stakeholder_name=stakeholder_name,
                trace_message_id=message_id,
                turn_id=turn_number,
                issues=validation_result.get('issues', []),
            )

    def validate_extraction(self, message, extraction, extraction_type):
        re_agent = self.re_agents[list(self.re_agents.keys())[0]]

        last_saved = self.shared_memory.read()
        exclude_last = bool(last_saved and last_saved.get('message') == message)

        for attempt in range(MAX_VALIDATION_RETRIES):
            print(f"[Orchestrator] RE validating {extraction_type} extraction "
                  f"(attempt {attempt + 1}/{MAX_VALIDATION_RETRIES})...")
 
            validation_str = re_agent.speak(
                message=message,
                role=AgentRole.VALIDATE,
                conversation_history=self.shared_memory.get_messages_formatted(exclude_last=exclude_last),
                current_extraction=json.dumps(extraction),
                saved_extractions=self.shared_memory.get_requirements_formatted() 
                    if extraction_type == "REQUIREMENT" 
                    else self.shared_memory.get_issues_formatted(),
                extraction_type=extraction_type
            )
 
            print(f"[Orchestrator] RE validation response: {validation_str}")
 
            try:
                validation = parse_json_response(validation_str)
            except Exception as e:
                print(f"[Orchestrator] Could not parse RE validation response: {e}")
                # If RE validation itself fails, return what we have
                return extraction
 
            if validation is None:
                return extraction

            validated = validation.get("validated", False)
            corrections  = validation.get("corrections", [])
            missed_items = validation.get("missed_items", [])
            
            if validated:
                print(f"[Orchestrator] {extraction_type} extraction validated by RE.")
                return extraction

            if not validated and not corrections and not missed_items:
                print(f"[Orchestrator] RE returned validated=false with empty lists. Treating as validated.")
                return extraction
            
            print(f"[Orchestrator] RE found {len(corrections)} correction(s) and "
                  f"{len(missed_items)} missed item(s). Re-extracting...")
 
            if extraction_type == "REQUIREMENT":
                re_extract_str = self.helper.speak(
                    message=message,
                    type="REQUIREMENT_CORRECTION",
                    existing_requirements=self.shared_memory.get_requirements_formatted(),
                    corrections=json.dumps(corrections),
                    missed_items=json.dumps(missed_items)
                )
                try:
                    new_extraction = parse_json_response(re_extract_str)
                    extraction = new_extraction if new_extraction else extraction
                except Exception as e:
                    print(f"[Orchestrator] Re-extraction parse error: {e}")
                    return extraction
 
            elif extraction_type == "ISSUE":
                re_extract_str = self.helper.speak(
                    message=message,
                    type="ISSUE_CORRECTION",
                    existing_requirements=self.shared_memory.get_requirements_formatted(),
                    existing_issues=self.shared_memory.get_issues_formatted(),
                    corrections=json.dumps(corrections),
                    missed_items=json.dumps(missed_items)
                )
                try:
                    new_extraction = parse_json_response(re_extract_str)
                    extraction = new_extraction if new_extraction else extraction
                except Exception as e:
                    print(f"[Orchestrator] Re-extraction parse error: {e}")
                    return extraction
 
        print(f"[Orchestrator] Max retries reached for {extraction_type} validation. "
              f"Saving best available extraction.")
        return extraction

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

def parse_json_response(raw: str):
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    print(f"[Orchestrator] Extracted JSON string: {match.group() if match else 'No match found'}")
    if not match:
        raise ValueError("No JSON found in response")
    
    return json.loads(match.group())