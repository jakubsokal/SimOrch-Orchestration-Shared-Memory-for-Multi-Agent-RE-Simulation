import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { usePopUp } from '../hooks/usePopUp';

interface SimulationContextType {
  simulationRunning: boolean;
  setSimulationRunning: (running: boolean) => void;
  popUps: ReturnType<typeof usePopUp>['popUps'];
  addPopUp: ReturnType<typeof usePopUp>['addPopUp'];
  removePopUp: ReturnType<typeof usePopUp>['removePopUp'];
}

const SimulationContext = createContext<SimulationContextType | null>(null);

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [simulationRunning, setSimulationRunning] = useState(
    () => localStorage.getItem('simulationRunning') === 'true'
  );
  const { popUps, addPopUp, removePopUp } = usePopUp();

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
    <SimulationContext.Provider value={{ simulationRunning, setSimulationRunning, popUps, addPopUp, removePopUp }}>
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulation() {
  const context = useContext(SimulationContext);
  if (!context) throw new Error('useSimulation must be used within SimulationProvider');
  return context;
}