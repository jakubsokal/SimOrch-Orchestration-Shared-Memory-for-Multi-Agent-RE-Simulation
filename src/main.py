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
    args = LoadScenario.args_load()
    context = LoadScenario.load(args.config)
    api_key = os.getenv('OPEN_AI_KEY')

    print(f"[Main] Starting simulation at {timestamp} with config: {context}")

    seed = context.get("scenario").get("seed", 42)

    random.seed(seed)

    re_agents = {}
    user_agents = {}

    agent_configs = context.get("re_agents", []) + context.get("user_agents", [])
    
    for agent_config in agent_configs:
        agent = AgentFactory.create_agent(agent_config, context.get("scenario").get("description", ""), seed=seed)
        print(f"[Main] Adding RE Agent: {agent.name}, Role: {agent.role}")
        if agent.role == 1:
            
            re_agents[agent.name] = agent
        elif agent.role == 2:
            user_agents[agent.name] = agent
        print(f"[LLM Factory] Created agent: {agent.name} ({agent.role})")
    
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
        re_agents = re_agents,
        user_agents = user_agents,
        helper_agent = helper_agent,
        max_turns = context.get("scenario", {}).get('max_turns'),
        shared_memory = SharedMemory(),
        logger = Logger()
    )
    
    print("[Orchestrator] Starting orchestration...")
    orchestrator.start("dynamic")

    orchestrator.logger.store_yaml(context)

    end_time = time.time()

    elapsed_seconds = round(end_time - start_time)
    elapsed_time = str(datetime.timedelta(seconds=elapsed_seconds))
    
    orchestrator.logger.store_run_details(timestamp, orchestrator.turn_counter, elapsed_time, seed=seed)
    print(f"[Orchestrator] Elapsed time: {elapsed_time[:]}")
   
if __name__ == "__main__":
    main()
