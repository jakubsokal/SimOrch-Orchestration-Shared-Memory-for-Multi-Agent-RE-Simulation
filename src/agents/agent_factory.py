from .helper_agent import HelperAgent
from .re_agent import REAgent
from .user_agent import UserAgent
from ..llm import LLMFactory
from .agent_types import AgentRole

class AgentFactory:
    AGENT_TYPE_MAP = {
        AgentRole.RE_AGENT: REAgent,
        AgentRole.USER_AGENT: UserAgent,
        AgentRole.HELPER_AGENT: HelperAgent
    }
    
    def create_agent(agent_cfg, description, seed, scenarioTruths=None):
        llm = LLMFactory.create_llm(agent_cfg, seed=seed)

        agent_class = AgentFactory.AGENT_TYPE_MAP.get(AgentRole(agent_cfg['role']))
        if not agent_class:
            raise ValueError(f"Unknown agent role: {agent_cfg['role']}")

        return agent_class(
            name = agent_cfg['name'],
            role = agent_cfg['role'],
            llm = llm,
            context_prompt=agent_cfg['context_prompt'],
            description=description,
            max_words=agent_cfg.get('max_words', 500),
            persona=agent_cfg.get('persona', None),
            scenario_truths=scenarioTruths if agent_class == AgentFactory.AGENT_TYPE_MAP[AgentRole.USER_AGENT] 
                            else None
        )  