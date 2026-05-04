import React, { useState, useEffect, useCallback } from 'react';
import SearchBar from './components/SearchBar';
import JobTable from './components/JobTable';
import SourceTabs from './components/SourceTabs';
import { Briefcase, Building2, MapPin, TrendingUp, RefreshCw, Download, Zap } from 'lucide-react';
import { apiBase } from './api/client';

const ALL_SOURCES = [
  "servir", "computrabajo", "bumeran", "laborum",
  "indeed", "getonboard", "jooble", "infojobs", "opcionempleo"
];

import AlertsManager from './components/AlertsManager';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('todos');
  const [activeView, setActiveView] = useState('buscador'); // buscador, analytics, alertas
  const [stats, setStats] = useState({ total: 0, sources: 0, unique_companies: 0 });
  const [lastSearch, setLastSearch] = useState(null);
  const [searchStatus, setSearchStatus] = useState('');
  const [scrapingProgress, setScrapingProgress] = useState(0);

  const handleSearch = useCallback(async (filters) => {
    setLoading(true);
    setActiveTab('todos');
    setSearchStatus('Iniciando búsqueda en 9 portales (puede tomar un minuto)...');
    setScrapingProgress(5);

    try {
      // 1. Start Async Search
      const startRes = await fetch(`${apiBase}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: filters.keyword || "",
          location: filters.location || "",
          modality: filters.modality || "",
          job_type: filters.job_type || "",
          seniority: filters.seniority || "",
          career_area: filters.career_area || "",
          sector: filters.sector || "",
          salary_min: filters.salary_min ? parseFloat(filters.salary_min) : null,
          salary_max: filters.salary_max ? parseFloat(filters.salary_max) : null,
          sources: ALL_SOURCES,
          max_pages: 1,
        })
      });
      
      if (!startRes.ok) throw new Error('Failed to start search');
      const runData = await startRes.json();
      const runId = runData.id;

      // 2. Poll for completion
      let isCompleted = false;
      let progress = 10;
      while (!isCompleted) {
        await new Promise(resolve => setTimeout(resolve, 3000)); // Poll every 3s
        progress = Math.min(progress + 5, 90);
        setScrapingProgress(progress);
        
        try {
          const pollRes = await fetch(`${apiBase}/api/search/runs/${runId}`);
          if (pollRes.ok) {
            const statusData = await pollRes.json();
            if (statusData.status === 'completed' || statusData.status === 'failed') {
              isCompleted = true;
            }
          }
        } catch (pollErr) {
          console.warn("Polling error:", pollErr);
          // Keep polling, might be a temporary network hiccup
        }
      }

      setScrapingProgress(95);
      setSearchStatus('Normalizando y filtrando resultados...');

      // 3. Fetch filtered results from DB
      const params = new URLSearchParams();
      if (filters.keyword) params.append('keyword', filters.keyword);
      if (filters.location) params.append('location', filters.location);
      if (filters.modality) params.append('modality', filters.modality);
      if (filters.job_type) params.append('job_type', filters.job_type);
      if (filters.seniority) params.append('seniority', filters.seniority);
      if (filters.career_area) params.append('career_area', filters.career_area);
      if (filters.sector) params.append('sector', filters.sector);
      if (filters.salary_min) params.append('salary_min', filters.salary_min);
      if (filters.salary_max) params.append('salary_max', filters.salary_max);
      params.append('page_size', '200');

      const res = await fetch(`${apiBase}/api/jobs?${params.toString()}`);
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      const items = data.items || data || [];

      setJobs(items);
      setLastSearch(filters);
      setStats({
        total: items.length,
        sources: new Set(items.map(j => j.source)).size,
        unique_companies: new Set(items.map(j => j.company).filter(Boolean)).size,
      });
      setScrapingProgress(100);
      setSearchStatus(`✓ ${items.length} ofertas encontradas en ${new Set(items.map(j => j.source)).size} portales`);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setSearchStatus('Error al buscar. Cargando últimos datos de la base de datos...');
      
      // Fallback: try loading from DB anyway
      try {
        const fallbackRes = await fetch(`${apiBase}/api/jobs?page_size=100`);
        const fallbackData = await fallbackRes.json();
        const items = fallbackData.items || fallbackData || [];
        setJobs(items);
      } catch(e) {}
    } finally {
      setLoading(false);
      setTimeout(() => setScrapingProgress(0), 1000);
    }
  }, []);

  useEffect(() => {
    handleSearch({ keyword: '' });
  }, []);

  // Filter jobs by active tab
  const displayedJobs = activeTab === 'todos'
    ? jobs
    : jobs.filter(j => j.source?.toLowerCase() === activeTab);

  const handleExport = async () => {
    try {
      const params = lastSearch ? new URLSearchParams(
        Object.entries(lastSearch).filter(([, v]) => v).map(([k, v]) => [k, String(v)])
      ).toString() : '';
      window.open(`${apiBase}/api/export/excel?${params}`, '_blank');
    } catch (e) {
      console.error('Export error:', e);
    }
  };

  const sourceColors = {
    servir: '#dc2626',
    computrabajo: '#2563eb',
    bumeran: '#7c3aed',
    laborum: '#16a34a',
    indeed: '#0f4c75',
    getonboard: '#ea580c',
    jooble: '#0891b2',
    infojobs: '#be185d',
    opcionempleo: '#ca8a04',
  };

  // Count jobs per source
  const sourceCounts = jobs.reduce((acc, job) => {
    const src = job.source?.toLowerCase() || 'unknown';
    acc[src] = (acc[src] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl sticky top-0 z-50 border-b border-slate-200/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
              <Zap size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900">Antigravity Jobs</h1>
              <p className="text-xs text-slate-500 font-medium">Inteligencia Laboral del Perú</p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-6">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
              {ALL_SOURCES.length} portales activos
            </div>
            <nav className="flex space-x-5 text-sm font-medium text-slate-500">
              <button onClick={() => setActiveView('buscador')} className={`${activeView === 'buscador' ? 'text-slate-900 font-semibold' : 'hover:text-slate-900'} transition-colors`}>Buscador</button>
              <button onClick={() => setActiveView('alertas')} className={`${activeView === 'alertas' ? 'text-slate-900 font-semibold' : 'hover:text-slate-900'} transition-colors`}>Alertas (Correos)</button>
              <a href="#" className="hover:text-slate-900 transition-colors">Analytics</a>
            </nav>
          </div>
        </div>

        {/* Progress bar */}
        {scrapingProgress > 0 && scrapingProgress < 100 && (
          <div className="h-0.5 bg-slate-100">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
              style={{ width: `${scrapingProgress}%` }}
            />
          </div>
        )}
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {activeView === 'alertas' ? (
          <AlertsManager />
        ) : (
          <>
            {/* Hero Search */}
            <section className="text-center py-10">
              <div className="inline-flex items-center gap-2 text-xs font-semibold text-blue-600 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-full mb-5">
                <Zap size={12} />
                Búsqueda asíncrona · 9 portales simultáneos
              </div>
              <h2 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-900 mb-3">
                Encuentra tu próxima
                <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> oportunidad</span>
              </h2>
              <p className="text-base text-slate-500 max-w-2xl mx-auto mb-8">
                Rastreamos en tiempo real Servir, Computrabajo, Bumeran, Laborum, Indeed, GetOnBoard, Jooble, InfoJobs y OpcionEmpleo.
              </p>
              <div className="max-w-5xl mx-auto text-left">
                <SearchBar onSearch={handleSearch} isLoading={loading} />
              </div>

              {/* Search Status */}
              {searchStatus && (
                <div className={`mt-4 text-sm font-medium transition-all ${loading ? 'text-blue-600' : 'text-emerald-600'}`}>
                  {loading && <RefreshCw size={13} className="inline mr-1.5 animate-spin" />}
                  {searchStatus}
                </div>
              )}
            </section>

            {/* Stats */}
            <section className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { icon: Briefcase, label: 'Ofertas encontradas', value: stats.total, color: 'blue', bg: 'from-blue-500 to-indigo-500' },
                { icon: Building2, label: 'Portales consultados', value: stats.sources, color: 'purple', bg: 'from-purple-500 to-pink-500' },
                { icon: TrendingUp, label: 'Empresas únicas', value: stats.unique_companies, color: 'emerald', bg: 'from-emerald-500 to-teal-500' },
              ].map(({ icon: Icon, label, value, color, bg }) => (
                <div key={label} className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm flex items-center gap-4">
                  <div className={`w-11 h-11 bg-gradient-to-br ${bg} rounded-xl flex items-center justify-center shadow-md flex-shrink-0`}>
                    <Icon size={20} className="text-white" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">{value}</p>
                    <p className="text-xs text-slate-500 font-medium">{label}</p>
                  </div>
                </div>
              ))}
            </section>

            {/* Results Panel */}
            <section className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              {/* Panel Header */}
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-wrap gap-3">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Resultados de búsqueda</h3>
                  {activeTab !== 'todos' && (
                    <p className="text-xs text-slate-500 mt-0.5">
                      Mostrando {displayedJobs.length} de {jobs.length} ofertas • Fuente: <span className="font-semibold capitalize">{activeTab}</span>
                    </p>
                  )}
                </div>
                <button
                  onClick={handleExport}
                  className="flex items-center gap-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-4 py-2 rounded-xl shadow-sm transition-all"
                >
                  <Download size={14} />
                  Exportar Excel
                </button>
              </div>

              {/* Source Tabs */}
              <SourceTabs
                jobs={jobs}
                activeTab={activeTab}
                onTabChange={setActiveTab}
                sourceCounts={sourceCounts}
                sourceColors={sourceColors}
              />

              {/* Job Table */}
              <JobTable jobs={displayedJobs} isLoading={loading} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
