import React from 'react';
import { GitInfo, GitCommit } from '../../types';
import { GitBranch, GitCommit as GitCommitIcon, Clock, User, Check } from 'lucide-react';

interface GitPanelProps {
  gitInfo: GitInfo | null;
}

export const GitPanel: React.FC<GitPanelProps> = ({ gitInfo }) => {
  const commits = gitInfo?.log || [];

  return (
    <div className="h-full flex flex-col bg-[#090d16] overflow-y-auto p-4 space-y-4 text-xs select-none">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-bold text-slate-200">
          <GitBranch className="w-4 h-4 text-purple-400" />
          <span>Git Version Control History</span>
        </div>
        <span className="text-[11px] font-mono text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
          branch: main
        </span>
      </div>

      <div className="space-y-3">
        {commits.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            No git commits recorded yet.
          </div>
        ) : (
          commits.map((c, idx) => (
            <div 
              key={idx}
              className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5 space-y-2 hover:border-purple-500/30 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GitCommitIcon className="w-4 h-4 text-purple-400 shrink-0" />
                  <span className="font-semibold text-slate-200">{c.message}</span>
                </div>
                <span className="font-mono text-[10px] bg-purple-950/60 text-purple-300 px-1.5 py-0.5 rounded border border-purple-800/40">
                  {c.commit_hash}
                </span>
              </div>

              <div className="flex items-center gap-4 text-[11px] text-slate-500">
                <span className="flex items-center gap-1">
                  <User className="w-3 h-3" /> {c.author}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {new Date(c.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
