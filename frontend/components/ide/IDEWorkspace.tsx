import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { 
  Project, 
  FileNode, 
  TestResult, 
  ReviewFinding, 
  GitInfo, 
  ApprovalRequest 
} from '../../types';
import { projectApi } from '../../services/api';
import { ProjectWebSocket } from '../../services/websocket';
import { FileExplorer } from './FileExplorer';
import { CodeEditor } from './CodeEditor';
import { AgentTimeline } from './AgentTimeline';
import { ApprovalBanner } from './ApprovalBanner';
import { TerminalPanel } from './TerminalPanel';
import { TestResultsPanel } from './TestResultsPanel';
import { CodeReviewPanel } from './CodeReviewPanel';
import { GitPanel } from './GitPanel';
import { 
  Play, 
  Square, 
  Download, 
  Terminal, 
  CheckCheck, 
  ShieldCheck, 
  GitBranch, 
  Sparkles, 
  ChevronUp, 
  ChevronDown,
  RotateCw
} from 'lucide-react';

interface IDEWorkspaceProps {
  projectId: string;
  onBackToDashboard: () => void;
}

export const IDEWorkspace: React.FC<IDEWorkspaceProps> = ({ projectId, onBackToDashboard }) => {
  const [project, setProject] = useState<Project | null>(null);
  const [tree, setTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [originalFileContent, setOriginalFileContent] = useState<string | undefined>(undefined);
  const [isFileLoading, setIsFileLoading] = useState(false);

  // Agent execution states
  const [currentAgent, setCurrentAgent] = useState<string>('idle');
  const [currentTask, setCurrentTask] = useState<string>('');
  const [agentStatus, setAgentStatus] = useState<string>('idle');
  const [debugIterations, setDebugIterations] = useState<number>(0);

  // Diagnostics & Logs
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [testResults, setTestResults] = useState<TestResult | null>(null);
  const [reviewFindings, setReviewFindings] = useState<ReviewFinding[]>([]);
  const [gitInfo, setGitInfo] = useState<GitInfo | null>(null);
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequest | null>(null);

  // Bottom dock tab
  const [activeBottomTab, setActiveBottomTab] = useState<'terminal' | 'tests' | 'review' | 'git'>('terminal');
  const [isBottomCollapsed, setIsBottomCollapsed] = useState(false);

  // Load project initial data
  const loadProjectData = async () => {
    try {
      const data = await projectApi.get(projectId);
      setProject(data.project);
      setTree(data.tree || []);
      setAgentStatus(data.project.status);
      setGitInfo(data.git);

      if (data.tests && data.tests.length > 0) {
        setTestResults(data.tests[0]);
      }
      if (data.reviews && data.reviews.length > 0) {
        setReviewFindings(data.reviews);
      }
      if (data.approvals && data.approvals.length > 0) {
        const pending = data.approvals.find((a: ApprovalRequest) => a.status === 'pending');
        setPendingApproval(pending || null);
      }

      // Auto open README.md or main.py if available
      if (!selectedFile && data.tree && data.tree.length > 0) {
        const readme = data.tree.find((n: FileNode) => n.name === 'README.md');
        if (readme) {
          handleSelectFile('README.md');
        } else {
          // Find first file
          const first = data.tree[0];
          if (first.type === 'file') {
            handleSelectFile(first.path);
          }
        }
      }
    } catch (err) {
      console.error('Error loading project:', err);
    }
  };

  useEffect(() => {
    loadProjectData();

    // Setup WebSocket
    const ws = new ProjectWebSocket(projectId);
    ws.connect();

    ws.on('run_started', (data) => {
      setAgentStatus('running');
      setCurrentAgent('planner');
      setTerminalLogs((prev) => [...prev, '$ autonomous-agent run --project ' + projectId]);
    });

    ws.on('agent_step', (data) => {
      setCurrentAgent(data.agent);
      setCurrentTask(data.task);
      setDebugIterations(data.debug_attempts || 0);
      if (data.tree) setTree(data.tree);
      if (data.git) setGitInfo(data.git);
    });

    ws.on('terminal_output', (data) => {
      if (data.command) {
        setTerminalLogs((prev) => [...prev, `$ ${data.command}`]);
      }
      if (data.stdout) {
        setTerminalLogs((prev) => [...prev, data.stdout]);
      }
      if (data.stderr) {
        setTerminalLogs((prev) => [...prev, data.stderr]);
      }
    });

    ws.on('test_results', (data) => {
      setTestResults(data);
      setActiveBottomTab('tests');
    });

    ws.on('review_results', (data) => {
      setReviewFindings(data);
    });

    ws.on('approval_needed', (data) => {
      setPendingApproval(data);
    });

    ws.on('approval_resolved', () => {
      setPendingApproval(null);
    });

    ws.on('run_completed', (data) => {
      setAgentStatus('completed');
      setCurrentAgent('documenter');
      setCurrentTask('Project successfully built, tested, and reviewed.');
      if (data.tree) setTree(data.tree);
      if (data.git) setGitInfo(data.git);
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
    });

    ws.on('run_failed', (data) => {
      setAgentStatus('failed');
      setTerminalLogs((prev) => [...prev, `[FATAL] Agent run failed: ${data.error}`]);
    });

    return () => {
      ws.disconnect();
    };
  }, [projectId]);

  const handleSelectFile = async (path: string) => {
    setSelectedFile(path);
    setIsFileLoading(true);
    try {
      const res = await projectApi.getFileContent(projectId, path);
      setFileContent(res.content);
      setOriginalFileContent(res.content);
    } catch (err) {
      setFileContent('// Could not load file content');
    } finally {
      setIsFileLoading(false);
    }
  };

  const handleSaveFile = async (path: string, content: string) => {
    await projectApi.saveFileContent(projectId, path, content);
    setFileContent(content);
    setOriginalFileContent(content);
  };

  const handleStartRun = async () => {
    setAgentStatus('running');
    setCurrentAgent('planner');
    setCurrentTask('Starting agent run...');
    await projectApi.startRun(projectId, { provider: 'demo' });
  };

  const handleStopRun = async () => {
    await projectApi.stopRun(projectId);
    setAgentStatus('stopped');
  };

  const handleResolveApproval = async (approvalId: string, decision: 'approve' | 'reject') => {
    await projectApi.resolveApproval(projectId, approvalId, decision);
    setPendingApproval(null);
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-[#090d16] overflow-hidden">
      {/* Top Workspace Action Header */}
      <div className="h-11 bg-[#0d1322] border-b border-slate-800 px-4 flex items-center justify-between select-none">
        <div className="flex items-center gap-3">
          <span className="font-bold text-sm text-white">{project?.name || 'Loading project...'}</span>
          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${
            agentStatus === 'completed'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
              : agentStatus === 'running'
              ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30 animate-pulse'
              : agentStatus === 'failed'
              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              : 'bg-slate-800 text-slate-400 border border-slate-700'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${
              agentStatus === 'completed' ? 'bg-emerald-400' :
              agentStatus === 'running' ? 'bg-amber-400' :
              agentStatus === 'failed' ? 'bg-rose-400' : 'bg-slate-400'
            }`}></span>
            {agentStatus.toUpperCase()}
          </span>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          {agentStatus === 'running' ? (
            <button
              onClick={handleStopRun}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white shadow-sm transition-colors"
            >
              <Square className="w-3.5 h-3.5" />
              <span>Stop Agents</span>
            </button>
          ) : (
            <button
              onClick={handleStartRun}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-900/30 transition-colors"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Run Agents</span>
            </button>
          )}

          <a
            href={projectApi.getDownloadUrl(projectId)}
            download
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Download ZIP</span>
          </a>

          <button
            onClick={loadProjectData}
            title="Refresh"
            className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Multi-Pane Workspace Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: File Explorer (240px) */}
        <div className="w-60 shrink-0 border-r border-slate-800 h-full">
          <FileExplorer
            tree={tree}
            selectedFile={selectedFile}
            onSelectFile={handleSelectFile}
            onRefresh={loadProjectData}
          />
        </div>

        {/* Center Panel: Monaco Code Editor */}
        <div className="flex-1 flex flex-col min-w-0 border-r border-slate-800 h-full">
          <div className="flex-1 min-h-0">
            <CodeEditor
              filePath={selectedFile}
              content={fileContent}
              originalContent={originalFileContent}
              onSave={handleSaveFile}
              isLoading={isFileLoading}
            />
          </div>

          {/* Bottom Dock Panel (Terminal, Tests, Code Review, Git) */}
          <div className={`border-t border-slate-800 flex flex-col bg-[#090d16] transition-all ${
            isBottomCollapsed ? 'h-9' : 'h-56'
          }`}>
            {/* Dock Tabs Header */}
            <div className="h-9 bg-[#0d1322] border-b border-slate-800 px-3 flex items-center justify-between select-none">
              <div className="flex items-center gap-1">
                <button
                  onClick={() => { setActiveBottomTab('terminal'); setIsBottomCollapsed(false); }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                    activeBottomTab === 'terminal' && !isBottomCollapsed
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Terminal</span>
                </button>

                <button
                  onClick={() => { setActiveBottomTab('tests'); setIsBottomCollapsed(false); }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                    activeBottomTab === 'tests' && !isBottomCollapsed
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <CheckCheck className="w-3.5 h-3.5 text-teal-400" />
                  <span>Pytest</span>
                  {testResults && (
                    <span className="text-[10px] font-mono px-1 rounded bg-teal-500/20 text-teal-300">
                      {testResults.passed}/{testResults.total}
                    </span>
                  )}
                </button>

                <button
                  onClick={() => { setActiveBottomTab('review'); setIsBottomCollapsed(false); }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                    activeBottomTab === 'review' && !isBottomCollapsed
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Review</span>
                  {reviewFindings.length > 0 && (
                    <span className="text-[10px] font-mono px-1 rounded bg-indigo-500/20 text-indigo-300">
                      {reviewFindings.length}
                    </span>
                  )}
                </button>

                <button
                  onClick={() => { setActiveBottomTab('git'); setIsBottomCollapsed(false); }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                    activeBottomTab === 'git' && !isBottomCollapsed
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <GitBranch className="w-3.5 h-3.5 text-purple-400" />
                  <span>Git History</span>
                </button>
              </div>

              <button
                onClick={() => setIsBottomCollapsed(!isBottomCollapsed)}
                className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors"
              >
                {isBottomCollapsed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>

            {/* Dock Content Body */}
            {!isBottomCollapsed && (
              <div className="flex-1 min-h-0 overflow-hidden">
                {activeBottomTab === 'terminal' && (
                  <TerminalPanel logs={terminalLogs} onClear={() => setTerminalLogs([])} />
                )}
                {activeBottomTab === 'tests' && (
                  <TestResultsPanel testResults={testResults} onSelectFile={handleSelectFile} />
                )}
                {activeBottomTab === 'review' && (
                  <CodeReviewPanel findings={reviewFindings} onSelectFile={handleSelectFile} />
                )}
                {activeBottomTab === 'git' && (
                  <GitPanel gitInfo={gitInfo} />
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Agent Timeline & Human Approval (300px) */}
        <div className="w-80 shrink-0 h-full flex flex-col bg-[#0d1322] border-l border-slate-800">
          <ApprovalBanner
            approval={pendingApproval}
            onResolve={handleResolveApproval}
          />
          <AgentTimeline
            currentAgent={currentAgent}
            currentTask={currentTask}
            status={agentStatus}
            debugIterations={debugIterations}
          />
        </div>
      </div>
    </div>
  );
};
