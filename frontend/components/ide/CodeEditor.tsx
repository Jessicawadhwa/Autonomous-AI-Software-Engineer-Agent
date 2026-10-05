import React, { useState, useEffect } from 'react';
import Editor, { DiffEditor } from '@monaco-editor/react';
import { 
  Save, 
  FileCode, 
  GitCompare, 
  Code, 
  Copy, 
  Check, 
  Sparkles,
  Maximize2
} from 'lucide-react';

interface CodeEditorProps {
  filePath: string | null;
  content: string;
  originalContent?: string;
  onSave: (path: string, content: string) => Promise<void>;
  isLoading?: boolean;
}

const getLanguageFromPath = (path: string | null): string => {
  if (!path) return 'plaintext';
  if (path.endsWith('.py')) return 'python';
  if (path.endsWith('.json')) return 'json';
  if (path.endsWith('.md')) return 'markdown';
  if (path.endsWith('.js') || path.endsWith('.jsx')) return 'javascript';
  if (path.endsWith('.ts') || path.endsWith('.tsx')) return 'typescript';
  if (path.endsWith('.html')) return 'html';
  if (path.endsWith('.css')) return 'css';
  if (path.endsWith('.yml') || path.endsWith('.yaml')) return 'yaml';
  if (path.endsWith('.sh') || path.endsWith('.bat')) return 'shell';
  return 'plaintext';
};

export const CodeEditor: React.FC<CodeEditorProps> = ({
  filePath,
  content,
  originalContent,
  onSave,
  isLoading = false
}) => {
  const [editorValue, setEditorValue] = useState(content);
  const [isDiffMode, setIsDiffMode] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setEditorValue(content);
  }, [content, filePath]);

  const isDirty = editorValue !== content;
  const language = getLanguageFromPath(filePath);

  const handleSave = async () => {
    if (!filePath || isSaving) return;
    setIsSaving(true);
    try {
      await onSave(filePath, editorValue);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(editorValue);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!filePath) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-[#111827] text-slate-500 space-y-3 select-none">
        <div className="w-12 h-12 rounded-2xl bg-slate-800/80 flex items-center justify-center border border-slate-700/60">
          <FileCode className="w-6 h-6 text-slate-400" />
        </div>
        <div className="text-center">
          <div className="text-sm font-medium text-slate-300">No File Selected</div>
          <div className="text-xs text-slate-500 mt-1">Select a file from the explorer to view and edit</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e]">
      {/* Editor Top Bar */}
      <div className="h-10 bg-[#181818] border-b border-[#2d2d2d] px-4 flex items-center justify-between select-none">
        {/* File Path & Dirty Indicator */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <FileCode className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-300 font-semibold">{filePath}</span>
          {isDirty && (
            <span className="flex items-center gap-1 text-[11px] text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20 font-sans">
              ● modified
            </span>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {originalContent !== undefined && (
            <button
              onClick={() => setIsDiffMode(!isDiffMode)}
              className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-md transition-colors ${
                isDiffMode
                  ? 'bg-purple-600 text-white'
                  : 'text-slate-400 hover:text-slate-200 bg-[#252526] hover:bg-[#2f2f30]'
              }`}
              title="Toggle Diff Viewer"
            >
              <GitCompare className="w-3.5 h-3.5" />
              <span>{isDiffMode ? 'Editor View' : 'Diff View'}</span>
            </button>
          )}

          <button
            onClick={handleCopy}
            title="Copy file contents"
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded hover:bg-[#252526] transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={handleSave}
            disabled={!isDirty || isSaving}
            className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-md transition-all ${
              isDirty
                ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-500/30'
                : 'text-slate-500 bg-[#252526] cursor-not-allowed opacity-60'
            }`}
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Saving...' : 'Save'}</span>
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div className="flex-1 relative overflow-hidden">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[#1e1e1e]/80 backdrop-blur-sm z-10">
            <span className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></span>
          </div>
        ) : null}

        {isDiffMode && originalContent !== undefined ? (
          <DiffEditor
            height="100%"
            language={language}
            original={originalContent}
            modified={editorValue}
            theme="vs-dark"
            options={{
              readOnly: true,
              renderSideBySide: true,
              fontSize: 13,
              fontFamily: '"JetBrains Mono", Consolas, monospace',
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
            }}
          />
        ) : (
          <Editor
            height="100%"
            language={language}
            value={editorValue}
            onChange={(val) => setEditorValue(val || '')}
            theme="vs-dark"
            options={{
              fontSize: 13,
              fontFamily: '"JetBrains Mono", Consolas, monospace',
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              wordWrap: 'on',
              lineNumbers: 'on',
              cursorBlinking: 'smooth',
              smoothScrolling: true,
            }}
          />
        )}
      </div>
    </div>
  );
};
