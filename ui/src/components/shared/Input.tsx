import React, { type FC, type InputHTMLAttributes } from 'react';
import { Search } from 'lucide-react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    icon?: React.ReactNode;
    fullWidth?: boolean;
}

const Input: FC<InputProps> = ({
    fullWidth = false,
    className = '',
    ...props
}) => {
    return (
        <div className={`relative ${fullWidth ? 'w-full' : ''}`}>
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                <Search size={16} />
            </div>

            <input
                className={`border border-gray-300 rounded-lg px-3 py-2 pl-10
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                    text-sm placeholder-gray-400 ${fullWidth ? 'w-full' : ''} ${className}`}
                {...props}
            />
        </div>
    );
};

export default Input;