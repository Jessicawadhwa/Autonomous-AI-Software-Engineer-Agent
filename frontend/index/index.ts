export type ViewMode = 'dashboard' | 'wizard' | 'ide' | 'settings' | 'mcp';

export interface Project {
  id: string;
  name: string;
  description?: string;
  requirement: string;
  status: 'idle' | 'running' | 'completed' | 'failed' | 'paused';
  options: {
    generate_tests?: boolean;
    generate_docs?: boolean;
    initialize_git?: boolean;
    run_code_review?: boolean;
    enable_mcp?: boolean;
    auto_approve?: boolean;
  };
  workspace_path?: string;
  created_at: string;
  updated_at: string;
  last_run_status?: string;
  total_tests_passed?: number;
  total_tests_failed?: number;
}

export interface AgentRun {
  id: string;
  project_id: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'awaiting_approval' | 'stopped';
  current_agent?: string;
  current_task?: string;
  debug_iterations: number;
  error?: string;
  metrics?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface AgentMessage {
  id: string;
  run_id: string;
  project_id: string;
  agent_name: string;
  message_type: string;
  content: string;
  data?: Record<string, any>;
  duration_seconds?: number;
  created_at: string;
}

export interface TestFailure {
  test_name: string;
  traceback: string;
}

export interface TestResult {
  id?: string;
  run_id?: string;
  iteration: number;
  total: number;
  passed: number;
  failed: number;
  errors: number;
  failures: TestFailure[];
  stdout?: string;
  stderr?: string;
  duration?: number;
  created_at?: string;
}

export interface ReviewFinding {
  id?: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  file: string;
  line?: number;
  issue: string;
  recommendation: string;
}

export interface GitCommit {
  commit_hash: string;
  message: string;
  author: string;
  timestamp: string;
}

export interface GitInfo {
  status?: {
    has_changes: boolean;
    changes: string[];
  };
  log?: GitCommit[];
  diff?: string;
}

export interface ApprovalRequest {
  id: string;
  run_id: string;
  project_id: string;
  action_type: string;
  command?: string;
  details?: Record<string, any>;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
}

export interface LLMSettings {
  provider: 'demo' | 'openai' | 'gemini';
  openai_api_key?: string;
  openai_model: string;
  google_api_key?: string;
  gemini_model: string;
  temperature: number;
  max_tokens: number;
  max_debug_iterations: number;
  auto_approve: boolean;
}

export interface DashboardStats {
  total_projects: number;
  successful_builds: number;
  failed_builds: number;
  average_build_time_seconds: number;
  total_tests_passed: number;
  total_agent_runs: number;
}
