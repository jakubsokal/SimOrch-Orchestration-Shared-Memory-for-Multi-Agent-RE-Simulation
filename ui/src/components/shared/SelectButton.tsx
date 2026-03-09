import { type FC } from 'react';

interface SelectButtonProps {
  label: string;
  active: boolean;
  onClick: () => void;
}

const SelectButton: FC<SelectButtonProps> = ({ label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`
      px-3 py-1.5 rounded-md text-xs font-semibold border transition-colors
      ${active
        ? 'bg-blue-50 border-blue-300 text-blue-700'
        : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'}
    `}
  >
    {label}
  </button>
);

export default SelectButton;