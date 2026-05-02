import React, { useState } from 'react';
import JobDetail from './JobDetail';
import { ExternalLink, Building2, MapPin, DollarSign, Calendar, Info, ArrowUpDown, TrendingUp } from 'lucide-react';

const SOURCE_COLORS = {
  servir: 'bg-red-100 text-red-700 border-red-200',
  computrabajo: 'bg-blue-100 text-blue-700 border-blue-200',
  bumeran: 'bg-purple-100 text-purple-700 border-purple-200',
  laborum: 'bg-green-100 text-green-700 border-green-200',
  indeed: 'bg-sky-100 text-sky-800 border-sky-200',
  getonboard: 'bg-orange-100 text-orange-700 border-orange-200',
  jooble: 'bg-cyan-100 text-cyan-700 border-cyan-200',
  infojobs: 'bg-pink-100 text-pink-700 border-pink-200',
  opcionempleo: 'bg-amber-100 text-amber-700 border-amber-200',
};

const SOURCE_DOTS = {
  servir: 'bg-red-500',
  computrabajo: 'bg-blue-500',
  bumeran: 'bg-purple-500',
  laborum: 'bg-green-500',
  indeed: 'bg-sky-700',
  getonboard: 'bg-orange-500',
  jooble: 'bg-cyan-500',
  infojobs: 'bg-pink-600',
  opcionempleo: 'bg-amber-500',
};

const MODALITY_BADGES = {
  remoto: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  híbrido: 'bg-blue-50 text-blue-700 border border-blue-200',
  presencial: 'bg-slate-100 text-slate-600 border border-slate-200',
};

const JobTable = ({ jobs, isLoading }) => {
  const [selectedJob, setSelectedJob] = useState(null);
  const [sortBy, setSortBy] = useState('recent'); // 'recent' | 'salary_desc' | 'salary_asc'

  if (isLoading) {
    return (
      <div className="w-full flex flex-col items-center justify-center py-20 gap-4">
        <div className="relative w-14 h-14">
          <div className="absolute inset-0 rounded-full border-4 border-slate-100" />
          <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
        </div>
        <div className="text-center">
          <p className="text-slate-700 font-semibold">Rastreando 9 portales en tiempo real...</p>
          <p className="text-slate-400 text-sm mt-1">Esto puede tomar entre 15 y 45 segundos</p>
        </div>
        {/* Skeleton rows */}
        <div className="w-full max-w-4xl px-6 space-y-3 mt-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gradient-to-r from-slate-100 to-slate-50 rounded-xl animate-pulse" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      </div>
    );
  }

  if (!jobs || jobs.length === 0) {
    return (
      <div className="w-full text-center py-20 px-4">
        <div className="bg-slate-50 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-slate-200">
          <Info className="w-8 h-8 text-slate-400" />
        </div>
        <h3 className="text-lg font-bold text-slate-700 mb-2">No se encontraron resultados</h3>
        <p className="text-slate-400 text-sm max-w-md mx-auto">
          Prueba con otra palabra clave o ajusta los filtros. Los portales son consultados en tiempo real.
        </p>
      </div>
    );
  }

  // Sort jobs
  const sorted = [...jobs].sort((a, b) => {
    if (sortBy === 'salary_desc') {
      return (b.salary_max || b.salary_min || 0) - (a.salary_max || a.salary_min || 0);
    }
    if (sortBy === 'salary_asc') {
      const aVal = (a.salary_min || a.salary_max || 0);
      const bVal = (b.salary_min || b.salary_max || 0);
      return aVal === 0 ? 1 : bVal === 0 ? -1 : aVal - bVal;
    }
    // Default: most recent
    return new Date(b.scraped_at || 0) - new Date(a.scraped_at || 0);
  });

  const formatSalary = (job) => {
    if (job.salary_raw) return job.salary_raw;
    if (job.salary_min && job.salary_max) {
      const curr = job.salary_currency === 'USD' ? 'USD' : 'S/';
      return `${curr} ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}`;
    }
    if (job.salary_min) return `Desde S/ ${job.salary_min.toLocaleString()}`;
    return null;
  };

  const formatDate = (job) => {
    if (job.publication_date_raw) return job.publication_date_raw;
    if (job.scraped_at) {
      const d = new Date(job.scraped_at);
      const now = new Date();
      const diffH = Math.floor((now - d) / 3600000);
      if (diffH < 1) return 'Hace menos de 1h';
      if (diffH < 24) return `Hace ${diffH}h`;
      const diffD = Math.floor(diffH / 24);
      return `Hace ${diffD}d`;
    }
    return 'Reciente';
  };

  return (
    <>
      {/* Sort controls */}
      <div className="px-6 py-3 flex items-center gap-3 border-b border-slate-50 bg-slate-50/50">
        <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
          <ArrowUpDown size={12} /> Ordenar:
        </span>
        {[
          { value: 'recent', label: 'Más recientes' },
          { value: 'salary_desc', label: 'Mayor salario' },
          { value: 'salary_asc', label: 'Menor salario' },
        ].map(opt => (
          <button
            key={opt.value}
            onClick={() => setSortBy(opt.value)}
            className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-all ${
              sortBy === opt.value
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-500 hover:bg-slate-200'
            }`}
          >
            {opt.label}
          </button>
        ))}
        <span className="ml-auto text-xs text-slate-400 font-medium">{jobs.length} resultados</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[860px]">
          <thead>
            <tr className="border-b border-slate-100 text-xs uppercase tracking-wider text-slate-400 bg-slate-50/70">
              <th className="font-semibold py-3 px-5">Oferta Laboral</th>
              <th className="font-semibold py-3 px-4">Ubicación</th>
              <th className="font-semibold py-3 px-4">Modalidad</th>
              <th className="font-semibold py-3 px-4">Salario</th>
              <th className="font-semibold py-3 px-4">Fuente</th>
              <th className="font-semibold py-3 px-4 text-right">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {sorted.map((job) => {
              const salary = formatSalary(job);
              const date = formatDate(job);
              const sourceKey = job.source?.toLowerCase() || 'unknown';
              const sourceBadge = SOURCE_COLORS[sourceKey] || 'bg-slate-100 text-slate-600 border-slate-200';
              const sourceDot = SOURCE_DOTS[sourceKey] || 'bg-slate-400';
              const modalityBadge = MODALITY_BADGES[job.modality?.toLowerCase()] || '';

              return (
                <tr
                  key={job.id || Math.random().toString()}
                  className="hover:bg-blue-50/30 transition-colors group cursor-pointer"
                  onClick={() => setSelectedJob(job)}
                >
                  {/* Title & Company */}
                  <td className="py-4 px-5 max-w-xs">
                    <div className="font-semibold text-slate-800 mb-1 group-hover:text-blue-600 transition-colors text-sm leading-snug truncate">
                      {job.title}
                    </div>
                    <div className="flex items-center text-xs text-slate-500">
                      <Building2 className="w-3 h-3 mr-1.5 flex-shrink-0" />
                      <span className="truncate max-w-[180px]">{job.company || 'Confidencial'}</span>
                    </div>
                    {/* Skills chips */}
                    {Array.isArray(job.skills_detected) && job.skills_detected.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {job.skills_detected.slice(0, 3).map(skill => (
                          <span key={skill} className="text-xs bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded font-medium border border-indigo-100">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>

                  {/* Location */}
                  <td className="py-4 px-4">
                    <div className="flex items-start text-xs text-slate-600 gap-1">
                      <MapPin className="w-3.5 h-3.5 mt-0.5 text-slate-400 flex-shrink-0" />
                      <span className="leading-snug max-w-[130px]">{job.location_raw || 'Perú'}</span>
                    </div>
                  </td>

                  {/* Modality */}
                  <td className="py-4 px-4">
                    {job.modality && job.modality !== 'no especificado' ? (
                      <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-1 rounded-lg capitalize ${modalityBadge}`}>
                        {job.modality}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-300">—</span>
                    )}
                  </td>

                  {/* Salary */}
                  <td className="py-4 px-4">
                    {salary ? (
                      <div className="flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-lg px-2.5 py-1.5 gap-1 w-max max-w-[150px] leading-tight">
                        <DollarSign className="w-3 h-3 flex-shrink-0" />
                        <span className="truncate">{salary}</span>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-300">No especificado</span>
                    )}
                  </td>

                  {/* Source */}
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border capitalize ${sourceBadge}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${sourceDot}`} />
                      {job.source}
                    </span>
                  </td>

                  {/* Action */}
                  <td className="py-4 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <span className="text-xs text-slate-400 hidden md:flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {date}
                      </span>
                      <a
                        href={job.original_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        onClick={(e) => e.stopPropagation()}
                        title="Ver en portal original"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {selectedJob && (
        <JobDetail job={selectedJob} onClose={() => setSelectedJob(null)} />
      )}
    </>
  );
};

export default JobTable;
