import React from 'react';
import { ReviewFinding } from '../../types';
import { ShieldCheck, AlertTriangle, AlertCircle, Info, FileCode } from 'lucide-react';

interface CodeReviewPanelProps {
  findings: ReviewFinding[];
  onSelectFile?: (path: string) => void;
}

export const CodeReviewPanel: React.FC<CodeReviewPanelProps> = ({ findings, onSelectFile }) => {
  if (!findings || findings.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-slate-500 text-xs bg-[#090d16] select-none">
        No code review findings recorded yet.
      </div>
    );
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase">
            <AlertCircle className="w-3 h-3 text-rose-400" /> Critical
          </span>
        );
      case 'high':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-500/30 uppercase">
            <AlertTriangle className="w-3 h-3 text-orange-400" /> High
          </span>
        );
      case 'medium':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
            <AlertTriangle className="w-3 h-3 text-amber-400" /> Medium
          </span>
        );
      case 'low':
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 uppercase">
            <Info className="w-3 h-3 text-blue-400" /> Low
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 uppercase">
            <Info className="w-3 h-3 text-slate-400" /> Info
          </span>
        );
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#090d16] overflow-y-auto p-4 space-y-4 text-xs select-none">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-bold text-slate-200">
          <ShieldCheck className="w-4 h-4 text-indigo-400" />
          <span>Code Review & Security Analysis</span>
        </div>
        <span className="text-slate-500 text-[11px]">{findings.length} findings</span>
      </div>

      <div className="space-y-3">
        {findings.map((item, idx) => (
          <div 
            key={idx} 
            className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getSeverityBadge(item.severity)}
                <button
                  onClick={() => onSelectFile?.(item.file)}
                  className="font-mono text-xs text-indigo-300 hover:text-indigo-200 hover:underline flex items-center gap-1 font-semibold"
                >
                  <FileCode className="w-3.5 h-3.5" />
                  <span>{item.file} {item.line ? `:${item.line}` : ''}</span>
                </button>
              </div>
            </div>

            <div className="text-slate-200 font-medium leading-relaxed">
              {item.issue}
            </div>

            <div className="bg-[#090d16] border border-slate-800/80 rounded-lg p-3 text-slate-400 text-[11px] leading-relaxed">
              <span className="text-indigo-400 font-semibold block mb-0.5">Recommendation:</span>
              {item.recommendation}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
