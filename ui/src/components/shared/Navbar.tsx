import { type FC, type ReactNode } from 'react';

interface NavItem {
  key: string;
  label: string;
  icon: ReactNode;
}

interface NavBarProps {
  items: NavItem[];
  activePage: string;
  onNavigate: (key: string) => void;
}

const NavBar: FC<NavBarProps> = ({ items, activePage, onNavigate }) => {
  return (
    <div className="border-b border-gray-200 bg-white px-6 py-2">
      <div className="flex p-1 rounded-[10px] bg-gray-100 w-fit">
        {items.map((item) => (
          <button
            key={item.key}
            onClick={() => onNavigate(item.key)}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors cursor-pointer
              ${activePage === item.key
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
              }
            `}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default NavBar;