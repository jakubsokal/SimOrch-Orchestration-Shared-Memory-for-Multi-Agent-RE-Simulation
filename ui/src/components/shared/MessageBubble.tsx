import { type FC } from 'react';
import Avatar from './Avatar';
import { AgentType } from '../../types/agentType';

interface MessageBubbleProps {
    type: 1 | 2;
    name: string;
    role?: number;
    message: string;
}


const MessageBubble: FC<MessageBubbleProps> = ({
    type,
    name,
    role,
    message
}) => {
    const isAgent = type === 1;
    const roleLabel =
        role === AgentType.REQUIREMENTS_ENGINEER ? 'Requirements Engineer'
            : role === AgentType.STAKEHOLDER ? 'Stakeholder'
                : undefined;

    return (

        <div className={`flex gap-3 ${isAgent ? '' : 'justify-end'}`}>
            {isAgent && (
                <Avatar type={1} size="md" />
            )}
            <div className={`flex flex-col ${isAgent ? 'items-start' : 'items-end'} max-w-2xl`}>
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-gray-900">{name}</span>
                    {role && <span className="text-xs text-gray-500">{roleLabel}</span>}
                </div>
                <div className={`rounded-lg px-4 py-3 ${isAgent
                    ? 'bg-white border border-gray-200'
                    : 'bg-blue-100 border border-blue-200'
                    }`}>
                    <p className="text-sm text-gray-900">{message}</p>
                </div>
            </div>
            {!isAgent && (
                <Avatar type={2} size="md" />
            )}
        </div>
    );
};

export default MessageBubble;