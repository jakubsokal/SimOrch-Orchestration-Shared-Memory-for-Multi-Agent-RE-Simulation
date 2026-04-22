import { type FC } from 'react';
import { Trash2, Plus, ChevronLeft } from 'lucide-react';
import FormInput from './shared/FormInput';
import Button from './shared/Button';
import { ChevronRight } from 'lucide-react';

export interface Requirement {
  id: string;
  type: 'FR' | 'NFR' | 'CON';
  statement: string;
}

interface ScenarioTruthsCardProps {
  predefined: boolean;
  scenarioTruths: Requirement[];
  onChange: (requirements: Requirement[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const REQ_TYPES: Requirement['type'][] = ['FR', 'NFR', 'CON'];

const ScenarioTruthsCard: FC<ScenarioTruthsCardProps> = ({
  predefined,
  scenarioTruths: requirements,
  onChange,
  onNext,
  onBack,
}) => {
  const update = (index: number, field: keyof Requirement, value: string) => {
    onChange(requirements.map((req, i) => i === index ? { ...req, [field]: value } : req));
  };

  const add = () => {
    onChange([...requirements, { id: `R${requirements.length + 1}`, type: 'FR', statement: '' }]);
  };

  const remove = (index: number) => {
    onChange(requirements.filter((_, i) => i !== index));
  };

  const isValid = requirements.length > 0 && requirements.every(req => req.statement.trim() !== '');

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6 pb-24">
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-1">Ground Truth Requirements</h4>
        <p className="text-sm text-gray-500">
          Define the full set of requirements. Visible to user agents and the evaluator - not the RE agent.
        </p>
      </div>

      <div className="space-y-3">
        {predefined ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-700">
              You are using a predefined scenario. The requirements defined here will be used in the simulation.
            </p>
          </div>
        ) : (
          <>
            {requirements.map((req, i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    Requirement {req.id}
                  </span>
                  <button
                    onClick={() => remove(i)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormInput
                    label="ID"
                    disabled
                    value={req.id}
                    fullWidth
                  />
                  <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <div className="flex gap-2">
                      {REQ_TYPES.map(t => (
                        <button
                          key={t}
                          onClick={() => update(i, 'type', t)}
                          className={`
                      px-3 py-1.5 rounded-md text-xs font-semibold border transition-colors
                      ${req.type === t
                              ? 'bg-blue-50 border-blue-300 text-blue-700'
                              : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'}
                    `}
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <FormInput
                  label="Statement"
                  placeholder="Describe the requirement..."
                  value={req.statement}
                  onChange={e => update(i, 'statement', e.target.value)}
                  fullWidth
                />
              </div>
            ))}

            <button
              onClick={add}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              <Plus size={16} />
              Add Requirement
            </button>
          </>
        )}
      </div>
      <div className="flex justify-end pt-2 space-x-2 border-t border-gray-200">
        <Button variant="outline" onClick={onBack}>
          <span className="flex items-center gap-2 cursor-pointer">
            <ChevronLeft size={16} />
            Back
          </span>
        </Button>

        <Button onClick={onNext} disabled={!isValid && !predefined}>
          <span className="flex items-center gap-2 cursor-pointer">
            Continue
            <ChevronRight size={16} />
          </span>
        </Button>
      </div>
    </div>
  );
};

export default ScenarioTruthsCard;