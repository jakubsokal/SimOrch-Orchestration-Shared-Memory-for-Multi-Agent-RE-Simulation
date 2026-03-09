import { type FC } from 'react';
import { Bot, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react';
import FormInput from './shared/FormInput';
import Button from './shared/Button';
import LLMSetup, { type Provider } from './shared/LLMSetup';
import SelectButton from './shared/SelectButton';

export interface REAgentConfig {
  name: string;
  role?: number; // 1 for RE Agent, 2 for User Agent
  persona: {
    experience_level: string;
    questioning_strategy: string;
    probing_intensity: string;
    requirement_focus: string;
    tone: string;
    output_prefixes: string[];
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

interface REAgentConfigCardProps {
  predefined?: boolean;
  agents: REAgentConfig[];
  onChange: (agents: REAgentConfig[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const OPTIONS = {
  experience_level: ['junior', 'intermediate', 'senior'],
  questioning_strategy: ['structured', 'exploratory'],
  probing_intensity: ['low', 'medium', 'high'],
  requirement_focus: ['functional', 'balanced', 'quality_oriented'],
  tone: ['formal', 'neutral', 'friendly'],
  output_prefixes: ['FR', 'NFR', 'CON'],
};

const LABELS: Record<string, string> = {
  name: 'Agent Name',
  experience_level: 'Experience Level',
  questioning_strategy: 'Questioning Strategy',
  probing_intensity: 'Probing Intensity',
  requirement_focus: 'Requirement Focus',
  tone: 'Tone',
  output_prefixes: 'Output Prefixes',
  provider: 'Model Provider',
  model: 'Model',
  temperature: 'Temperature',
  top_p: 'Top-p',
  max_tokens: 'Max Tokens',
};

export const DEFAULT_AGENT: REAgentConfig = {
  name: '',
  role: 1,
  persona: {
    experience_level: '',
    questioning_strategy: '',
    probing_intensity: '',
    requirement_focus: '',
    tone: '',
    output_prefixes: ['FR', 'NFR', 'CON'],
  },
  provider: 'ollama',
  model: 'llama2',
  params: {
    temperature: 0.0,
    top_p: 1.0,
    max_tokens: 512
  },
  context_prompt: '',
  api_key: '',
};

const REAgentConfigCard: FC<REAgentConfigCardProps> = ({ predefined, agents, onChange, onNext, onBack }) => {
  const updateAgent = (index: number, updated: REAgentConfig) => {
    onChange(agents.map((a, i) => i === index ? updated : a));
  };

  const togglePrefix = (index: number, prefix: string) => {
    const agent = agents[index];
    const prefixes = agent.persona.output_prefixes.includes(prefix)
      ? agent.persona.output_prefixes.filter(p => p !== prefix)
      : [...agent.persona.output_prefixes, prefix];
    updateAgent(index, { ...agent, persona: { ...agent.persona, output_prefixes: prefixes } });
  };

  const addAgent = () => onChange([...agents, { ...DEFAULT_AGENT }]);

  const removeAgent = (index: number) => onChange(agents.filter((_, i) => i !== index));

  const isValid = agents.length > 0 &&
    agents.every(agent =>
      agent.name.trim() !== '' &&
      agent.persona.experience_level !== '' &&
      agent.persona.questioning_strategy !== '' &&
      agent.persona.probing_intensity !== '' &&
      agent.persona.requirement_focus !== '' &&
      agent.persona.tone !== '' &&
      agent.persona.output_prefixes.length > 0
    );

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6 pb-24">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-1">RE Agent Configuration</h4>
          <p className="text-sm text-gray-500">Configure how Requirements Engineer agents conduct elicitation.</p>
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
            <span className="text-xs text-gray-500 ml-1">RE Agents</span>
          </div>
        )}
      </div>

      {predefined ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-700">
            You are using a predefined scenario. The RE agent configuration has been set automatically.
          </p>
        </div>
      ) : (
        <>
          {agents.map((agent, i) => (
            <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-md bg-blue-50 flex items-center justify-center text-sm"><Bot /></div>
                  <span className="text-sm font-semibold text-gray-900">RE Agent {i + 1}</span>
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
                {(Object.keys(OPTIONS) as (keyof typeof OPTIONS)[])
                  .filter(key => key !== 'output_prefixes')
                  .map(key => (
                    <div key={key} className="space-y-1.5">
                      <label className="text-sm font-medium text-gray-700">{LABELS[key]}</label>
                      <div className="flex flex-wrap gap-2">
                        {OPTIONS[key].map(opt => (
                          <SelectButton
                            key={opt}
                            label={opt}
                            active={(agent[key as keyof REAgentConfig] as string) === opt}
                            onClick={() => updateAgent(i, { ...agent, [key]: opt })}
                          />
                        ))}
                      </div>
                    </div>
                  ))}

                <div className="col-span-2 space-y-1.5">
                  <label className="text-sm font-medium text-gray-700">{LABELS.output_prefixes}</label>
                  <div className="flex gap-2">
                    {OPTIONS.output_prefixes.map(prefix => (
                      <SelectButton
                        key={prefix}
                        label={prefix}
                        active={agent.persona.output_prefixes.includes(prefix)}
                        onClick={() => togglePrefix(i, prefix)}
                      />
                    ))}
                  </div>
                </div>
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

        <Button onClick={onNext} disabled={!predefined && !isValid}>
          <span className="flex items-center gap-2">
            Continue
            <ChevronRight size={16} />
          </span>
        </Button>
      </div>
    </div>
  );
};

export default REAgentConfigCard;