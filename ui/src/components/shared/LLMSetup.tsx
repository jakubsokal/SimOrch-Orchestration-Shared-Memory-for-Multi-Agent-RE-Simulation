import { type FC } from 'react';
import FormInput from './FormInput';
import SelectButton from './SelectButton';
import FormTextarea from './FormTextarea';

const PROVIDERS = ['ollama', 'openai' /*, 'groq', 'gemini'*/] as const;
export type Provider = typeof PROVIDERS[number];

export const MODELS_BY_PROVIDER: Record<Provider, string[]> = {
    ollama: ['llama2', 'mistral', 'gemma2', 'phi3'],
    openai: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o-mini']/*,
    groq: ['llama3-70b', 'mixtral-8x7b', 'gemma-7b'],
    gemini: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],*/
};

export interface ModelConfig {
    provider: Provider;
    model: string;
    params: {
        temperature: number;
        top_p: number;
        max_tokens: number;
    }
    api_key?: string;
    context_prompt: string;
}

export const DEFAULT_MODEL_CONFIG: ModelConfig = {
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

interface LLMSetupProps {
    config: ModelConfig;
    onChange: (config: ModelConfig) => void;
}

const LLMSetup: FC<LLMSetupProps> = ({ config, onChange }) => {
    return (
        <div className="border-t border-gray-100 pt-4 space-y-4">
            <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Model</h5>
            <FormTextarea
                label="Context Prompt"
                placeholder="Describe the role of this agent in the simulation, any specific instructions for its behavior, and any other relevant context that should be included in every prompt sent to the LLM."
                value={config.context_prompt}
                onChange={e => onChange({ ...config, context_prompt: e.target.value })}
                fullWidth
            />
            <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700">Provider</label>
                <div className="flex flex-wrap gap-2">
                    {PROVIDERS.map(p => (
                        <SelectButton
                            key={p}
                            label={p}
                            active={config.provider === p}
                            onClick={() => onChange({ ...config, provider: p, model: MODELS_BY_PROVIDER[p][0] })}
                        />
                    ))}
                </div>
            </div>

            <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700">Model</label>
                <div className="flex flex-wrap gap-2">
                    {MODELS_BY_PROVIDER[config.provider].map(m => (
                        <SelectButton
                            key={m}
                            label={m}
                            active={config.model === m}
                            onClick={() => onChange({ ...config, model: m })}
                        />
                    ))}
                    <FormInput
                        label="API KEY"
                        type="password"
                        placeholder='API Key'
                        value={config.api_key || ''}
                        onChange={e => onChange({ ...config, api_key: e.target.value })}
                        fullWidth
                    />
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                <FormInput
                    label="Temperature"
                    type="number"
                    value={config.params.temperature}
                    onChange={e => onChange({ ...config, params: { ...config.params, temperature: Number(e.target.value) } })}
                    min={0} max={2} step={0.1} fullWidth
                />
                <FormInput
                    label="Top-P"
                    type="number"
                    value={config.params.top_p}
                    onChange={e => onChange({ ...config, params: { ...config.params, top_p: Number(e.target.value) } })}
                    min={0} max={1} step={0.05} fullWidth
                />
                <FormInput
                    label="Max Tokens"
                    type="number"
                    value={config.params.max_tokens === 0 ? '' : config.params.max_tokens}
                    onChange={e => onChange({ ...config, params: { ...config.params, max_tokens: Number(e.target.value) } })}
                    min={64} max={4096} step={64} fullWidth
                />
            </div>
        </div>
    );
};

export default LLMSetup;