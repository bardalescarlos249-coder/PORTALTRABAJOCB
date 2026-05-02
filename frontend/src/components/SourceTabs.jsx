import React from 'react';

const SOURCE_LABELS = {
  servir: 'Servir',
  computrabajo: 'Computrabajo',
  bumeran: 'Bumeran',
  laborum: 'Laborum',
  indeed: 'Indeed',
  getonboard: 'GetOnBoard',
  jooble: 'Jooble',
  infojobs: 'InfoJobs',
  opcionempleo: 'OpcionEmpleo',
};

const SOURCE_COLORS = {
  servir: { dot: '#dc2626', badge: 'bg-red-100 text-red-700 border-red-200' },
  computrabajo: { dot: '#2563eb', badge: 'bg-blue-100 text-blue-700 border-blue-200' },
  bumeran: { dot: '#7c3aed', badge: 'bg-purple-100 text-purple-700 border-purple-200' },
  laborum: { dot: '#16a34a', badge: 'bg-green-100 text-green-700 border-green-200' },
  indeed: { dot: '#0f4c75', badge: 'bg-sky-100 text-sky-800 border-sky-200' },
  getonboard: { dot: '#ea580c', badge: 'bg-orange-100 text-orange-700 border-orange-200' },
  jooble: { dot: '#0891b2', badge: 'bg-cyan-100 text-cyan-700 border-cyan-200' },
  infojobs: { dot: '#be185d', badge: 'bg-pink-100 text-pink-700 border-pink-200' },
  opcionempleo: { dot: '#ca8a04', badge: 'bg-amber-100 text-amber-700 border-amber-200' },
};

const SourceTabs = ({ jobs, activeTab, onTabChange, sourceCounts }) => {
  const activeSources = Object.entries(sourceCounts)
    .filter(([, count]) => count > 0)
    .sort(([, a], [, b]) => b - a);

  return (
    <div className="border-b border-slate-100 overflow-x-auto">
      <div className="flex px-4 gap-1 min-w-max py-2">
        {/* "Todos" tab */}
        <button
          onClick={() => onTabChange('todos')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
            activeTab === 'todos'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Todos
          <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
            activeTab === 'todos' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
          }`}>
            {jobs.length}
          </span>
        </button>

        {/* Per-source tabs */}
        {activeSources.map(([source, count]) => {
          const isActive = activeTab === source;
          const colors = SOURCE_COLORS[source] || { dot: '#64748b', badge: 'bg-slate-100 text-slate-600 border-slate-200' };
          const label = SOURCE_LABELS[source] || source;

          return (
            <button
              key={source}
              onClick={() => onTabChange(source)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all whitespace-nowrap border ${
                isActive
                  ? `${colors.badge} border shadow-sm`
                  : 'text-slate-500 border-transparent hover:bg-slate-50'
              }`}
            >
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: colors.dot }}
              />
              {label}
              <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
                isActive ? 'bg-white/50' : 'bg-slate-100 text-slate-500'
              }`}>
                {count}
              </span>
            </button>
          );
        })}

        {/* Empty state for tabs if no data */}
        {activeSources.length === 0 && (
          <span className="text-xs text-slate-400 px-3 py-2 italic">
            Realiza una búsqueda para ver resultados por portal
          </span>
        )}
      </div>
    </div>
  );
};

export default SourceTabs;
export { SOURCE_COLORS, SOURCE_LABELS };
