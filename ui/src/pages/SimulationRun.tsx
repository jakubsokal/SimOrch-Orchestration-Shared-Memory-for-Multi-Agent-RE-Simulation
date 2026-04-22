import { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import Typography from '@mui/material/Typography';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';
import ScenarioCard from '../components/ScenarioCard';
import ScenarioTruthsCard, { type Requirement } from '../components/ScenarioTruthCard';
import REAgentConfigCard, { type REAgentConfig, DEFAULT_AGENT as DEFAULT_RE_AGENT } from '../components/ReAgentConfigCard';
import UserAgentConfigCard, { type UserAgentConfig, DEFAULT_AGENT as DEFAULT_USER_AGENT } from '../components/UserAgentConfigCard';
import { type PredefinedScenario, type ScenarioSelection } from '../components/ScenarioCard';
import { initiateSimulation } from '../api/simulation';
import { getScenarios } from '../api/run';
import PopUp from '../components/shared/PopUp';
import { useSimulation } from '../components/SimulationContext';

const STEPS = [
  { id: 'scenario-select', label: 'Scenario Select' },
  { id: 'scenario-truths', label: 'Scenario Truths' },
  { id: 're-agents', label: 'RE Agent Config' },
  { id: 'user-agents', label: 'User Agent Config' },
];

export default function SimulationRun() {
  const { simulationRunning, setSimulationRunning, popUps, addPopUp, removePopUp } = useSimulation();
  const [selection, setSelection] = useState<ScenarioSelection>({ mode: 'none' });
  const [predefinedScenarios, setPredefinedScenarios] = useState<PredefinedScenario[]>([]);
  const [scenarioTruths, setScenarioTruths] = useState<Requirement[]>([{ id: 'R1', type: 'FR', statement: '' }]);
  const [reAgents, setReAgents] = useState<REAgentConfig[]>([{ ...DEFAULT_RE_AGENT }]);
  const [userAgents, setUserAgents] = useState<UserAgentConfig[]>([{ ...DEFAULT_USER_AGENT }]);
  const [currentStep, setCurrentStep] = useState(0);

  const isPredefined = selection.mode === 'predefined';
  const isCustom = selection.mode === 'custom';

  useEffect(() => {
    let cancelled = false;

    const normalize = (scenario: any): PredefinedScenario => {
      const normalizedReAgents = (scenario?.re_agents ?? []).map((agent: any) => {
        const persona = agent?.persona ?? {};
        const outputPrefixes = persona.output_prefixes ?? agent?.output_prefixes ?? ['FR', 'NFR', 'CON'];

        return {
          ...agent,
          role: agent?.role ?? 1,
          persona: {
            ...persona,
            output_prefixes: outputPrefixes,
          },
        };
      });

      const normalizedUserAgents = (scenario?.user_agents ?? []).map((agent: any) => ({
        ...agent,
        role: agent?.role ?? 2,
      }));

      return {
        ...scenario,
        re_agents: normalizedReAgents,
        user_agents: normalizedUserAgents,
      } as PredefinedScenario;
    };

    (async () => {
      try {
        const data = await getScenarios();
        if (cancelled) return;

        const scenarios = Array.isArray(data) ? data.map(normalize) : [];
        setPredefinedScenarios(scenarios);
      } catch (error) {
        console.error('Failed to load scenarios:', error);
        if (!cancelled) setPredefinedScenarios([]);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  async function startSimulation() {
    try {
      const customConversationType = isCustom ? (userAgents.length > 1 ? 'dynamic' : 'one_to_one') : undefined;

      const config = isPredefined
        ? {
            scenario: selection.scenario.scenario,
            scenarioTruths: selection.scenario.scenarioTruths,
            re_agents: selection.scenario.re_agents,
            user_agents: selection.scenario.user_agents,
          }
        : {
            scenario: isCustom
              ? {
                  ...selection.scenario.scenario,
                  id: `scenario_${String(predefinedScenarios.length + 1).padStart(3, '0')}`,
                  conversation_type: customConversationType ?? selection.scenario.scenario.conversation_type,
                }
              : null,
            scenarioTruths,
            re_agents: reAgents,
            user_agents: userAgents,
          };

      console.log('Initiating simulation with config:', config);
      await initiateSimulation(config);
      setSimulationRunning(true);
      localStorage.setItem('simulationRunning', 'true');

      addPopUp({
        type: 'success',
        message: 'Simulation initiated successfully!',
      });
    } catch (error) {
      console.error('Error initiating simulation:', error);
      addPopUp({
        type: 'error',
        message: 'Failed to initiate simulation.',
        description: (error as any)?.response?.data?.detail || 'An unexpected error occurred.',
      });
    } finally {
      setSimulationRunning(false);
    }
  }

  useEffect(() => {
    if (!simulationRunning) return;

    const events = new EventSource('http://localhost:8000/initiate/stream');

    events.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.status === 'completed') {
        setSimulationRunning(false);
        localStorage.removeItem('simulationRunning');
        addPopUp({ type: 'success', message: 'Simulation completed!' });
        events.close();
      }

      if (data.status === 'failed') {
        setSimulationRunning(false);
        localStorage.removeItem('simulationRunning');
        addPopUp({ type: 'error', message: 'Simulation failed.', description: data.error });
        events.close();
      }
    };

    events.onerror = () => {
      setSimulationRunning(false);
      localStorage.removeItem('simulationRunning');
      addPopUp({ type: 'error', message: 'Lost connection to simulation.' });
      events.close();
    };

    return () => events.close();
  }, [simulationRunning]);

  return (
    <div className="h-screen w-screen flex bg-gray-50 overflow-hidden">
      <div className="w-72 border-r border-gray-200 bg-white flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-lg">New Simulation</h2>
          <p className="text-sm text-gray-500 mt-1">Configure and launch</p>
        </div>
        <div className="flex-1 p-4 space-y-2">
          {simulationRunning ? (
            <>
              <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 cursor-not-allowed">
                <Settings size={16} />
                <span className="text-sm font-medium">Setup</span>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-blue-50 border border-blue-200 cursor-default">
                <Settings size={16} className="text-blue-600" />
                <span className="text-sm font-medium text-blue-700">Setup</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b border-gray-200 bg-white px-6 py-4 space-y-3">
          <div>
            <h3 className="font-semibold">Start a New Simulation</h3>
            <p className="text-sm text-gray-600 mt-1">Choose a predefined scenario or create your own</p>
          </div>

          <Breadcrumbs aria-label="breadcrumb">
            {STEPS.map((step, index) => {
              const isActive = index === currentStep;
              const isVisited = index < currentStep;
              return isActive ? (
                <Typography key={step.id} sx={{ fontSize: 13, fontWeight: 600, color: 'text.primary' }}>
                  {step.label}
                </Typography>
              ) : (
                <Link
                  key={step.id}
                  underline={isVisited ? 'hover' : 'none'}
                  color={isVisited ? 'inherit' : 'text.disabled'}
                  sx={{ fontSize: 13, cursor: isVisited ? 'pointer' : 'default' }}
                  onClick={() => isVisited && setCurrentStep(index)}
                >
                  {step.label}
                </Link>
              );
            })}
          </Breadcrumbs>
        </div>

        <div className="flex-1 overflow-y-auto">
          {currentStep === 0 && (
            <ScenarioCard
              selection={selection}
              onSelect={setSelection}
              predefinedScenarios={predefinedScenarios}
              onNext={() => setCurrentStep(1)}
            />
          )}

          {currentStep === 1 && (
            <ScenarioTruthsCard
              predefined={isPredefined}
              scenarioTruths={isPredefined ? selection.scenario.scenarioTruths : scenarioTruths}
              onChange={setScenarioTruths}
              onNext={() => setCurrentStep(2)}
              onBack={() => setCurrentStep(0)}
            />
          )}

          {currentStep === 2 && (
            <REAgentConfigCard
              predefined={isPredefined}
              agents={isPredefined ? selection.scenario.re_agents : reAgents}
              onChange={setReAgents}
              onNext={() => setCurrentStep(3)}
              onBack={() => setCurrentStep(1)}
            />
          )}

          {currentStep === 3 && (
            <UserAgentConfigCard
              predefined={isPredefined}
              agents={isPredefined ? selection.scenario.user_agents : userAgents}
              onChange={setUserAgents}
              onSubmit={startSimulation}
              onBack={() => setCurrentStep(2)}
              running={simulationRunning}
            />
          )}
        </div>
      </div>

      <PopUp popUps={popUps} onClose={removePopUp} />
    </div>
  );
}