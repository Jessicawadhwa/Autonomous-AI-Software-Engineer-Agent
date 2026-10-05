import React, { useState, useEffect } from 'react';
import { ViewMode, Project, DashboardStats } from './types';
import { projectApi } from './services/api';
import { Navbar } from './components/layout/Navbar';
import { DashboardView } from './components/dashboard/DashboardView';
import { NewProjectWizard } from './components/wizard/NewProjectWizard';
import { IDEWorkspace } from './components/ide/IDEWorkspace';
import { SettingsView } from './components/settings/SettingsView';
import { MCPView } from './components/mcp/MCPView';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewMode>('dashboard');
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats>({
    total_projects: 0,
    successful_builds: 0,
    failed_builds: 0,
    average_build_time_seconds: 0,
    total_tests_passed: 0,
    total_agent_runs: 0
  });

  const loadProjectsAndStats = async () => {
    try {
      const [projList, statsData] = await Promise.all([
        projectApi.list(),
        projectApi.getStats()
      ]);
      setProjects(projList);
      setStats(statsData);

      // Default active project if none selected
      if (!activeProjectId && projList.length > 0) {
        setActiveProjectId(projList[0].id);
      }
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  useEffect(() => {
    loadProjectsAndStats();
  }, [currentView]);

  const handleOpenProject = (id: string) => {
    setActiveProjectId(id);
    setCurrentView('ide');
  };

  const handleCreateProject = async (data: {
    name: string;
    description?: string;
    requirement: string;
    options: Record<string, any>;
    provider?: string;
    api_key?: string;
    model?: string;
  }) => {
    const newProj = await projectApi.create(data);
    setActiveProjectId(newProj.id);
    setCurrentView('ide');
    // Start agent run automatically
    await projectApi.startRun(newProj.id, {
      provider: data.provider || 'demo',
      api_key: data.api_key,
      model: data.model
    });
  };

  const handleLaunchDemo = async () => {
    const demoPayload = {
      name: `FastAPI-Employee-Service-${Math.floor(1000 + Math.random() * 9000)}`,
      description: "FastAPI REST API with CRUD, SQLite, Pytest & Docs (Demo)",
      requirement: "Build a FastAPI REST API for an employee management system with CRUD operations, SQLite database, authentication, unit tests, and API documentation.",
      options: {
        generate_tests: true,
        generate_docs: true,
        initialize_git: true,
        run_code_review: true,
        enable_mcp: true,
        auto_approve: true
      },
      provider: "demo"
    };

    const newProj = await projectApi.create(demoPayload);
    setActiveProjectId(newProj.id);
    setCurrentView('ide');
    await projectApi.startRun(newProj.id, { provider: 'demo' });
  };

  const handleDeleteProject = async (id: string) => {
    await projectApi.delete(id);
    if (activeProjectId === id) {
      setActiveProjectId(null);
    }
    await loadProjectsAndStats();
  };

  const handleRunProject = async (id: string) => {
    setActiveProjectId(id);
    setCurrentView('ide');
    await projectApi.startRun(id, { provider: 'demo' });
  };

  const activeProject = projects.find((p) => p.id === activeProjectId);

  return (
    <div className="h-screen w-screen flex flex-col bg-[#090d16] text-[#f1f5f9] overflow-hidden">
      <Navbar
        currentView={currentView}
        onSelectView={setCurrentView}
        activeProjectName={activeProject?.name}
        onLaunchDemo={handleLaunchDemo}
      />

      <main className="flex-1 flex overflow-hidden">
        {currentView === 'dashboard' && (
          <DashboardView
            projects={projects}
            stats={stats}
            onOpenProject={handleOpenProject}
            onCreateNew={() => setCurrentView('wizard')}
            onLaunchDemo={handleLaunchDemo}
            onDeleteProject={handleDeleteProject}
            onRunProject={handleRunProject}
          />
        )}

        {currentView === 'wizard' && (
          <NewProjectWizard
            onCreate={handleCreateProject}
            onCancel={() => setCurrentView('dashboard')}
            onLaunchDemo={handleLaunchDemo}
          />
        )}

        {currentView === 'ide' && activeProjectId && (
          <IDEWorkspace
            projectId={activeProjectId}
            onBackToDashboard={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'ide' && !activeProjectId && (
          <div className="flex-1 flex flex-col items-center justify-center space-y-4">
            <div className="text-slate-400 text-sm font-medium">No project currently selected in IDE</div>
            <button
              onClick={() => setCurrentView('wizard')}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-lg"
            >
              + Create a Project
            </button>
          </div>
        )}

        {currentView === 'settings' && <SettingsView />}

        {currentView === 'mcp' && <MCPView />}
      </main>
    </div>
  );
};

export default App;
