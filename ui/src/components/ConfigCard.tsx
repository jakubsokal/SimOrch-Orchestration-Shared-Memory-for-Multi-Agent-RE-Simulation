import { type FC } from 'react';
import { AgentType, AgentTypeLabels } from '../types/agentType';
import { type REAgentConfig } from './ReAgentConfigCard';
import { type UserAgentConfig } from './UserAgentConfigCard';

type ScenarioConfig = {
    scenario: {
        scenario_name?: string;
        description?: string;
        domain?: string;
        system_type?: string;
        seed?: number;
        max_turns?: number;
        conversation_type?: string;
    }
    re_agents?: REAgentConfig[];
    user_agents?: UserAgentConfig[];

};

interface ConfigCardProps {
    config: ScenarioConfig;
}

export type AnyAgentConfig = REAgentConfig | UserAgentConfig;

const ConfigCard: FC<ConfigCardProps> = ({ config }) => {

    const reAgents = Array.isArray(config?.re_agents) ? config.re_agents : [];
    const userAgents = Array.isArray(config?.user_agents) ? config.user_agents : [];

    const agents = [...reAgents, ...userAgents];

    function isREAgent(agent: AnyAgentConfig): agent is REAgentConfig {
        return agent.role === AgentType.REQUIREMENTS_ENGINEER;
    }

    function isStakeholder(agent: AnyAgentConfig): agent is UserAgentConfig {
        return agent.role === AgentType.STAKEHOLDER;
    }

    return (
        <div className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow pb-8">
            <div className="p-5 border-b border-gray-200 bg-white">
                <div className="flex items-start gap-3">
                    <div className="shrink-0 w-10 h-10 rounded bg-blue-50 border border-blue-200 flex items-center justify-center">
                        <span className="text-xs font-semibold text-blue-700">YAML</span>
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                                Scenario
                            </span>
                            {config?.scenario.scenario_name ? (
                                <span className="text-base font-semibold text-gray-900">
                                    {config.scenario.scenario_name}
                                </span>
                            ) : (
                                <span className="text-base text-gray-500">Unnamed scenario</span>
                            )}
                        </div>
                        {config?.scenario.description ? (
                            <p className="text-sm text-gray-700">{config.scenario.description}</p>
                        ) : (
                            <p className="text-sm text-gray-500">No description provided</p>
                        )}
                    </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-3">
                    <div className="px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                        <p className="text-[11px] uppercase text-gray-500 mb-1">Seed</p>
                        <p className="text-sm font-medium text-gray-900">{config?.scenario.seed ?? 'N/A'}</p>
                    </div>
                    <div className="px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                        <p className="text-[11px] uppercase text-gray-500 mb-1">Max Turns</p>
                        <p className="text-sm font-medium text-gray-900">{config?.scenario.max_turns ?? 'N/A'}</p>
                    </div>
                    <div className="px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                        <p className="text-[11px] uppercase text-gray-500 mb-1">Domain</p>
                        <p className="text-sm font-medium text-gray-900">{config?.scenario.domain ?? 'N/A'}</p>
                    </div>
                    <div className="px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                        <p className="text-[11px] uppercase text-gray-500 mb-1">System Type</p>
                        <p className="text-sm font-medium text-gray-900">{config?.scenario.system_type ?? 'N/A'}</p>
                    </div>
                    <div className="px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                        <p className="text-[11px] uppercase text-gray-500 mb-1">Conversation Type</p>
                        <p className="text-sm font-medium text-gray-900">{config?.scenario.conversation_type ?? 'N/A'}</p>
                    </div>
                </div>
            </div>

            <div className="p-5 bg-white">
                {agents.length > 0 ? (
                    <div>
                        <p className="text-sm text-gray-500 mb-3">Agents</p>
                        <div className="space-y-3">
                            {agents.map((agent, index) => (
                                <div
                                    key={`${agent.name ?? 'agent'}-${index}`}
                                    className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                                >
                                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                                        <span className="text-sm font-semibold text-gray-900">
                                            {agent.name || `Agent ${index + 1}`}
                                        </span>
                                        {agent.role && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium border border-gray-300">
                                                {AgentTypeLabels[agent.role as AgentType] || `Unknown Role (${agent.role})`}
                                            </span>
                                        )}
                                        {agent.provider && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                                                {agent.provider}
                                            </span>
                                        )}
                                        {agent.model && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                                                {agent.model}
                                            </span>
                                        )}
                                    </div>
                                    {agent.params && Object.keys(agent.params).length > 0 ? (
                                        <div className="grid grid-cols-2 gap-3 mb-2">
                                            {Object.entries(agent.params).map(([key, value]) => (
                                                <div key={key}>
                                                    <p className="text-[11px] uppercase text-gray-500 mb-1">{key}</p>
                                                    <p className="text-sm text-gray-900">{String(value)}</p>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500 mb-2">No params provided.</p>
                                    )}

                                    {isREAgent(agent) && (
                                        <div className="grid grid-cols-2 gap-3 mb-2">
                                            {[
                                                { label: 'Experience Level', value: agent.persona.experience_level },
                                                { label: 'Questioning Strategy', value: agent.persona.questioning_strategy },
                                                { label: 'Probing Intensity', value: agent.persona.probing_intensity },
                                                { label: 'Requirement Focus', value: agent.persona.requirement_focus },
                                                { label: 'Tone', value: agent.persona.tone },
                                            ].filter(f => f.value).map(({ label, value }) => (
                                                <div key={label}>
                                                    <p className="text-[11px] uppercase text-gray-500 mb-1">{label}</p>
                                                    <p className="text-sm text-gray-900">{value}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {isStakeholder(agent) && (
                                        <div className="grid grid-cols-2 gap-3 mb-2">
                                            {[
                                                { label: 'Domain Knowledge', value: agent.persona.domain_knowledge_level },
                                                { label: 'Communication Style', value: agent.persona.communication_style },
                                                { label: 'Clarity Level', value: agent.persona.clarity_level },
                                                { label: 'Revelation Strategy', value: agent.persona.revelation_strategy },
                                                { label: 'Revelation Rate', value: agent.persona.revelation_rate },
                                            ].filter(f => f.value).map(({ label, value }) => (
                                                <div key={label}>
                                                    <p className="text-[11px] uppercase text-gray-500 mb-1">{label}</p>
                                                    <p className="text-sm text-gray-900">{value}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {agent.context_prompt ? (
                                        <div className="bg-white border border-gray-200 rounded p-3">
                                            <p className="text-[11px] uppercase text-gray-500 mb-1">Context Prompt</p>
                                            <p className="text-sm text-gray-800">{agent.context_prompt}</p>
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500">No context prompt provided.</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <p className="text-sm text-gray-500">No agent configuration provided.</p>
                )}
            </div>
        </div>
    );
};

export default ConfigCard;