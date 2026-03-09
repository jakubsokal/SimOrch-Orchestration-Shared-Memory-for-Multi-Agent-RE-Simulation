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

const predefinedScenarios: PredefinedScenario[] = [
  {
    scenario: {
      id: 'scenario_001',
      seed: 42,
      scenario_name: 'Meeting Room Booking Elicitation',
      description:
        'A dialogue between a Requirements Engineer and a User(employee) and a User(office manager) to elicit requirements for a corporate room booking system.',
      domain: 'Corporate',
      system_type: 'Booking System',
      max_turns: 10,
      conversation_type: 'dynamic',
    },
    scenarioTruths: [
      { id: 'R1', type: 'FR', statement: 'Users must be able to search for available meeting rooms by date, time, and capacity.' },
      { id: 'R2', type: 'FR', statement: 'Users must be able to book, modify, and cancel room reservations.' },
      { id: 'R3', type: 'FR', statement: 'The system must send booking confirmation and reminder notifications to the user.' },
      { id: 'R4', type: 'FR', statement: 'The office manager must be able to view all bookings across all rooms.' },
      { id: 'R5', type: 'FR', statement: 'The system must prevent double booking of the same room at the same time.' },
      { id: 'R6', type: 'NFR', statement: 'The system must be accessible via web and mobile.' },
    ],
    re_agents: [
      {
        name: 'Requirement Engineer',
        role: 1,
        persona: {
          experience_level: 'senior',
          questioning_strategy: 'structured',
          probing_intensity: 'medium',
          requirement_focus: 'functional',
          tone: 'formal',
          output_prefixes: ['FR', 'NFR', 'CON'],
        },
        provider: 'openai',
        model: 'gpt-4o-mini',
        params: {
          temperature: 0,
          top_p: 1,
          max_tokens: 512
        },
        context_prompt:
          'You are an experienced Requirements Engineer conducting a structured elicitation \n  interview for a corporate meeting room booking system. You are interviewing multiple \n  stakeholders who may have different and sometimes conflicting needs.\n\n  Your behaviour:\n  - Ask one focused question at a time\n  - Listen carefully and probe ambiguities before moving on\n  - Never lead the stakeholder toward a specific answer\n  - Prioritise unresolved requirements and open issues flagged by the analyst\n  - Remain neutral when stakeholders disagree \u2014 note the conflict, do not resolve it yourself\n  - Use plain, jargon-free language appropriate for non-technical stakeholders\n  - Be professional but conversational in tone',
      },
    ],
    user_agents: [
      {
        name: 'Jamie',
        role: 2,
        persona: {
          communication_style: 'concise',
          domain_knowledge_level: 'high',
          clarity_level: 'clear',
          revelation_strategy: 'proactive',
          revelation_rate: 'medium',
        },
        provider: 'openai',
        model: 'gpt-4o-mini',
        params: {
          temperature: 0,
          top_p: 1,
          max_tokens: 512
        },
        context_prompt:
          "You are Jamie, an office employee at a mid-sized company. You book meeting rooms \n    several times a week for team meetings and client calls.\n\n    Your frustrations:\n    - The current process is email-based and slow, often taking hours to get confirmation\n    - Rooms are frequently already taken when you arrive despite no visible booking\n    - You have no way to see room availability in advance\n\n    Your needs:\n    - A quick, self-service way to check availability and book instantly\n    - Notifications when your booking is confirmed or if something changes\n    - Ability to book from your phone\n\n    Your personality:\n    - Practical and direct, you want simple solutions\n    - Not very technical, avoid system or developer jargon\n    - Will express frustration if asked about the current process",
      },
      {
        name: 'Sarah',
        role: 2,
        persona: {
          communication_style: 'cooperative',
          domain_knowledge_level: 'high',
          clarity_level: 'clear',
          revelation_strategy: 'proactive',
          revelation_rate: 'slow',
        },
        provider: 'openai',
        model: 'gpt-4o-mini',
        params: {
          temperature: 0,
          top_p: 1,
          max_tokens: 512
        },
        context_prompt:
          "You are Sarah, the office manager at a mid-sized company. You are responsible \n    for managing all meeting room bookings and resolving scheduling conflicts.\n\n    Your frustrations:\n    - Employees book large rooms for small meetings, wasting space\n    - No-shows are common \u2014 rooms get booked and never used\n    - You have no visibility into room utilisation patterns\n    - Last-minute cancellations leave rooms empty with no way to reassign them\n\n    Your needs:\n    - A dashboard to see all bookings across all rooms at a glance\n    - Ability to override or cancel any booking if there is a priority conflict\n    - Automatic release of rooms if a meeting hasnt started within 10 minutes\n    - Reports on room utilisation to justify space planning decisions\n\n    Your personality:\n    - Organised and assertive, you take room management seriously\n    - You are skeptical of systems that give employees too much freedom without oversight\n    - You will push back if you feel control is being taken away from you\n    - Mildly territorial about room management being your responsibility",
      },
    ],
  },
];

interface ScenarioCardProps {
  selection: ScenarioSelection;
  onSelect: (selection: ScenarioSelection) => void;
  onNext: () => void;
}

const ScenarioCard: FC<ScenarioCardProps> = ({ selection, onSelect, onNext }) => {
  const isCustom = selection.mode === 'custom';
  const customScenario = isCustom ? selection.scenario : DEFAULT_CUSTOM_SCENARIO;

  const isValid =
    selection.mode === 'predefined' ||
    (isCustom &&
      customScenario.scenario.scenario_name.trim() !== '' &&
      customScenario.scenario.description.trim() !== '' &&
      customScenario.scenario.conversation_type !== '');

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
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-700">Conversation Type</label>
              <select
                value={customScenario.scenario.conversation_type}
                onChange={(e) => updateCustomField('conversation_type', e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="">Select a type...</option>
                <option value="one_by_one">One by One</option>
                <option value="dynamic">Dynamic</option>
              </select>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end pt-2">
        <Button onClick={onNext} disabled={!isValid}>
          <span className="flex items-center gap-2">
            Continue
            <ChevronRight size={16} />
          </span>
        </Button>
      </div>
    </div>
  );
};

export default ScenarioCard;