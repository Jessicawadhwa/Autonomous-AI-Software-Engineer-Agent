import React from 'react';
import { ApprovalRequest } from '../../types';
import { ShieldAlert, Check, X, Terminal } from 'lucide-react';

interface ApprovalBannerProps {
  approval: ApprovalRequest | null;
  onResolve: (approvalId: string, decision: 'approve' | 'reject') => void;
}

export const ApprovalBanner: React.FC<ApprovalBannerProps> = ({
  approval,
  onResolve
}) => {
  if (!approval || approval.status !== 'pending') return null;

  return (
    <div className="bg-amber-950/40 border border-amber-500/40 rounded-xl p-4 m-3 space-y-3 shadow-xl backdrop-blur-md animate-bounce-subtle select-none">
      <div className="flex items-center gap-2 text-amber-300 font-bold text-xs">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
        <span>HUMAN APPROVAL REQUIRED</span>
      </div>

      <div className="text-xs text-slate-300 leading-relaxed">
        Agent requested permission to execute a potentially sensitive workspace operation:
      </div>

      {approval.command && (
        <div className="bg-[#090d16] border border-slate-800 rounded-lg p-2.5 font-mono text-xs text-amber-300 flex items-center gap-2 overflow-x-auto">
          <Terminal className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <code>{approval.command}</code>
        </div>
      )}

      <div className="flex items-center justify-end gap-2 pt-1">
        <button
          onClick={() => onResolve(approval.id, 'reject')}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          <span>Deny</span>
        </button>

        <button
          onClick={() => onResolve(approval.id, 'approve')}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-900/30 transition-colors"
        >
          <Check className="w-3.5 h-3.5" />
          <span>Approve & Proceed</span>
        </button>
      </div>
    </div>
  );
};
