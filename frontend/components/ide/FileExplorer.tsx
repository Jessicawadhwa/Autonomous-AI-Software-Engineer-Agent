import React, { useState } from 'react';
import { FileNode } from '../../types';
import { 
  Folder, 
  FolderOpen, 
  FileCode, 
  FileText, 
  FileJson, 
  File, 
  ChevronRight, 
  ChevronDown, 
  Search,
  RefreshCw
} from 'lucide-react';

interface FileExplorerProps {
  tree: FileNode[];
  selectedFile: string | null;
  onSelectFile: (path: string) => void;
  onRefresh: () => void;
}

const getFileIcon = (filename: string) => {
  if (filename.endsWith('.py')) return <FileCode className="w-4 h-4 text-emerald-400 shrink-0" />;
  if (filename.endsWith('.md')) return <FileText className="w-4 h-4 text-cyan-400 shrink-0" />;
  if (filename.endsWith('.json')) return <FileJson className="w-4 h-4 text-amber-400 shrink-0" />;
  if (filename.endsWith('.txt') || filename.startsWith('.')) return <File className="w-4 h-4 text-slate-400 shrink-0" />;
  return <File className="w-4 h-4 text-indigo-400 shrink-0" />;
};

const FileTreeNode: React.FC<{
  node: FileNode;
  selectedFile: string | null;
  onSelectFile: (path: string) => void;
  depth?: number;
}> = ({ node, selectedFile, onSelectFile, depth = 0 }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (node.type === 'directory') {
    return (
      <div>
        <div
          onClick={() => setIsOpen(!isOpen)}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          className="flex items-center gap-1.5 py-1 px-2 text-xs font-medium text-slate-300 hover:bg-slate-800/60 rounded cursor-pointer transition-colors group select-none"
        >
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300" />
          )}
          {isOpen ? (
            <FolderOpen className="w-4 h-4 text-amber-400 shrink-0" />
          ) : (
            <Folder className="w-4 h-4 text-amber-400 shrink-0" />
          )}
          <span className="truncate">{node.name}</span>
        </div>

        {isOpen && node.children && (
          <div>
            {node.children.map((child) => (
              <FileTreeNode
                key={child.path}
                node={child}
                selectedFile={selectedFile}
                onSelectFile={onSelectFile}
                depth={depth + 1}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  const isSelected = selectedFile === node.path;

  return (
    <div
      onClick={() => onSelectFile(node.path)}
      style={{ paddingLeft: `${depth * 12 + 20}px` }}
      className={`flex items-center gap-1.5 py-1 px-2 text-xs rounded cursor-pointer transition-colors group select-none ${
        isSelected
          ? 'bg-indigo-600/30 text-indigo-200 border-l-2 border-indigo-500 font-medium'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
      }`}
    >
      {getFileIcon(node.name)}
      <span className="truncate">{node.name}</span>
    </div>
  );
};

export const FileExplorer: React.FC<FileExplorerProps> = ({
  tree,
  selectedFile,
  onSelectFile,
  onRefresh
}) => {
  const [filter, setFilter] = useState('');

  const filterTree = (nodes: FileNode[], query: string): FileNode[] => {
    if (!query.trim()) return nodes;
    const res: FileNode[] = [];
    for (const n of nodes) {
      if (n.type === 'directory' && n.children) {
        const filteredChildren = filterTree(n.children, query);
        if (filteredChildren.length > 0 || n.name.toLowerCase().includes(query.toLowerCase())) {
          res.push({ ...n, children: filteredChildren });
        }
      } else if (n.name.toLowerCase().includes(query.toLowerCase())) {
        res.push(n);
      }
    }
    return res;
  };

  const displayedTree = filterTree(tree, filter);

  return (
    <div className="h-full flex flex-col bg-[#0d1322] select-none">
      {/* Header */}
      <div className="h-9 px-3 border-b border-slate-800 flex items-center justify-between text-xs font-semibold text-slate-400">
        <span className="uppercase tracking-wider text-[10px]">Explorer</span>
        <button
          onClick={onRefresh}
          title="Refresh Workspace"
          className="p-1 hover:text-slate-200 rounded hover:bg-slate-800/60 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Filter Input */}
      <div className="p-2 border-b border-slate-800/60">
        <div className="relative">
          <Search className="w-3 h-3 text-slate-500 absolute left-2.5 top-2.5" />
          <input
            type="text"
            placeholder="Search files..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full bg-[#090d16] border border-slate-800 rounded-lg pl-7 pr-2 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>
      </div>

      {/* File Tree List */}
      <div className="flex-1 overflow-y-auto p-1.5 space-y-0.5">
        {displayedTree.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-500">
            No files in workspace
          </div>
        ) : (
          displayedTree.map((node) => (
            <FileTreeNode
              key={node.path}
              node={node}
              selectedFile={selectedFile}
              onSelectFile={onSelectFile}
            />
          ))
        )}
      </div>
    </div>
  );
};
