import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import SimulationRun from './pages/SimulationRun';
import ViewRuns from './pages/ViewRuns';
import ViewEvalResults from './pages/ViewEvalResults';
import { SimulationProvider } from './components/SimulationContext';

export default function Router() {
  return (
    <SimulationProvider>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<SimulationRun />} />
          <Route path="/runs" element={<ViewRuns />} />
          <Route path="/evals" element={<ViewEvalResults />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </SimulationProvider>
  );
}