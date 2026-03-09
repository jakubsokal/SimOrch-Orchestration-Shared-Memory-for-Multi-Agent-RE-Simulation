import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import SimulationRun from './pages/SimulationRun';
import ViewRuns from './pages/ViewRuns';
import { SimulationProvider } from './components/SimulationContext';

export default function Router() {
  return (
    <SimulationProvider>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<SimulationRun />} />
          <Route path="/runs" element={<ViewRuns />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </SimulationProvider>
  );
}