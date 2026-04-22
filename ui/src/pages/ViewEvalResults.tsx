import { useEffect, useMemo, useState } from 'react';
import { BarChart3, ChevronDown, FileJson, ListChecks } from 'lucide-react';
import Input from '../components/shared/Input';
import Loading from '../components/shared/Loading';
import TabButton from '../components/shared/TabButton';
import { Card, CardBody } from '../components/shared/Card';
import Badge from '../components/shared/Badge';
import { getEvalResultById, getEvalResults, type EvalResultSummary } from '../api/results';

type EvalResult = any;

type TabKey = 'overview' | 'runs' | 'raw';

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes)) return 'N/A';
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}

function statusVariant(status: unknown): 'success' | 'warning' | 'error' | 'info' | 'default' {
  const s = String(status ?? '').toLowerCase();
  if (s === 'completed' || s === 'success') return 'success';
  if (s === 'failed' || s === 'error') return 'error';
  if (s === 'running') return 'info';
  if (s === 'partial' || s === 'warning') return 'warning';
  return 'default';
}

function boolVariant(value: unknown): 'success' | 'error' {
  return value === true ? 'success' : 'error';
}

function reportGrade(score: number): string {
  if (!Number.isFinite(score)) return 'N/A';
  if (score >= 90) return 'Excellent';
  if (score >= 75) return 'Good';
  if (score >= 60) return 'Satisfactory';
  return 'Needs Improvement';
}

function fmtPct(value: unknown, digits = 2): string {
  return typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(digits)}%` : 'N/A';
}

function severityVariant(severity: unknown): 'error' | 'warning' | 'default' {
  const s = String(severity ?? '').toLowerCase();
  if (s === 'high') return 'error';
  if (s === 'medium') return 'warning';
  return 'default';
}

const CHECK_LABELS: Record<string, string> = {
  B1_all_agents_contributed: 'All agents contributed',
  B2_turn_alternation: 'Turn alternation',
  B3_no_consecutive_duplicates: 'No consecutive duplicates',
  B4_min_turns_reached: 'Minimum turns reached',
  B4_re_question_rate: 'RE question rate',
  B5_re_question_rate: 'RE question rate',
  B5_extraction_coverage: 'Extraction coverage',
  B6_extraction_coverage: 'Extraction coverage',
};

export default function ViewEvalResults() {
  const [results, setResults] = useState<EvalResultSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<EvalResult | null>(null);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [isLoadingResult, setIsLoadingResult] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [expandedRuns, setExpandedRuns] = useState<Record<string, boolean>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [expandedTraceRuns, setExpandedTraceRuns] = useState<Record<string, boolean>>({});
  const [expandedIssueRuns, setExpandedIssueRuns] = useState<Record<string, boolean>>({});
  const [expandedGtRuns, setExpandedGtRuns] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        setIsLoadingList(true);
        const data = await getEvalResults();
        if (cancelled) return;
        setResults(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error('Failed to fetch eval results:', e);
        if (!cancelled) setResults([]);
      } finally {
        if (!cancelled) setIsLoadingList(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredResults = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return results;
    return results.filter((r) => r.id.toLowerCase().includes(q));
  }, [results, searchQuery]);

  const selectResult = (id: string) => {
    setSelectedId(id);
    setActiveTab('overview');
    setExpandedRuns({});
    setExpandedSections({});
    setExpandedTraceRuns({});
    setExpandedIssueRuns({});
    setExpandedGtRuns({});

    (async () => {
      try {
        setIsLoadingResult(true);
        const data = await getEvalResultById(id);
        setSelected(data);
      } catch (e) {
        console.error(`Failed to fetch eval result ${id}:`, e);
        setSelected(null);
      } finally {
        setIsLoadingResult(false);
      }
    })();
  };

  const selectedMeta = useMemo(() => results.find((r) => r.id === selectedId) ?? null, [results, selectedId]);

  const feasibility = selected?.feasibility;
  const feasibilityScore = feasibility?.score_percent ?? feasibility?.score_pct;
  const completionRate = feasibility?.completion_rate_percent ?? feasibility?.completion_rate_pct;
  const grade = feasibility?.grade;
  const totalRuns = feasibility?.total_runs;
  const runDetails = Array.isArray(feasibility?.details) ? feasibility.details : [];
  const behaviouralValidityAvg = feasibility?.behavioural_validity_avg_percent ?? feasibility?.behavioural_validity_avg_pct;

  const reproducibility = selected?.reproducibility;
  const structuralRepro = reproducibility?.structural;
  const semanticRepro = reproducibility?.semantic;
  const lexicalRef = reproducibility?.lexical_reference;
  const reproPairs = Array.isArray(reproducibility?.pair_details) ? reproducibility.pair_details : [];

  const traceability = selected?.traceability;
  const issues = selected?.issues;
  const gtCoverage = selected?.gt_coverage;
  const reqRepro = selected?.req_reproducibility;

  const traceRuns = Array.isArray(traceability?.run_details) ? traceability.run_details : [];
  const issueRuns = Array.isArray(issues?.run_details) ? issues.run_details : [];
  const gtRuns = Array.isArray(gtCoverage?.run_details) ? gtCoverage.run_details : [];
  const reqReproPairs = Array.isArray(reqRepro?.pair_details) ? reqRepro.pair_details : [];

  const overallSummary = useMemo(() => {
    const values: number[] = [];
    const structural = structuralRepro?.average_percent;
    const semantic = semanticRepro?.average_percent;
    const reqRep = reqRepro?.avg_score_percent ?? reqRepro?.avg_score_pct;
    const trace = traceability?.score_percent ?? traceability?.score_pct;
    const iss = issues?.score_percent ?? issues?.score_pct;
    const gt = gtCoverage?.score_percent ?? gtCoverage?.score_pct;

    if (typeof feasibilityScore === 'number') values.push(feasibilityScore);
    if (typeof structural === 'number') values.push(structural);
    if (typeof semantic === 'number') values.push(semantic);
    if (typeof reqRep === 'number') values.push(reqRep);
    if (typeof trace === 'number') values.push(trace);
    if (typeof iss === 'number') values.push(iss);
    if (typeof gt === 'number') values.push(gt);

    const mean = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : null;
    return {
      count: values.length,
      mean,
      grade: typeof mean === 'number' ? reportGrade(mean) : 'N/A',
    };
  }, [feasibilityScore, structuralRepro, semanticRepro, reqRepro, traceability, issues, gtCoverage]);

  return (
    <div className="h-screen w-screen flex bg-gray-50 overflow-hidden">
      <div className="w-72 border-r border-gray-200 bg-white flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-lg mb-3">Evaluation Results</h2>
          <Input
            type="text"
            placeholder="Search results..."
            fullWidth
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {isLoadingList ? (
            <div className="text-center text-sm text-gray-600 py-8">
              <Loading size={48} thickness={4} label="Loading results..." direction="column" gap={2} />
            </div>
          ) : filteredResults.length > 0 ? (
            filteredResults.map((r) => (
              <Card
                key={r.id}
                className={`cursor-pointer transition-all ${selectedId === r.id
                  ? 'border-2 border-blue-500 bg-blue-50 shadow-md'
                  : 'border border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  }`}
                onClick={() => selectResult(r.id)}
              >
                <CardBody>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className={`font-semibold ${selectedId === r.id ? 'text-blue-900' : 'text-gray-900'}`}>{r.id}</h3>
                    {selectedId === r.id && <Badge variant="info">Active</Badge>}
                  </div>
                  <div className={`text-xs ${selectedId === r.id ? 'text-blue-700' : 'text-gray-600'}`}>
                    {r.createdOn ? new Date(r.createdOn).toLocaleString() : 'N/A'} • {formatBytes(r.sizeBytes)}
                  </div>
                </CardBody>
              </Card>
            ))
          ) : (
            <div className="text-center text-sm text-gray-600 py-8">No results found</div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          {results.length} results displayed
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Evaluation Viewer</h3>
              {selectedId ? (
                <p className="text-sm text-gray-600 mt-1">Viewing: <span className="font-medium">{selectedId}</span></p>
              ) : (
                <p className="text-sm text-gray-600 mt-1">Select an evaluation result to view</p>
              )}
            </div>

            {selected && (
              <div className="flex gap-6 text-sm">
                <div className="text-right">
                  <div className="text-gray-600">Feasibility Score</div>
                  <div className="text-lg font-semibold">{typeof feasibilityScore === 'number' ? `${feasibilityScore.toFixed(1)}%` : 'N/A'}</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-600">Completion</div>
                  <div className="text-lg font-semibold">{typeof completionRate === 'number' ? `${completionRate.toFixed(1)}%` : 'N/A'}</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-600">Runs</div>
                  <div className="text-lg font-semibold">{typeof totalRuns === 'number' ? totalRuns : 'N/A'}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          {isLoadingResult ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loading size={48} thickness={4} label="Loading evaluation..." direction="column" gap={2} />
              </div>
            </div>
          ) : selected ? (
            <div className="h-full flex flex-col ">
              <div className="border-b border-gray-200 bg-white">
                <div className="flex px-6">
                  <div className="flex p-1 rounded-[10px] bg-gray-100 cursor-pointer">
                    <TabButton
                      icon={<BarChart3 size={16} />}
                      label="Overview"
                      count={1}
                      isSelected={activeTab === 'overview'}
                      onClick={() => setActiveTab('overview')}
                    />
                    <TabButton
                      icon={<ListChecks size={16} />}
                      label="Runs"
                      count={runDetails.length}
                      isSelected={activeTab === 'runs'}
                      onClick={() => setActiveTab('runs')}
                    />
                    <TabButton
                      icon={<FileJson size={16} />}
                      label="Raw"
                      count={1}
                      isSelected={activeTab === 'raw'}
                      onClick={() => setActiveTab('raw')}
                    />
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto bg-gray-50 pb-24 ">
                {activeTab === 'overview' && (
                  <div className="p-6 max-w-5xl mx-auto space-y-4">
                    <Card className="border border-gray-200">
                      <CardBody>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Summary</div>
                            <div className="text-xs text-gray-500 mt-1">
                              Generated: {selected?.generated_at ? new Date(selected.generated_at).toLocaleString() : 'N/A'}
                            </div>
                            {selectedMeta?.sizeBytes && (
                              <div className="text-xs text-gray-500 mt-1">
                                File Size: {formatBytes(selectedMeta.sizeBytes)}
                              </div>
                            )}
                          </div>
                          {grade && (
                            <Badge variant="success">{grade}</Badge>
                          )}
                        </div>
                      </CardBody>
                    </Card>

                    <Card className="border border-gray-200">
                      <CardBody>
                        <div className="text-sm font-semibold text-gray-900 mb-2">Feasibility</div>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div className="text-gray-700">Successful runs</div>
                          <div className="text-gray-900 font-medium">{feasibility?.successful_runs ?? 'N/A'} / {feasibility?.total_runs ?? 'N/A'}</div>

                          <div className="text-gray-700">Behavioural validity (avg)</div>
                          <div className="text-gray-900 font-medium">
                            {typeof behaviouralValidityAvg === 'number'
                              ? `${behaviouralValidityAvg.toFixed(1)}%`
                              : 'N/A'}
                          </div>

                          <div className="text-gray-700">Behavioural validity (sd)</div>
                          <div className="text-gray-900 font-medium">
                            {typeof feasibility?.behavioural_validity_sd === 'number'
                              ? feasibility.behavioural_validity_sd.toFixed(2)
                              : 'N/A'}
                          </div>
                        </div>
                      </CardBody>
                    </Card>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Card className="border border-gray-200">
                        <CardBody>
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-gray-900">Reproducibility</div>
                            {semanticRepro?.grade && <Badge variant="default">{String(semanticRepro.grade)}</Badge>}
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                            <div className="text-gray-700">Structural</div>
                            <div className="text-gray-900 font-medium">
                              {typeof structuralRepro?.average_percent === 'number' ? `${structuralRepro.average_percent.toFixed(2)}%` : 'N/A'}
                              {typeof structuralRepro?.sd === 'number' ? ` ±${structuralRepro.sd}` : ''}
                            </div>

                            <div className="text-gray-700">Semantic (SBERT)</div>
                            <div className="text-gray-900 font-medium">
                              {typeof semanticRepro?.average_percent === 'number' ? `${semanticRepro.average_percent.toFixed(2)}%` : 'N/A'}
                              {typeof semanticRepro?.sd === 'number' ? ` ±${semanticRepro.sd}` : ''}
                            </div>

                            <div className="text-gray-700">Lexical (ref)</div>
                            <div className="text-gray-900 font-medium">
                              {typeof lexicalRef?.average_percent === 'number' ? `${lexicalRef.average_percent.toFixed(2)}%` : 'N/A'}
                            </div>
                          </div>
                        </CardBody>
                      </Card>

                      <Card className="border border-gray-200">
                        <CardBody>
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-gray-900">Traceability</div>
                            {traceability?.grade && <Badge variant="success">{String(traceability.grade)}</Badge>}
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                            <div className="text-gray-700">Runs evaluated</div>
                            <div className="text-gray-900 font-medium">{traceability?.runs_evaluated ?? 'N/A'}</div>

                            <div className="text-gray-700">Score</div>
                            <div className="text-gray-900 font-medium">
                              {typeof (traceability?.score_percent ?? traceability?.score_pct) === 'number'
                                ? `${(traceability.score_percent ?? traceability.score_pct).toFixed(2)}%`
                                : 'N/A'}
                              {typeof traceability?.sd === 'number' ? ` ±${traceability.sd}` : ''}
                            </div>
                          </div>
                        </CardBody>
                      </Card>

                      <Card className="border border-gray-200">
                        <CardBody>
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-gray-900">Issues Traceability</div>
                            {issues?.grade && <Badge variant="success">{String(issues.grade)}</Badge>}
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                            <div className="text-gray-700">Runs evaluated</div>
                            <div className="text-gray-900 font-medium">{issues?.runs_evaluated ?? 'N/A'}</div>

                            <div className="text-gray-700">Score</div>
                            <div className="text-gray-900 font-medium">
                              {typeof (issues?.score_percent ?? issues?.score_pct) === 'number'
                                ? `${(issues.score_percent ?? issues.score_pct).toFixed(2)}%`
                                : 'N/A'}
                              {typeof issues?.sd === 'number' ? ` ±${issues.sd}` : ''}
                            </div>
                          </div>
                        </CardBody>
                      </Card>

                      <Card className="border border-gray-200">
                        <CardBody>
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-gray-900">Ground-truth Coverage</div>
                            {gtCoverage?.grade && <Badge variant="success">{String(gtCoverage.grade)}</Badge>}
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                            <div className="text-gray-700">Primary threshold</div>
                            <div className="text-gray-900 font-medium">{gtCoverage?.primary_threshold ?? 'N/A'}</div>

                            <div className="text-gray-700">Score</div>
                            <div className="text-gray-900 font-medium">
                              {typeof (gtCoverage?.score_percent ?? gtCoverage?.score_pct) === 'number'
                                ? `${(gtCoverage.score_percent ?? gtCoverage.score_pct).toFixed(2)}%`
                                : 'N/A'}
                              {typeof gtCoverage?.sd === 'number' ? ` ±${gtCoverage.sd}` : ''}
                            </div>
                          </div>
                        </CardBody>
                      </Card>

                      <Card className="border border-gray-200">
                        <CardBody>
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-gray-900">Requirement Content Reproducibility</div>
                            {reqRepro?.grade && <Badge variant="default">{String(reqRepro.grade)}</Badge>}
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                            <div className="text-gray-700">Method</div>
                            <div className="text-gray-900 font-medium">{reqRepro?.method ?? 'N/A'}</div>

                            <div className="text-gray-700">Avg score</div>
                            <div className="text-gray-900 font-medium">
                              {typeof (reqRepro?.avg_score_percent ?? reqRepro?.avg_score_pct) === 'number'
                                ? `${(reqRepro.avg_score_percent ?? reqRepro.avg_score_pct).toFixed(2)}%`
                                : 'N/A'}
                              {typeof reqRepro?.sd === 'number' ? ` ±${reqRepro.sd}` : ''}
                            </div>
                          </div>
                        </CardBody>
                      </Card>

                      <Card className="border border-gray-200">
                        <CardBody>
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-gray-900">Overall Summary</div>
                            <Badge variant={overallSummary.grade === 'Excellent' ? 'success' : overallSummary.grade === 'Good' ? 'info' : overallSummary.grade === 'Satisfactory' ? 'warning' : 'default'}>
                              {overallSummary.grade}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                            <div className="text-gray-700">Metrics included</div>
                            <div className="text-gray-900 font-medium">{overallSummary.count}</div>

                            <div className="text-gray-700">Mean score</div>
                            <div className="text-gray-900 font-medium">
                              {typeof overallSummary.mean === 'number' ? `${overallSummary.mean.toFixed(2)}%` : 'N/A'}
                            </div>
                          </div>
                        </CardBody>
                      </Card>
                    </div>

                    <Card className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow">
                      <CardBody>
                        <button
                          type="button"
                          className="w-full text-left flex items-center justify-between gap-3 cursor-pointer px-2 py-1"
                          onClick={() => setExpandedSections((p) => ({ ...p, repro: !p.repro }))}
                          aria-expanded={expandedSections.repro === true}
                        >
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Reproducibility details</div>
                            <div className="text-xs text-gray-500 mt-1">Pairwise structural / lexical / SBERT (if available)</div>
                          </div>
                          <ChevronDown
                            className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.repro ? 'rotate-180' : ''}`}
                          />
                        </button>

                        {expandedSections.repro && (
                          <div className="mt-4 space-y-2">
                            {reproPairs.length === 0 ? (
                              <div className="text-sm text-gray-600">No pair details available</div>
                            ) : (
                              reproPairs.map((p: any, idx: number) => (
                                <div key={idx} className="bg-white border border-gray-200 rounded-lg px-3 py-2">
                                  <div className="flex items-center justify-between gap-3">
                                    <div className="text-sm font-medium text-gray-900">{String(p?.pair ?? `pair_${idx + 1}`)}</div>
                                    <div className="flex items-center gap-2">
                                      <Badge variant="default">Structural {fmtPct(p?.structural_similarity_percent)}</Badge>
                                      <Badge variant="default">Lexical {fmtPct(p?.lexical_percent)}</Badge>
                                      {typeof p?.sbert_percent === 'number' && <Badge variant="info">SBERT {fmtPct(p.sbert_percent)}</Badge>}
                                    </div>
                                  </div>
                                  <div className="text-xs text-gray-500 mt-1">
                                    Turns compared: {p?.turns_compared ?? 'N/A'} • Messages: {p?.messages_run_a ?? 'N/A'} vs {p?.messages_run_b ?? 'N/A'}
                                  </div>
                                </div>
                              ))
                            )}
                          </div>
                        )}
                      </CardBody>
                    </Card>

                    <Card className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow">
                      <CardBody>
                        <button
                          type="button"
                          className="w-full text-left flex items-center justify-between gap-3 cursor-pointer rounded-lg px-2 py-1"
                          onClick={() => setExpandedSections((p) => ({ ...p, trace: !p.trace }))}
                          aria-expanded={expandedSections.trace === true}
                        >
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Traceability details</div>
                            <div className="text-xs text-gray-500 mt-1">Per-run structural and semantic traceability</div>
                          </div>
                          <ChevronDown
                            className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.trace ? 'rotate-180' : ''}`}
                          />
                        </button>

                        {expandedSections.trace && (
                          <div className="mt-4 space-y-3 ">
                            {traceRuns.length === 0 ? (
                              <div className="text-sm text-gray-600">No per-run traceability details available</div>
                            ) : (
                              traceRuns.map((r: any) => {
                                const runId = String(r?.run ?? r?.id ?? 'run');
                                const expanded = expandedTraceRuns[runId] === true;
                                const reqs = Array.isArray(r?.requirements) ? r.requirements : [];
                                return (
                                  <div
                                    key={runId}
                                    className={'rounded-lg transition-all border border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'}
                                  >
                                    <button
                                      type="button"
                                      className="w-full text-left px-3 py-2 cursor-pointer"
                                      onClick={() => setExpandedTraceRuns((p) => ({ ...p, [runId]: !expanded }))}
                                    >
                                      <div className="flex items-center justify-between gap-3">
                                        <div className="text-sm font-semibold text-gray-900">{runId}</div>
                                        <div className="flex items-center gap-2">
                                          <Badge variant="default">Reqs {r?.total_requirements ?? reqs.length ?? 'N/A'}</Badge>
                                          <Badge variant="default">Score {fmtPct(r?.score_percent ?? r?.score_pct)}</Badge>
                                        </div>
                                      </div>
                                      <div className={`text-xs  mt-1 ${expanded ? 'text-blue-700' : 'text-gray-600'}`}>
                                        Structural: {fmtPct(r?.structural_traceability_percent)} • Semantic: {fmtPct(r?.semantic_similarity_percent)}
                                        {typeof r?.avg_sbert === 'number' ? ` • Avg SBERT ${r.avg_sbert}` : ''}
                                        {typeof r?.avg_tfidf === 'number' ? ` • Avg TF-IDF ${r.avg_tfidf}` : ''}
                                      </div>
                                    </button>

                                    {expanded && (
                                      <div className="px-3 pb-3 border-t border-gray-200 p-4 bg-gray-50">
                                        {reqs.length === 0 ? (
                                          <div className="text-sm text-gray-600">No requirement-level traceability details</div>
                                        ) : (
                                          <div className="space-y-2">
                                            {reqs.map((q: any, idx: number) => (
                                              <div key={idx} className="bg-white border border-gray-200 rounded-lg px-3 py-2">
                                                <div className="flex items-start justify-between gap-3">
                                                  <div className="min-w-0">
                                                    <div className="text-sm font-medium text-gray-900">#{q?.id ?? idx + 1}</div>
                                                    <div className="text-sm text-gray-700 mt-1 wrap-break-word">{String(q?.text ?? '')}</div>
                                                    <div className="text-xs text-gray-500 mt-1">Turn: {q?.source_turn ?? q?.turn ?? 'N/A'}</div>
                                                  </div>
                                                  <div className="shrink-0 flex flex-col items-end gap-2">
                                                    <Badge variant={boolVariant(q?.struct_traced)}>Struct {q?.struct_traced === true ? 'Pass' : 'Fail'}</Badge>
                                                    <Badge variant={boolVariant(q?.sem_traced)}>Sem {q?.sem_traced === true ? 'Pass' : 'Fail'}</Badge>
                                                    {typeof q?.sbert === 'number' && <Badge variant="info">SBERT {q.sbert}</Badge>}
                                                    {typeof q?.tfidf === 'number' && <Badge variant="info">TF-IDF {q.tfidf}</Badge>}
                                                  </div>
                                                </div>
                                              </div>
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                );
                              })
                            )}
                          </div>
                        )}
                      </CardBody>
                    </Card>

                    <Card className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow">
                      <CardBody>
                        <button
                          type="button"
                          className="w-full text-left flex items-center justify-between gap-3 cursor-pointer  px-2 py-1"
                          onClick={() => setExpandedSections((p) => ({ ...p, issues: !p.issues }))}
                          aria-expanded={expandedSections.issues === true}
                        >
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Issues details</div>
                            <div className="text-xs text-gray-500 mt-1">Per-run issues traceability and issue list</div>
                          </div>
                          <ChevronDown
                            className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.issues ? 'rotate-180' : ''}`}
                          />
                        </button>

                        {expandedSections.issues && (
                          <div className="mt-4 space-y-3">
                            {issueRuns.length === 0 ? (
                              <div className="text-sm text-gray-600">No per-run issues details available</div>
                            ) : (
                              issueRuns.map((r: any) => {
                                const runId = String(r?.run ?? r?.id ?? 'run');
                                const expanded = expandedIssueRuns[runId] === true;
                                const items = Array.isArray(r?.issues) ? r.issues : [];

                                return (
                                  <div
                                    key={runId}
                                    className={'rounded-lg transition-all border border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'}
                                  >
                                    <button
                                      type="button"
                                      className="w-full text-left px-3 py-2 cursor-pointer"
                                      onClick={() => setExpandedIssueRuns((p) => ({ ...p, [runId]: !expanded }))}
                                    >
                                      <div className="flex items-center justify-between gap-3">
                                        <div className="text-sm font-semibold text-gray-900">{runId}</div>
                                        <div className="flex items-center gap-2">
                                          {typeof r?.score_percent === 'number' || typeof r?.score_pct === 'number' ? (
                                            <Badge variant="default">Traceability {fmtPct(r?.score_percent ?? r?.score_pct)}</Badge>
                                          ) : (
                                            <Badge variant="default">N/A</Badge>
                                          )}
                                          {typeof r?.total_issues === 'number' && <Badge variant="default">Issues {r.total_issues}</Badge>}
                                        </div>
                                      </div>
                                      {r?.note && <div className="text-xs text-gray-600 mt-1">{String(r.note)}</div>}
                                      {!r?.note && (
                                        <div className={`text-xs  mt-1 ${expanded ? 'text-blue-700' : 'text-gray-600'}`}>
                                          Turn coverage: {fmtPct(r?.turn_coverage_percent)} • Req linkage: {fmtPct(r?.requirement_linkage_percent)}
                                        </div>
                                      )}
                                    </button>

                                    {expanded && !r?.note && (
                                      <div className="px-3 pb-3 space-y-2 border-t border-gray-200 p-4 bg-gray-50">
                                        {items.length === 0 ? (
                                          <div className="text-sm text-gray-600">No issues listed</div>
                                        ) : (
                                          items.map((iss: any, idx: number) => (
                                            <div key={idx} className="bg-white border border-gray-200 rounded-lg px-3 py-2">
                                              <div className="flex items-start justify-between gap-3">
                                                <div className="min-w-0">
                                                  <div className="text-sm font-medium text-gray-900">Issue #{iss?.issue_id ?? idx + 1}</div>
                                                  <div className="text-sm text-gray-700 mt-1 wrap-break-word">{String(iss?.description ?? '')}</div>
                                                  <div className="text-xs text-gray-500 mt-1">Turn: {iss?.turn_id ?? 'N/A'} • Related req: {iss?.related_req_id ?? 'N/A'} • By: {iss?.created_by ?? 'N/A'}</div>
                                                </div>
                                                <div className="shrink-0 flex flex-col items-end gap-2">
                                                  {iss?.type && <Badge variant="default">{String(iss.type)}</Badge>}
                                                  {iss?.severity && <Badge variant={severityVariant(iss.severity)}>{String(iss.severity)}</Badge>}
                                                  {iss?.status && <Badge variant={statusVariant(iss.status)}>{String(iss.status)}</Badge>}
                                                </div>
                                              </div>
                                            </div>
                                          ))
                                        )}
                                      </div>
                                    )}
                                  </div>
                                );
                              })
                            )}
                          </div>
                        )}
                      </CardBody>
                    </Card>

                    <Card className="border border-gray-200 rounded-lg px-2 py-1 cursor-pointer hover:shadow-md transition-shadow">
                      <CardBody>
                        <button
                          type="button"
                          className="w-full text-left flex items-center justify-between gap-3 cursor-pointer"
                          onClick={() => setExpandedSections((p) => ({ ...p, gt: !p.gt }))}
                          aria-expanded={expandedSections.gt === true}
                        >
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Ground-truth coverage details</div>
                            <div className="text-xs text-gray-500 mt-1">Per-run coverage and per-ground-truth matches</div>
                          </div>
                          <ChevronDown
                            className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.gt ? 'rotate-180' : ''}`}
                          />
                        </button>

                        {expandedSections.gt && (
                          <div className="mt-4 space-y-3">
                            {gtRuns.length === 0 ? (
                              <div className="text-sm text-gray-600">No per-run GT details available</div>
                            ) : (
                              gtRuns.map((r: any) => {
                                const runId = String(r?.run ?? r?.id ?? 'run');
                                const expanded = expandedGtRuns[runId] === true;
                                const perGt = Array.isArray(r?.per_gt) ? r.per_gt : [];
                                const primary = gtCoverage?.primary_threshold;
                                const primaryKey = primary != null ? `covered_${primary}` : null;

                                const covered045 = r?.['covered_sbert_0.45'] ?? r?.covered_sbert_0_45;
                                const covered06 = r?.['covered_sbert_0.6'] ?? r?.covered_sbert_0_6;
                                const covered07 = r?.['covered_sbert_0.7'] ?? r?.covered_sbert_0_7;

                                return (
                                  <div
                                    key={runId}
                                    className={'rounded-lg transition-all border border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'}
                                  >
                                    <button
                                      type="button"
                                      className="w-full text-left px-3 py-2 cursor-pointer"
                                      onClick={() => setExpandedGtRuns((p) => ({ ...p, [runId]: !expanded }))}
                                    >
                                      <div className="flex items-center justify-between gap-3">
                                        <div className="text-sm font-semibold text-gray-900">{runId}</div>
                                        <div className="flex items-center gap-2">
                                          <Badge variant="default">Score {fmtPct(r?.score_percent ?? r?.score_pct)}</Badge>
                                          <Badge variant="default">GT {r?.total_gt ?? perGt.length ?? 'N/A'}</Badge>
                                        </div>
                                      </div>
                                      <div className={`text-xs  mt-1 ${expanded ? 'text-blue-700' : 'text-gray-600'}`}>
                                        Covered (SBERT): 0.45 → {covered045 ?? 'N/A'} • 0.60 → {covered06 ?? 'N/A'} • 0.70 → {covered07 ?? 'N/A'}
                                      </div>
                                    </button>

                                    {expanded && (
                                      <div className="px-3 pb-3 space-y-2 border-t border-gray-200 p-4 bg-gray-50">
                                        {perGt.length === 0 ? (
                                          <div className="text-sm text-gray-600">No per-ground-truth details</div>
                                        ) : (
                                          perGt.map((g: any, idx: number) => {
                                            const coveredPrimary = primaryKey
                                              ? g?.[primaryKey] === true
                                              : g?.['covered_0.45'] === true || g?.covered_0_45 === true;
                                            return (
                                              <div key={idx} className="bg-white border border-gray-200 cursor-default rounded-lg px-3 py-2">
                                                <div className="flex items-start justify-between gap-3">
                                                  <div className="min-w-0">
                                                    <div className="text-sm font-medium text-gray-900">[{String(g?.id ?? idx + 1)}] {String(g?.type ?? '')}</div>
                                                    <div className="text-sm text-gray-700 mt-1 wrap-break-word">{String(g?.ground_truth ?? '')}</div>
                                                  </div>
                                                  <div className="shrink-0 flex flex-col items-end gap-2">
                                                    <Badge variant={coveredPrimary ? 'success' : 'error'}>{coveredPrimary ? 'Covered' : 'Miss'}</Badge>
                                                    {typeof g?.best_sbert === 'number' && <Badge variant="info">SBERT {g.best_sbert}</Badge>}
                                                    {typeof g?.best_tfidf === 'number' && <Badge variant="info">TF-IDF {g.best_tfidf}</Badge>}
                                                  </div>
                                                </div>
                                              </div>
                                            );
                                          })
                                        )}
                                      </div>
                                    )}
                                  </div>
                                );
                              })
                            )}
                          </div>
                        )}
                      </CardBody>
                    </Card>

                    <Card className="border border-gray-200 cursor-pointer rounded-lg hover:shadow-md transition-shadow">
                      <CardBody>
                        <button
                          type="button"
                          className="w-full text-left flex items-center justify-between gap-3 cursor-pointer rounded-lg px-2 py-1"
                          onClick={() => setExpandedSections((p) => ({ ...p, reqRepro: !p.reqRepro }))}
                          aria-expanded={expandedSections.reqRepro === true}
                        >
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Requirement reproducibility details</div>
                            <div className="text-xs text-gray-500 mt-1">Pairwise best-match similarity across extracted requirements</div>
                          </div>
                          <ChevronDown
                            className={`w-5 h-5 text-gray-400 transition-transform ${expandedSections.reqRepro ? 'rotate-180' : ''}`}
                          />
                        </button>

                        {expandedSections.reqRepro && (
                          <div className="mt-4 space-y-2">
                            {reqReproPairs.length === 0 ? (
                              <div className="text-sm text-gray-600">No pair details available</div>
                            ) : (
                              reqReproPairs.map((p: any, idx: number) => (
                                <div key={idx} className="bg-white border border-gray-200 rounded-lg px-3 py-2 cursor-default">
                                  <div className="flex items-center justify-between gap-3">
                                    <div className="text-sm font-medium text-gray-900">{String(p?.pair ?? `pair_${idx + 1}`)}</div>
                                    <div className="flex items-center gap-2">
                                      <Badge variant="default">Reqs {p?.reqs_run_a ?? 'N/A'} vs {p?.reqs_run_b ?? 'N/A'}</Badge>
                                      <Badge variant="info">{fmtPct(p?.symmetric_score_percent)}</Badge>
                                    </div>
                                  </div>
                                  <div className="text-xs text-gray-500 mt-1">
                                    A→B: {fmtPct(p?.ab_best_match_percent)} • B→A: {fmtPct(p?.ba_best_match_percent)} • Method: {p?.method ?? 'N/A'}
                                  </div>
                                </div>
                              ))
                            )}
                          </div>
                        )}
                      </CardBody>
                    </Card>
                  </div>
                )}

                {activeTab === 'runs' && (
                  <div className="p-6 max-w-5xl mx-auto space-y-4">
                    {runDetails.length === 0 ? (
                      <div className="text-center text-gray-600 py-12">
                        No per-run details available in this evaluation
                      </div>
                    ) : (
                      runDetails.map((run: any) => {
                        const runId = String(run?.run ?? run?.id ?? 'run');
                        const expanded = expandedRuns[runId] === true;
                        const behavioural = run?.behavioural_validity;
                        const checks = behavioural?.checks && typeof behavioural.checks === 'object' ? behavioural.checks : null;
                        const warnings = Array.isArray(run?.warnings) ? run.warnings : [];
                        const errors = Array.isArray(run?.errors) ? run.errors : [];
                        const scorePct = behavioural?.score_percent ?? behavioural?.score_pct;
                        const passed = behavioural?.passed;
                        const total = behavioural?.total;

                        return (
                          <Card
                            key={runId}
                            className={'cursor-pointer transition-all border border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'}
                            onClick={() => setExpandedRuns((prev) => ({ ...prev, [runId]: !expanded }))}
                          >
                            <CardBody>
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <div className={`text-sm font-semibold ${expanded ? 'text-blue-900' : 'text-gray-900'}`}>{runId}</div>
                                  <div className={`text-xs mt-1 ${expanded ? 'text-blue-700' : 'text-gray-600'}`}>
                                    Turns: {run?.turns ?? 'N/A'} • Messages: {run?.messages ?? 'N/A'} • Seed: {run?.seed ?? 'N/A'}
                                  </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                  {typeof scorePct === 'number' && (
                                    <Badge variant="info">Behavioural validity {scorePct.toFixed(1)}%</Badge>
                                  )}
                                  {typeof passed === 'number' && typeof total === 'number' && (
                                    <Badge variant="default">{passed}/{total}</Badge>
                                  )}
                                  {run?.status && (
                                    <Badge variant={statusVariant(run.status)}>{String(run.status)}</Badge>
                                  )}
                                </div>
                              </div>

                              {expanded && (
                                <div className="mt-4 space-y-4 border-t border-gray-200 p-4 bg-gray-50">
                                  <div className="border-t border-blue-200 pt-4" />

                                  <div>
                                    <div className="text-sm font-semibold text-gray-900 mb-2">Behavioural validity checks</div>
                                    {checks ? (
                                      <div className="grid grid-cols-2 gap-2 text-sm">
                                        {Object.entries(checks).map(([key, value]) => (
                                          <div key={key} className="flex items-center justify-between gap-3 bg-white border border-gray-200 rounded-lg px-3 py-2">
                                            <div className="text-gray-700">{CHECK_LABELS[key] ?? key}</div>
                                            <Badge variant={boolVariant(value)}>{value === true ? 'Pass' : 'Fail'}</Badge>
                                          </div>
                                        ))}
                                      </div>
                                    ) : (
                                      <div className="text-sm text-gray-600">No checks available for this run</div>
                                    )}
                                  </div>

                                  <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                                      <div className="text-sm font-semibold text-gray-900 mb-2">Warnings</div>
                                      {warnings.length > 0 ? (
                                        <div className="space-y-2">
                                          {warnings.map((w: any, idx: number) => (
                                            <div key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                                              <Badge variant="warning">Warn</Badge>
                                              <div className="flex-1">{String(w)}</div>
                                            </div>
                                          ))}
                                        </div>
                                      ) : (
                                        <div className="text-sm text-gray-600">None</div>
                                      )}
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                                      <div className="text-sm font-semibold text-gray-900 mb-2">Errors</div>
                                      {errors.length > 0 ? (
                                        <div className="space-y-2">
                                          {errors.map((err: any, idx: number) => (
                                            <div key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                                              <Badge variant="error">Error</Badge>
                                              <div className="flex-1">{String(err)}</div>
                                            </div>
                                          ))}
                                        </div>
                                      ) : (
                                        <div className="text-sm text-gray-600">None</div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </CardBody>
                          </Card>
                        );
                      })
                    )}
                  </div>
                )}

                {activeTab === 'raw' && (
                  <div className="p-6 max-w-5xl mx-auto">
                    <Card className="border border-gray-200">
                      <CardBody>
                        <pre className="text-xs text-gray-800 whitespace-pre-wrap wrap-break-word overflow-x-auto">
                          {JSON.stringify(selected, null, 2)}
                        </pre>
                      </CardBody>
                    </Card>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-sm text-gray-600">
              Select an evaluation result to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
