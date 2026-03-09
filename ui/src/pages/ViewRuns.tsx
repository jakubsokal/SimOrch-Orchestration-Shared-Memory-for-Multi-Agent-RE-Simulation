import { useState, useEffect } from 'react';
import { Search, FileText, AlertCircle, MessageSquare, Info, AlertTriangle, XCircle } from 'lucide-react';
import RunCard from '../components/RunCard';
import Input from '../components/shared/Input';
import TabButton from '../components/shared/TabButton';
import MessageBubble from '../components/shared/MessageBubble';
import { getAllRuns, getRunById } from '../api/run';
import RequirementCard from '../components/RequirementCard';
import IssueCard from '../components/IssueCard';
import Loading from '../components/shared/Loading';
import ConfigCard from '../components/ConfigCard';

interface RunSummary {
  id: string;
  date: string;
  time: string;
  timeElapsed: string;
  totalTurns: number;
}

interface RunDetails {
  id: string;
  totalTurns: number;
  requirements: any[];
  issues: any[];
  messages: any[];
  clarifications: any[];
  config: any;
}

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunDetails | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [isLoadingRuns, setIsLoadingRuns] = useState(true);
  const [isLoadingRun, setIsLoadingRun] = useState(false);
  const [activeTab, setActiveTab] = useState('transcript');
  const [searchQuery, setSearchQuery] = useState('');

   useEffect(() => {
    const fetchRuns = async () => {
      try {
        setIsLoadingRuns(true);
        const data = await getAllRuns() as any[];
        
        const transformedRuns = data.map((run: any) => ({
          id: run.id,
          date: run.createdOn ? new Date(run.createdOn).toLocaleDateString() : 'N/A',
          time: run.createdOn ? new Date(run.createdOn).toLocaleTimeString() : 'N/A',
          timeElapsed: run.timeElapsed || 'N/A',
          totalTurns: run.turnNumber || 0,
          requirements: [],
          issues: [],
          messages: [],
          clarifications: [],
          config: {}
        }));
        
        setRuns(transformedRuns);
      } catch (error) {
        console.error('Failed to fetch runs:', error);
      } finally {
        setIsLoadingRuns(false);
      }
    };

    fetchRuns();
  }, []);

  const handleSelectRun = (runId: string) => {
    setSelectedRunId(runId);
    setActiveTab('transcript');

    const fetchRunDetails = async () => {
      try {
        setIsLoadingRun(true);
        const data = await getRunById(runId) as any;
        setSelectedRun({
          id: runId,
          totalTurns: runs.find(r => r.id === runId)?.totalTurns || 0,
          requirements: data.requirements || [],
          issues: data.issues || [],
          messages: data.transcript || [],
          clarifications: data.clarifications || [],
          config: data.config || {}
        });
      } catch (error) {
        console.error(`Failed to fetch run details run ID: ${runId}:`, error);
      } finally {
        setIsLoadingRun(false);
      }
    }
    fetchRunDetails();
  };

  const filteredRuns = runs.filter(run => 
    run.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-screen w-screen flex bg-gray-50 overflow-hidden ">
      <div className="w-72 border-r border-gray-200 bg-white flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-lg mb-3">Simulation Runs</h2>
          <Input 
            type="text" 
            placeholder="Search runs..."
            icon={<Search size={16} />}
            fullWidth
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {isLoadingRuns ? (
            <div className="text-center text-sm text-gray-600 py-8">
              <Loading size={48} thickness={4} label="Loading runs..." direction="column" gap={2} />
            </div>
          ) : filteredRuns.length > 0 ? (
            filteredRuns.map((run) => (
              <RunCard
                key={run.id}
                runId={run.id}
                date={run.date}
                createdOn={run.time}
                timeElapsed={run.timeElapsed}
                turns={run.totalTurns}
                isSelected={selectedRunId === run.id}
                onClick={() => handleSelectRun(run.id)}
              />
            ))
          ) : (
            <div className="text-center text-sm text-gray-600 py-8">
              No runs found
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          {runs.length} runs displayed
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Requirements Engineering Simulation Dashboard</h3>
              {selectedRun && (
                <p className="text-sm text-gray-600 mt-1">
                  Viewing: <span className="font-medium">{selectedRun.id}</span>
                </p>
              )}
            </div>

            {selectedRun && (
              <div className="flex gap-6 text-sm">
                <div className="text-right">
                  <div className="text-gray-600">Total Turns</div>
                  <div className="text-lg font-semibold">{selectedRun.totalTurns}</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-600">Requirements</div>
                  <div className="text-lg font-semibold">{selectedRun.requirements.length}</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-600">Issues</div>
                  <div className="text-lg font-semibold">{selectedRun.issues.length}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          {isLoadingRun ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loading size={48} thickness={4} label="Loading simulation details..." direction="column" gap={2} />
              </div>
            </div>
          ) : selectedRun ? (
            <div className="h-full flex flex-col">
              <div className="border-b border-gray-200 bg-white">
                <div className="flex px-6">
                  <div className="flex p-1 rounded-[10px] bg-gray-100">
                  <TabButton
                    icon={<MessageSquare size={16} />}
                    label="Transcript"
                    count={selectedRun.messages.length}
                    isSelected={activeTab === 'transcript'}
                    onClick={() => setActiveTab('transcript')}
                  />
                  <TabButton
                    icon={<FileText size={16} />}
                    label="Requirements"
                    count={selectedRun.requirements.length}
                    isSelected={activeTab === 'requirements'}
                    onClick={() => setActiveTab('requirements')}
                  />
                  <TabButton
                    icon={<AlertCircle size={16} />}
                    label="Issues"
                    count={selectedRun.issues.length}
                    isSelected={activeTab === 'issues'}
                    onClick={() => setActiveTab('issues')}
                  />
                  <TabButton
                    icon={<Info size={16} />}
                    label="Config"
                    count={1}
                    isSelected={activeTab === 'config'}
                    onClick={() => setActiveTab('config')}
                  />
                  </div>
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto bg-gray-50 pb-24">
                {activeTab === 'transcript' && (
                  <div className="p-6 space-y-6 max-w-5xl mx-auto">
                    {selectedRun.messages.length > 0 ? (
                      selectedRun.messages.map((message) => (
                        <div key={message.id}>
                          {message.turn && (
                            <div className="text-sm font-semibold text-gray-700 mb-4">
                              Turn {message.turn}
                            </div>
                          )}
                          <MessageBubble
                            type={message.role}
                            name={message.agent}
                            role={message.role}
                            message={message.message}
                          />
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-600 py-12">
                        No messages in this simulation
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'requirements' && (
                  <div className="p-6">
                    <div className="max-w-5xl mx-auto">
                      <div className="mb-4">
                        <h2 className="text-lg font-semibold text-gray-900">Extracted Requirements</h2>
                        <p className="text-sm text-blue-600">
                          {selectedRun.requirements.length} requirements identified during the simulation
                        </p>
                      </div>
                      {selectedRun.requirements.length > 0 ? (
                        <div className="space-y-4">
                          {selectedRun.requirements.map((req) => (
                            <>{console.log(req)}
                            <RequirementCard key={req.id} requirement={req} />
                            </>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center text-gray-600 py-12 bg-white rounded-lg border border-gray-200">
                          No requirements generated yet
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === 'issues' && (
                  <div className="p-6">
                    <div className="max-w-5xl mx-auto">
                      <div className="mb-4">
                        <h2 className="text-lg font-semibold text-gray-900">Detected Issues</h2>
                        <p className="text-sm text-blue-600">
                          {selectedRun.issues.length} issues identified during requirements elicitation
                        </p>
                      </div>

                      <div className="grid grid-cols-4 gap-4 mb-6">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 text-blue-700 mb-2">
                            <Info size={16} />
                            <span className="text-xs font-medium uppercase">Low</span>
                          </div>
                          <div className="text-2xl font-bold text-blue-900">
                            {selectedRun.issues.filter(i => (i.issue?.severity || i.severity) === 'low').length}
                          </div>
                        </div>

                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 text-yellow-700 mb-2">
                            <AlertCircle size={16} />
                            <span className="text-xs font-medium uppercase">Medium</span>
                          </div>
                          <div className="text-2xl font-bold text-yellow-900">
                            {selectedRun.issues.filter(i => (i.issue?.severity || i.severity) === 'medium').length}
                          </div>
                        </div>

                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 text-orange-700 mb-2">
                            <AlertTriangle size={16} />
                            <span className="text-xs font-medium uppercase">High</span>
                          </div>
                          <div className="text-2xl font-bold text-orange-900">
                            {selectedRun.issues.filter(i => (i.issue?.severity || i.severity) === 'high').length}
                          </div>
                        </div>

                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 text-red-700 mb-2">
                            <XCircle size={16} />
                            <span className="text-xs font-medium uppercase">Critical</span>
                          </div>
                          <div className="text-2xl font-bold text-red-900">
                            {selectedRun.issues.filter(i => (i.issue?.severity || i.severity) === 'critical').length}
                          </div>
                        </div>
                      </div>

                      {selectedRun.issues.length > 0 ? (
                        <div className="space-y-4">
                          {selectedRun.issues.map((issue) => (
                            <IssueCard key={issue.issue_id || issue.id} issue={issue} />
                          ))}
                        </div>
                      ) : (
                        <div className="text-center text-gray-600 py-12 bg-white rounded-lg border border-gray-200">
                          No issues identified yet
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === 'config' && (
                  <div className="p-6">
                    <div className="max-w-5xl mx-auto">
                      <div className="mb-4">
                        <h2 className="text-lg font-semibold text-gray-900">Scenario Configuration</h2>
                        <p className="text-sm text-blue-600">Configuration used for this run</p>
                      </div>
                      <ConfigCard config={selectedRun.config} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="p-8 text-center max-w-md">
                <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">No Simulation Selected</h3>
                <p className="text-sm text-gray-600">
                  Select a simulation run from the sidebar to view its details
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}