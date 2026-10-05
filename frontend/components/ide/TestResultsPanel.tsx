import React from 'react';
import { TestResult, TestFailure } from '../../types';
import { CheckCheck, XCircle, Clock, AlertCircle, FileCode, CheckCircle2 } from 'lucide-react';

interface TestResultsPanelProps {
  testResults: TestResult | null;
  onSelectFile?: (path: string) => void;
}

export const TestResultsPanel: React.FC<TestResultsPanelProps> = ({ testResults, onSelectFile }) => {
  if (!testResults) {
    return (
      <div className="h-full flex items-center justify-center text-slate-500 text-xs bg-[#090d16] select-none">
        No test runs recorded for this project yet.
      </div>
    );
  }

  const { total, passed, failed, errors, failures, duration } = testResults;
  const isSuccess = failed === 0 && errors === 0 && passed > 0;

  return (
    <div className="h-full flex flex-col bg-[#090d16] overflow-y-auto p-4 space-y-4 text-xs font-sans select-none">
      {/* Test Metrics Header Cards */}
      <div className="flex flex-wrap items-center gap-3">
        <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border ${
          isSuccess 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
        }`}>
          {isSuccess ? <CheckCheck className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-rose-400" />}
          <span className="font-bold text-sm">
            {isSuccess ? 'ALL TESTS PASSED' : 'TEST FAILURES DETECTED'}
          </span>
        </div>

        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
          <span className="text-slate-500">Total:</span>
          <span className="font-bold text-white font-mono">{total}</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{passed} Passed</span>
        </div>

        {failed > 0 && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-rose-400">
            <XCircle className="w-3.5 h-3.5" />
            <span>{failed} Failed</span>
          </div>
        )}

        {duration !== undefined && (
          <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 font-mono">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>{duration}s</span>
          </div>
        )}
      </div>

      {/* Failure Breakdown */}
      {failures && failures.length > 0 && (
        <div className="space-y-3">
          <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4" />
            <span>Failure Analysis & Tracebacks</span>
          </div>

          <div className="space-y-2">
            {failures.map((f, idx) => (
              <div key={idx} className="bg-slate-900/80 border border-rose-500/30 rounded-xl p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-rose-300 font-mono text-xs flex items-center gap-2">
                    <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                    <span>{f.test_name}</span>
                  </div>
                </div>

                <div className="bg-[#090d16] border border-slate-800 rounded-lg p-2.5 font-mono text-[11px] text-slate-300 overflow-x-auto whitespace-pre leading-relaxed">
                  {f.traceback}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
