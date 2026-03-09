import { type FC } from 'react';
import { ChevronLeft, ChevronRight, Trash2 } from 'lucide-react';
import FormInput from './shared/FormInput';
import Button from './shared/Button';
import { type Provider } from './shared/LLMSetup';
import LLMSetup from './shared/LLMSetup';
import SelectButton from './shared/SelectButton';

export interface UserAgentConfig {
    name: string;
    role?: number; // 1 for RE Agent, 2 for User Agent
    persona: { 
        communication_style: string;
        domain_knowledge_level: string;
        clarity_level: string;
        revelation_strategy: string;
        revelation_rate: string;
    },
    provider: Provider;
    model: string;
    params: {
        temperature: number;
        top_p: number;
        max_tokens: number;
    };
    context_prompt: string;
    api_key?: string;
}

interface UserAgentConfigCardProps {
    predefined?: boolean;
    agents: UserAgentConfig[];
    onChange: (agents: UserAgentConfig[]) => void;
    onSubmit: () => void;
    onBack: () => void;
    running: boolean;
}

const OPTIONS = {
    communication_style: ['cooperative', 'vague', 'verbose', 'concise', 'impatient'],
    domain_knowledge_level: ['low', 'medium', 'high'],
    clarity_level: ['clear', 'partially_clear', 'unclear'],
    revelation_strategy: ['reactive', 'proactive', 'reluctant'],
    revelation_rate: ['slow', 'medium', 'fast'],
};

const LABELS: Record<string, string> = {
    communication_style: 'Communication Style',
    domain_knowledge_level: 'Domain Knowledge',
    clarity_level: 'Clarity Level',
    revelation_strategy: 'Revelation Strategy',
    revelation_rate: 'Revelation Rate',
    provider: 'Model Provider',
    model: 'Model',
    temperature: 'Temperature',
    top_p: 'Top-p',
    max_tokens: 'Max Tokens',
};

export const DEFAULT_AGENT: UserAgentConfig = {
    name: '',
    role: 2,
    persona: {
        communication_style: '',
        domain_knowledge_level: '',
        clarity_level: '',
        revelation_strategy: '',
        revelation_rate: '',
    },
    provider: 'ollama',
    model: 'llama2',
    params: {
        temperature: 0.0,
        top_p: 1.0,
        max_tokens: 512,
    },
    context_prompt: '',
    api_key: '',
};

const UserAgentConfigCard: FC<UserAgentConfigCardProps> = ({ predefined, agents, onChange, onSubmit, onBack, running }) => {
    const updateAgent = (index: number, updated: UserAgentConfig) => {
        onChange(agents.map((a, i) => i === index ? updated : a));
    };

    const addAgent = () => onChange([...agents, { ...DEFAULT_AGENT }]);

    const removeAgent = (index: number) => onChange(agents.filter((_, i) => i !== index));

    const isValid = agents.length > 0 &&
        agents.every(agent =>
            agent.name.trim() !== '' &&
            agent.persona.communication_style !== '' &&
            agent.persona.domain_knowledge_level !== '' &&
            agent.persona.clarity_level !== '' &&
            agent.persona.revelation_strategy !== '' &&
            agent.persona.revelation_rate !== ''
        );

    return (
        <div className="p-6 max-w-3xl mx-auto space-y-6 pb-24">
            <div className="flex items-start justify-between">
                <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-1">User Agent Configuration</h4>
                    <p className="text-sm text-gray-500">Configure stakeholder simulation behaviour and personas.</p>
                </div>
                {!predefined && (
                    <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
                        <button
                            onClick={() => agents.length > 1 && removeAgent(agents.length - 1)}
                            className="w-6 h-6 flex items-center justify-center rounded border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-colors text-sm"
                        >
                            −
                        </button>
                        <span className="text-sm font-semibold text-gray-900 min-w-5 text-center">
                            {agents.length}
                        </span>
                        <button
                            onClick={addAgent}
                            className="w-6 h-6 flex items-center justify-center rounded border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-colors text-sm"
                        >
                            +
                        </button>
                        <span className="text-xs text-gray-500 ml-1">User Agents</span>
                    </div>
                )}
            </div>

            {predefined ? (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-700">
                        You are using a predefined scenario. The user agent configuration has been set automatically.
                    </p>
                </div>
            ) : (
                <>
                    {agents.map((agent, i) => (
                        <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="w-7 h-7 rounded-md bg-green-50 flex items-center justify-center text-sm">👤</div>
                                    <span className="text-sm font-semibold text-gray-900">User Agent {i + 1}</span>
                                </div>
                                {agents.length > 1 && (
                                    <button onClick={() => removeAgent(i)} className="text-gray-400 hover:text-red-500 transition-colors">
                                        <Trash2 size={15} />
                                    </button>
                                )}
                            </div>
                            <div className="grid grid-cols-2 gap-4 border-t border-gray-200 bg-white px-6 py-4 justify-end">
                                <FormInput
                                    label="Agent Name"
                                    value={agent.name}
                                    onChange={(e) => updateAgent(i, { ...agent, name: e.target.value })}
                                />
                                {(Object.keys(OPTIONS) as (keyof typeof OPTIONS)[]).map(key => (
                                    <div key={key} className="space-y-1.5">
                                        <label className="text-sm font-medium text-gray-700">{LABELS[key]}</label>
                                        <div className="flex flex-wrap gap-2">
                                            {OPTIONS[key].map(opt => (
                                                <SelectButton
                                                    key={opt}
                                                    label={opt}
                                                    active={agent.persona[key] === opt}
                                                    onClick={() => updateAgent(i, { ...agent, persona: { ...agent.persona, [key]: opt } })}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <LLMSetup config={agent} onChange={cfg => updateAgent(i, {
                                ...agent,
                                ...cfg,
                            })} />
                        </div>
                    ))}
                </>
            )}

            <div className="flex justify-end pt-2 space-x-2 border-t border-gray-200">
                <Button variant="outline" onClick={onBack}>
                    <span className="flex items-center gap-2">
                        <ChevronLeft size={16} />
                        Back
                    </span>
                </Button>

                <Button onClick={onSubmit} disabled={!isValid || running}>
                    <span className="flex items-center gap-2">
                        Start Simulation
                        <ChevronRight size={16} />
                    </span>
                </Button>
            </div>
        </div>
    );
}

export default UserAgentConfigCard;