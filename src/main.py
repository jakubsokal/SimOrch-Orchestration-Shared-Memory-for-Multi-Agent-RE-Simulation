import os

from .orchestrator import Orchestrator
from .context import LoadScenario
from .agents import AgentFactory
from .memory import SharedMemory
from .logs import Logger
import time, datetime, random
from dotenv import load_dotenv

load_dotenv()

def main():
    timestamp = datetime.datetime.now().isoformat()
    start_time = time.time()

    status = "completed"
    error = None
    seed = None
    turn_counter = 1
    args = LoadScenario.args_load()
    context = LoadScenario.load(args.config)

    logger = Logger(scenario_id=context.get("scenario", {}).get("id", None))
    api_key = os.getenv('OPEN_AI_KEY')

    print(f"[Main] Starting simulation at {timestamp}")

    seed = context.get("scenario").get("seed", 42)

    random.seed(seed)
    try:
        re_agents = {}
        user_agents = {}

        agent_configs = context.get("re_agents", []) + context.get("user_agents", [])
        
        for agent_config in agent_configs:
            effective_api_key = agent_config.get('api_key') or api_key
            agent_cfg = {**agent_config, 'api_key': effective_api_key}
            
            agent = AgentFactory.create_agent(agent_cfg, context.get("scenario").get("description", ""),
                                               seed=seed, scenarioTruths=context.get("scenarioTruths", []))
            if agent.role == 1:
                re_agents[agent.name] = agent
            elif agent.role == 2:
                user_agents[agent.name] = agent
            print(f"[LLM Factory] Created agent: {agent.name} Role: ({agent.role})")
        
        helper_agent = AgentFactory.create_agent(
            {
                'name': 'Analyst Agent',
                'role': 3,
                'model': 'gpt-4o-mini',
                'provider': 'OPENAI',
                'params': {
                    'temperature': 0,
                },
                'context_prompt': None,
                'api_key': api_key,
            }, context.get("scenario").get("description", ""), seed=seed
        )

        print(f"[LLM Factory] Created agent: {helper_agent.name} ({helper_agent.role})")

        orchestrator = Orchestrator(
            re_agents=re_agents,
            user_agents=user_agents,
            helper_agent=helper_agent,
            max_turns=context.get("scenario", {}).get('max_turns'),
            shared_memory=SharedMemory(),
            logger=logger,
        )
        
        print(f"[Orchestrator] Starting orchestration... {context.get('scenario', {}).get('scenario_name', '')}")
        orchestrator.start(context.get("scenario", {}).get("conversation_type", "dynamic"))
        turn_counter = context.get("scenario", {}).get('max_turns', 0)

        orchestrator.logger.store_yaml(context)
    except Exception as e:
        status = "failed"
        error = e
        print(f"[Main] Simulation failed: {e}")
        try:
            if context is not None:
                orchestrator.logger.store_yaml(context)
        except Exception:
            pass
        raise
    finally:
        end_time = time.time()

        elapsed_seconds = round(end_time - start_time)
        elapsed_time = str(datetime.timedelta(seconds=elapsed_seconds))

        orchestrator.logger.store_run_details(
            timestamp,
            turn_counter,
            elapsed_time,
            seed=seed,
            successful=(status != "failed"),
            status=status,
            error=error,
        )

    elapsed_seconds = round(end_time - start_time)
    elapsed_time = str(datetime.timedelta(seconds=elapsed_seconds))
    
    orchestrator.logger.store_run_details(timestamp, orchestrator.turn_counter, elapsed_time, seed=seed)
    print(f"[Orchestrator] Elapsed time: {elapsed_time[:]}")
   
if __name__ == "__main__":
    main()
