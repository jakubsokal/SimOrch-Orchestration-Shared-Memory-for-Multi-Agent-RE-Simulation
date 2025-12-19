from agents.user_agent import UserAgent
from agents.re_agent import REAgent
from orchestrator.orchestrator import Orchestrator

def main():
    user_agent = UserAgent("user", role="stakeholder")
    re_agent = REAgent("re", role="RE")
    user_agent2 = UserAgent("user2", role="stakeholder")

    orchestrator = Orchestrator(
        agents={
            re_agent.name: re_agent,
            user_agent.name: user_agent,
            user_agent2.name: user_agent2
        },
    )
    
    orchestrator.start()
   
if __name__ == "__main__":
    main()
