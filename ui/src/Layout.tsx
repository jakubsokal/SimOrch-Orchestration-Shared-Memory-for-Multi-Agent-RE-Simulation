import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Play, List } from 'lucide-react';
import NavBar from './components/shared/Navbar';

const navItems = [
  { key: '/', label: 'Start Simulation', icon: <Play size={16} /> },
  { key: '/runs', label: 'View Runs', icon: <List size={16} /> },
];

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-50 overflow-hidden">
      <NavBar
        items={navItems}
        activePage={location.pathname}
        onNavigate={(path) => navigate(path)}
      />
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  );
}