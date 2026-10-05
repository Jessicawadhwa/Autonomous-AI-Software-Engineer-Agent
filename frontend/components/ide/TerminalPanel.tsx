import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2, Copy, Check } from 'lucide-react';

interface TerminalPanelProps {
  logs: string[];
  onClear: () => void;
}

export const TerminalPanel: React.FC<TerminalPanelProps> = ({ logs, onClear }) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = React.useState(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleCopy = () => {
    navigator.clipboard.writeText(logs.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-full flex flex-col bg-[#090d16] font-mono text-xs select-text">
      {/* Terminal Header */}
      <div className="h-8 bg-[#0d1322] border-b border-slate-800 px-3 flex items-center justify-between select-none">
        <div className="flex items-center gap-2 text-slate-400 font-semibold">
          <Terminal className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[11px] uppercase tracking-wider">Terminal Output</span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopy}
            title="Copy logs"
            className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
          </button>
          <button
            onClick={onClear}
            title="Clear terminal"
            className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Terminal Log Lines */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1 text-slate-300">
        {logs.length === 0 ? (
          <div className="text-slate-600 italic select-none">
            Ready. Waiting for agent commands (pytest, git, subprocess)...
          </div>
        ) : (
          logs.map((line, idx) => {
            let textColor = 'text-slate-300';
            if (line.includes('PASSED') || line.includes('passed') || line.includes('SUCCESS')) {
              textColor = 'text-emerald-400 font-semibold';
            } else if (line.includes('FAILED') || line.includes('failed') || line.includes('ERROR') || line.includes('Error')) {
              textColor = 'text-rose-400 font-semibold';
            } else if (line.startsWith('$') || line.includes('pytest') || line.includes('git')) {
              textColor = 'text-cyan-300 font-bold';
            } else if (line.includes('===') || line.includes('---')) {
              textColor = 'text-indigo-400';
            }

            return (
              <div key={idx} className={`whitespace-pre-wrap leading-relaxed ${textColor}`}>
                {line}
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
