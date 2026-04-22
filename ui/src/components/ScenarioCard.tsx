import { type FC } from 'react';
import { ChevronRight } from 'lucide-react';
import FormInput from './shared/FormInput';
import FormTextarea from './shared/FormTextarea';
import Button from './shared/Button';
import type { UserAgentConfig } from './UserAgentConfigCard';
import type { REAgentConfig } from './ReAgentConfigCard';
import type { Requirement } from './ScenarioTruthCard';

export interface PredefinedScenario {
  scenario: {
    id: string;
    seed: number;
    scenario_name: string;
    description: string;
    domain: string;
    system_type: string;
    max_turns: number;
    conversation_type: string;
  };
  scenarioTruths: Requirement[];
  re_agents: REAgentConfig[];
  user_agents: UserAgentConfig[];
}

export interface CustomScenarioData {
  scenario: {
    id: string;
    scenario_name: string;
    seed: number;
    description: string;
    domain: string;
    system_type: string;
    max_turns: number;
    conversation_type: string;
  };
}

export type ScenarioSelection =
  | { mode: 'none' }
  | { mode: 'predefined'; scenario: PredefinedScenario }
  | { mode: 'custom'; scenario: CustomScenarioData };

export const DEFAULT_CUSTOM_SCENARIO: CustomScenarioData = {
  scenario: {
    id: '',
    scenario_name: '',
    seed: 0,
    description: '',
    domain: '',
    system_type: '',
    max_turns: 0,
    conversation_type: '',
  },
};

interface ScenarioCardProps {
  selection: ScenarioSelection;
  predefinedScenarios: PredefinedScenario[];
  onSelect: (selection: ScenarioSelection) => void;
  onNext: () => void;
}

const ScenarioCard: FC<ScenarioCardProps> = ({ selection, predefinedScenarios, onSelect, onNext }) => {
  const isCustom = selection.mode === 'custom';
  const customScenario = isCustom ? selection.scenario : DEFAULT_CUSTOM_SCENARIO;

  const isValid =
    selection.mode === 'predefined' ||
    (isCustom &&
      customScenario.scenario.scenario_name.trim() !== '' &&
      customScenario.scenario.description.trim() !== '' && 
      customScenario.scenario.domain.trim() !== '' &&
      customScenario.scenario.system_type.trim() !== '' &&
      customScenario.scenario.max_turns > 0);

  const updateCustomField = (field: string, value: string | number) => {
    if (selection.mode !== 'custom') return;
    onSelect({
      mode: 'custom',
      scenario: {
        ...selection.scenario,
        scenario: { ...selection.scenario.scenario, [field]: value },
      },
    });
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6 pb-24">
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Predefined Scenarios</h4>
        {predefinedScenarios.length === 0 ? (
          <div className="text-sm text-gray-500">No predefined scenarios found.</div>
        ) : (
          <div className="space-y-3">
            {predefinedScenarios.map((s) => {
              const isSelected =
                selection.mode === 'predefined' && selection.scenario.scenario.id === s.scenario.id;

              return (
                <label
                  key={s.scenario.id}
                  className={`
                    flex items-start gap-3 p-4 rounded-lg border cursor-pointer transition-colors
                    ${isSelected ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'}
                  `}
                  onClick={() => onSelect({ mode: 'predefined', scenario: s })}
                >
                  <input
                    type="radio"
                    name="scenario"
                    value={s.scenario.id}
                    checked={isSelected}
                    onChange={() => onSelect({ mode: 'predefined', scenario: s })}
                    className="mt-0.5 accent-blue-600"
                  />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{s.scenario.scenario_name}</div>
                    <div className="text-sm text-gray-500 mt-0.5">{s.scenario.description}</div>
                  </div>
                </label>
              );
            })}
          </div>
        )}
      </div>

      <label
        className={`
          flex items-start gap-3 p-4 rounded-lg border cursor-pointer transition-colors
          ${isCustom ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'}
        `}
        onClick={() => onSelect({ mode: 'custom', scenario: DEFAULT_CUSTOM_SCENARIO })}
      >
        <input
          type="radio"
          name="scenario"
          value="custom"
          checked={isCustom}
          onChange={() => onSelect({ mode: 'custom', scenario: DEFAULT_CUSTOM_SCENARIO })}
          className="mt-0.5 accent-blue-600"
        />
        <div>
          <div className="text-sm font-medium text-gray-900">Custom Scenario</div>
          <div className="text-sm text-gray-500 mt-0.5">Define your own simulation parameters</div>
        </div>
      </label>

      {isCustom && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h4 className="text-sm font-semibold text-gray-900">Custom Scenario Details</h4>
          <p className="text-sm text-blue-600">Fill in the details for your custom simulation</p>

          <div className="grid grid-cols-2 gap-4">
            <FormInput
              label="Scenario Name"
              placeholder="e.g. Hospital Patient Portal"
              value={customScenario.scenario.scenario_name}
              onChange={(e) => updateCustomField('scenario_name', e.target.value)}
              fullWidth
            />
            <FormInput
              label="Domain"
              placeholder="e.g. Healthcare"
              value={customScenario.scenario.domain}
              onChange={(e) => updateCustomField('domain', e.target.value)}
              fullWidth
            />
          </div>

          <FormTextarea
            label="Description"
            placeholder="Describe the simulation scenario..."
            value={customScenario.scenario.description}
            onChange={(e) => updateCustomField('description', e.target.value)}
            fullWidth
          />

          <div className="grid grid-cols-2 gap-4">
            <FormInput
              label="System Type"
              placeholder="e.g. Web Application"
              value={customScenario.scenario.system_type}
              onChange={(e) => updateCustomField('system_type', e.target.value)}
              fullWidth
            />
            <FormInput
              label="Max Turns"
              type="number"
              min={1}
              placeholder="6"
              max={100}
              value={
                customScenario.scenario.max_turns === 0
                  ? ''
                  : String(customScenario.scenario.max_turns > 100 ? 100 : customScenario.scenario.max_turns)
              }
              onChange={(e) => updateCustomField('max_turns', Number(e.target.value))}
              fullWidth
            />
            <FormInput
              label="Random Seed"
              type="number"
              value={customScenario.scenario.seed === 0 ? '' : customScenario.scenario.seed}
              onChange={(e) => updateCustomField('seed', Number(e.target.value))}
              placeholder="42"
              fullWidth
            />
          </div>
        </div>
      )}

      <div className="flex justify-end pt-2">
        <Button onClick={onNext} disabled={!isValid}>
          <span className="flex items-center gap-2 cursor-pointer">
            Continue
            <ChevronRight size={16} />
          </span>
        </Button>
      </div>
    </div>
  );
};

export default ScenarioCard;