import { type FC, type ReactNode } from 'react';

interface TabButtonProps {
    icon: ReactNode;
    label: string;
    count: number;
    isSelected: boolean;
    onClick: () => void;
}

const TabButton: FC<TabButtonProps> = ({ icon, label, count, isSelected, onClick }) => {
    return (
        <button
            onClick={onClick}
            className={`
                flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors
                ${isSelected
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }
            `}
            style={{ textDecoration: 'none', outline: 'none' }}
        >
            {icon}
            <span className="no-underline">{label}</span>
            <span className={`
                ml-1 px-2 py-0.5 rounded-full text-xs font-semibold
                ${isSelected
                    ? 'bg-gray-100 text-gray-700'
                    : 'bg-gray-200 text-gray-600'
                }
            `}>
                {count}
            </span>
        </button>
    );
};

export default TabButton;