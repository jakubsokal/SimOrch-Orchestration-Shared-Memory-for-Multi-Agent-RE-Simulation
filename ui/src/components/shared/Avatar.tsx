import { type FC } from 'react';
import { Bot, CircleUserRound } from 'lucide-react';
import { AgentType } from '../../types/agentType';

interface AvatarProps {
    type: AgentType;
    name?: string;
    role?: string;
    size?: 'sm' | 'md' | 'lg';
    className?: string;
    showName?: boolean;
}

const Avatar: FC<AvatarProps> = ({
    type,
    name,
    role,
    size = 'md',
    className = '',
    showName = false
}) => {
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-10 h-10',
        lg: 'w-12 h-12',
    };

    const iconSizes = {
        sm: 16,
        md: 20,
        lg: 24,
    };

    const bgColor = type === AgentType.REQUIREMENTS_ENGINEER ? 'bg-blue-100' : 'bg-purple-100';
    const iconColor = type === AgentType.REQUIREMENTS_ENGINEER ? 'text-blue-600' : 'text-purple-600';

    return (
        <div className={`flex items-start gap-3 ${className}`}>
            <div
                className={`${sizeClasses[size]} ${bgColor} rounded-full flex items-center justify-center ${iconColor} shrink-0`}
                title={name}
            >
                {type === AgentType.REQUIREMENTS_ENGINEER ? (
                    <Bot size={iconSizes[size]} />
                ) : (
                    <CircleUserRound size={iconSizes[size]} />
                )}
            </div>
            {showName && (name || role) && (
                <div className="flex flex-col">
                    {name && (
                        <span className="text-sm font-semibold text-gray-900">
                            {name}
                        </span>
                    )}
                    {role && (
                        <span className="text-xs text-gray-500">
                            {role}
                        </span>
                    )}
                </div>
            )}
        </div>
    );
};

export default Avatar;