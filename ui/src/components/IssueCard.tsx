import { type FC, useState } from 'react';
import { ChevronRight, AlertCircle, AlertTriangle, Info, XCircle, User, Clock, Shield, FileText } from 'lucide-react';

interface IssueCardProps {
    issue: any;
}

const IssueCard: FC<IssueCardProps> = ({ issue }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const issueId = issue.id;
    const type = issue.issue?.type || issue.type || 'unknown';
    const severity = issue.issue?.severity || issue.severity || 'low';
    const originalMessage = issue.issue?.description || issue.description || '';
    const originalMessageId = issue.issue?.trace_message_id || issue.trace_message_id || 'N/A';
    const suggestedAction = issue.issue?.suggested_action || issue.suggested_action;
    const evidenceQuote = issue.issue?.evidence_quote || issue.evidence_quote || '';
    const affectsRequirements = issue.issue?.affects_requirements || issue.affects_requirements || [];
    const createdBy = issue.createdBy || 'Unknown';
    const timestamp = issue.timestamp || '';
    const turn = issue.turn_id || issue.turn || 0;

    const formattedTimestamp = timestamp ? new Date(timestamp).toLocaleString() : 'N/A';

    const severityConfig = {
        low: {
            bg: 'bg-blue-50',
            border: 'border-blue-200',
            icon: Info,
            iconColor: 'text-blue-600',
            badge: 'bg-blue-100 text-blue-700'
        },
        medium: {
            bg: 'bg-yellow-50',
            border: 'border-yellow-200',
            icon: AlertCircle,
            iconColor: 'text-yellow-600',
            badge: 'bg-yellow-100 text-yellow-700'
        },
        high: {
            bg: 'bg-orange-50',
            border: 'border-orange-200',
            icon: AlertTriangle,
            iconColor: 'text-orange-600',
            badge: 'bg-orange-100 text-orange-700'
        },
        critical: {
            bg: 'bg-red-50',
            border: 'border-red-200',
            icon: XCircle,
            iconColor: 'text-red-600',
            badge: 'bg-red-100 text-red-700'
        }
    };

    const config = severityConfig[severity as keyof typeof severityConfig] || severityConfig.low;
    const IconComponent = config.icon;

    return (
        <div className={`border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow`}>
            <div
                className="p-4 cursor-pointer flex items-start gap-3"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className={`shrink-0 w-10 h-10 rounded ${config.bg} flex items-center justify-center`}>
                    <IconComponent className={`w-6 h-6 ${config.iconColor}`} />
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                        {issueId > 0 && (
                            <span className="px-2 py-0.5 rounded text-xs font-medium border border-gray-300">
                                Issue ID: {issueId}
                            </span>
                        )}
                        <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${config.badge}`}>
                            {severity}
                        </span>
                        <span className={"px-2 py-0.5 rounded text-xs font-medium border border-gray-300"}>
                            {type}
                        </span>
                        {turn > 0 && (
                            <span className="px-2 py-0.5 rounded text-xs font-medium border border-gray-300">
                                Turn {turn}
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-gray-900 font-medium">{originalMessage}</p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400 shrink-0" />
            </div>

            {isExpanded && (
                <div className="border-t border-gray-200 p-4 bg-white">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                                <User className="w-4 h-4" />
                                <span>Created By</span>
                            </div>
                            <p className="text-sm font-medium text-gray-900">{createdBy}</p>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                                <Clock className="w-4 h-4" />
                                <span>Timestamp</span>
                            </div>
                            <p className="text-sm font-medium text-gray-900">{formattedTimestamp}</p>
                        </div>
                    </div>

                    {suggestedAction && (
                        <div className="mb-4">
                            <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                                <Shield className="w-4 h-4" />
                                <span>Suggested Action</span>
                            </div>
                            <div className="bg-blue-50 border border-blue-200 rounded p-3">
                                <p className="text-sm text-blue-900">{suggestedAction}</p>
                            </div>
                        </div>
                    )}

                    {evidenceQuote && (
                        <div className="mb-4">
                            <p className="text-sm text-gray-500 mb-2">Evidence / Traceability</p>
                            <div className="bg-blue-50 border border-blue-200 rounded p-3">
                                <p className="text-sm italic text-blue-900">"{evidenceQuote}"</p>
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

                    {affectsRequirements && affectsRequirements.length > 0 && (
                        <div>
                            <p className="text-sm text-gray-500 mb-2">Affects Requirements</p>
                            <div className="flex flex-wrap gap-2">
                                {affectsRequirements.map((reqId: string, index: number) => (
                                    <span
                                        key={`${String(reqId)}-${index}`}
                                        className="px-2 py-1 bg-gray-100 border border-gray-300 rounded text-xs font-medium text-gray-700"
                                    >
                                        {String(reqId)}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default IssueCard;