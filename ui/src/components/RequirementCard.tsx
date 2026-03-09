import { type FC, useState } from 'react';
import { ChevronDown, FileText, User, Clock } from 'lucide-react';

interface RequirementCardProps {
    requirement: any;
}

const RequirementCard: FC<RequirementCardProps> = ({ requirement }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    { console.log("Rendering RequirementCard with requirement:", requirement) }
    const reqId = requirement.req_id;
    const type = requirement.requirement?.type || requirement.type || 'functional';
    const turn = requirement?.turn_id || 0;
    const evidence = requirement.requirement?.evidence_quote || requirement.evidence_quote || '';
    const createdBy = requirement.requirement?.createdBy || requirement.createdBy || 'Unknown';
    const timestamp = requirement.requirement?.timestamp || requirement.timestamp || '';
    const originalMessage = requirement.requirement?.description || requirement.description;
    const originalMessageId = requirement.requirement?.trace_message_id || requirement.trace_message_id || 'N/A';

    console.log("Rendering RequirementCard with data:", originalMessage, originalMessageId)
    const formattedTimestamp = timestamp ? new Date(timestamp).toLocaleString() : 'N/A';

    return (
        <div className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow">
            <div
                className="p-4 cursor-pointer flex items-start gap-3"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="shrink-0 w-10 h-10 bg-blue-50 rounded flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-0.5 rounded text-xs font-medium border border-gray-300 text-gray-700">Requirement ID: {reqId}</span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${type === 'functional'
                            ? 'bg-green-100 text-green-700 border border-green-300'
                            : 'bg-purple-100 text-purple-700 border border-purple-300'
                            }`}>
                            {type}
                        </span>
                        {turn > 0 && (
                            <span className="px-2 py-0.5 rounded text-xs font-medium border border-gray-300 text-gray-700">
                                Turn {turn}
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-gray-900">{originalMessage}</p>
                </div>
                <ChevronDown
                    className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''
                        }`}
                />
            </div>

            {isExpanded && (
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                                <User className="w-4 h-4" />
                                <span>Created By</span>
                            </div>
                            <p className="text-sm font-medium text-gray-900">{createdBy}</p>
                            <p className="text-xs text-blue-600">Stakeholder</p>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                                <Clock className="w-4 h-4" />
                                <span>Timestamp</span>
                            </div>
                            <p className="text-sm font-medium text-gray-900">{formattedTimestamp}</p>
                        </div>
                    </div>

                    {evidence && (
                        <div className="mb-4">
                            <p className="text-sm text-gray-500 mb-2">Evidence / Traceability</p>
                            <div className="bg-blue-50 border border-blue-200 rounded p-3">
                                <p className="text-sm italic text-blue-900">"{evidence}"</p>
                            </div>
                        </div>
                    )}

                    {originalMessage && (
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <FileText className="w-4 h-4 text-gray-500" />
                                <p className="text-xs font-bold text-gray-800">Original Message (ID: {originalMessageId})</p>
                            </div>
                            <div className="border border-gray-200 rounded bg-white p-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <User className="w-4 h-4 text-gray-400" />
                                    <span className="font-semibold text-gray-900">{createdBy}</span>
                                    <span className="text-xs text-blue-600">Stakeholder</span>
                                </div>
                                <p className="text-sm text-gray-900">{originalMessage}</p>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default RequirementCard;