import { type FC } from 'react';
import { Calendar, MessageSquare, Timer } from 'lucide-react';
import { Card, CardBody } from './shared/Card';
import Badge from './shared/Badge';

interface RunCardProps {
    runId: string;
    date: string;
    createdOn: string;
    timeElapsed: string;
    turns: number;
    isSelected?: boolean;
    onClick: () => void;
}

const RunCard: FC<RunCardProps> = ({
    runId,
    date,
    createdOn,
    timeElapsed,
    turns,
    isSelected = false,
    onClick
}) => {
    return (
        <Card
            className={`cursor-pointer transition-all ${isSelected
                ? 'border-2 border-blue-500 bg-blue-50 shadow-md'
                : 'border border-gray-200 hover:border-gray-300 hover:shadow-sm'
                }`}
            onClick={onClick}
        >
            <CardBody>
                <div className="flex items-start justify-between mb-2">
                    <h3 className={`font-semibold ${isSelected ? 'text-blue-900' : 'text-gray-900'}`}>
                        {runId}
                    </h3>
                    {(isSelected) && (
                        <Badge variant={isSelected ? "info" : "success"}>
                            Active
                        </Badge>
                    )}
                </div>
                <div className={`flex items-center gap-2 text-xs mb-1 ${isSelected ? 'text-blue-700' : 'text-gray-600'
                    }`}>
                    <Calendar size={12} />
                    <span>{date} • {createdOn}</span>
                </div>
                <div className={`flex items-center gap-2 text-xs ${isSelected ? 'text-blue-700' : 'text-gray-600'
                    }`}>
                    <Timer size={12} />
                    <span>{timeElapsed}</span>
                </div>
                <div className={`flex items-center gap-2 text-xs ${isSelected ? 'text-blue-700' : 'text-gray-600'
                    }`}>
                    <MessageSquare size={12} />
                    <span>{turns} turns</span>
                </div>
            </CardBody>
        </Card>
    );
};

export default RunCard;