import React, { useState } from 'react';
import { Search, MapPin, Briefcase, ChevronDown, ChevronUp, SlidersHorizontal, X, DollarSign } from 'lucide-react';

const MODALITIES = ['', 'presencial', 'remoto', 'híbrido'];
const JOB_TYPES = ['', 'CAS', 'Planilla 728', 'Practicante', 'Part-time', 'Freelance'];
const SENIORITIES = ['', 'Junior', 'Semi-senior', 'Senior', 'Lead', 'Manager'];
const CAREER_AREAS = [
  '', 'Tecnología', 'Administración', 'Contabilidad y Finanzas', 'Marketing y Ventas',
  'Recursos Humanos', 'Ingeniería', 'Minería', 'Salud', 'Educación', 'Legal',
  'Logística y Supply Chain', 'Diseño', 'Gastronomía', 'Construcción',
];
const SECTORS = ['', 'Privado', 'Público', 'ONG / Sin fines de lucro', 'Internacional'];

const SearchBar = ({ onSearch, isLoading }) => {
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [filters, setFilters] = useState({
    modality: '',
    job_type: '',
    seniority: '',
    career_area: '',
    sector: '',
    salary_min: '',
    salary_max: '',
  });

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ keyword, location, ...filters });
  };

  const clearFilters = () => {
    setFilters({ modality: '', job_type: '', seniority: '', career_area: '', sector: '', salary_min: '', salary_max: '' });
    setLocation('');
  };

  const activeFilterCount = Object.values(filters).filter(v => v !== '').length + (location ? 1 : 0);

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200/80 overflow-hidden">
      {/* Main search row */}
      <form onSubmit={handleSubmit}>
        <div className="flex flex-col md:flex-row gap-0 divide-y md:divide-y-0 md:divide-x divide-slate-100">
          {/* Keyword */}
          <div className="flex-1 flex items-center px-5 py-3.5">
            <Search className="w-5 h-5 text-slate-400 mr-3 flex-shrink-0" />
            <input
              id="search-keyword"
              type="text"
              placeholder="Cargo, habilidad o empresa (ej: Excel, Python, Enfermera)..."
              className="bg-transparent w-full outline-none text-slate-800 placeholder-slate-400 text-sm"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>

          {/* Location */}
          <div className="md:w-56 flex items-center px-5 py-3.5">
            <MapPin className="w-5 h-5 text-slate-400 mr-3 flex-shrink-0" />
            <input
              id="search-location"
              type="text"
              placeholder="Lima, Arequipa, Cusco..."
              className="bg-transparent w-full outline-none text-slate-800 placeholder-slate-400 text-sm"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>

          {/* Modality quick select */}
          <div className="md:w-44 flex items-center px-5 py-3.5">
            <Briefcase className="w-5 h-5 text-slate-400 mr-3 flex-shrink-0" />
            <select
              id="search-modality"
              className="bg-transparent w-full outline-none text-slate-700 cursor-pointer appearance-none text-sm"
              value={filters.modality}
              onChange={(e) => updateFilter('modality', e.target.value)}
            >
              <option value="">Modalidad</option>
              <option value="presencial">Presencial</option>
              <option value="remoto">Remoto</option>
              <option value="híbrido">Híbrido</option>
            </select>
          </div>

          {/* Search button */}
          <div className="flex items-center p-2.5 bg-gradient-to-br from-blue-600 to-indigo-600">
            <button
              type="submit"
              disabled={isLoading}
              id="btn-search"
              className="w-full md:w-36 h-11 flex items-center justify-center gap-2 text-white font-bold text-sm rounded-xl transition-all hover:opacity-90 disabled:opacity-70"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Search size={16} />
                  Buscar
                </>
              )}
            </button>
          </div>
        </div>

        {/* Advanced filters toggle */}
        <div className="border-t border-slate-100 px-5 py-2.5 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            <SlidersHorizontal size={15} />
            Filtros avanzados
            {activeFilterCount > 0 && (
              <span className="bg-blue-600 text-white text-xs font-bold px-1.5 py-0.5 rounded-full leading-none">
                {activeFilterCount}
              </span>
            )}
            {showAdvanced ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          </button>

          {activeFilterCount > 0 && (
            <button
              type="button"
              onClick={clearFilters}
              className="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 font-medium transition-colors"
            >
              <X size={12} />
              Limpiar filtros
            </button>
          )}
        </div>

        {/* Advanced filters panel */}
        {showAdvanced && (
          <div className="border-t border-slate-100 px-5 py-4 bg-slate-50/50 grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Salary range */}
            <div className="col-span-2 md:col-span-1">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                <DollarSign size={11} className="inline mr-1" />
                Salario mínimo (S/)
              </label>
              <input
                id="filter-salary-min"
                type="number"
                placeholder="Ej: 2000"
                min="0"
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400 bg-white text-slate-700"
                value={filters.salary_min}
                onChange={(e) => updateFilter('salary_min', e.target.value)}
              />
            </div>

            <div className="col-span-2 md:col-span-1">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                <DollarSign size={11} className="inline mr-1" />
                Salario máximo (S/)
              </label>
              <input
                id="filter-salary-max"
                type="number"
                placeholder="Ej: 8000"
                min="0"
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400 bg-white text-slate-700"
                value={filters.salary_max}
                onChange={(e) => updateFilter('salary_max', e.target.value)}
              />
            </div>

            {/* Job type */}
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Tipo de contrato
              </label>
              <select
                id="filter-job-type"
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400 bg-white text-slate-700 cursor-pointer"
                value={filters.job_type}
                onChange={(e) => updateFilter('job_type', e.target.value)}
              >
                {JOB_TYPES.map(v => (
                  <option key={v} value={v}>{v || 'Todos los contratos'}</option>
                ))}
              </select>
            </div>

            {/* Seniority */}
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Seniority / Nivel
              </label>
              <select
                id="filter-seniority"
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400 bg-white text-slate-700 cursor-pointer"
                value={filters.seniority}
                onChange={(e) => updateFilter('seniority', e.target.value)}
              >
                {SENIORITIES.map(v => (
                  <option key={v} value={v}>{v || 'Cualquier nivel'}</option>
                ))}
              </select>
            </div>

            {/* Career area */}
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Área profesional
              </label>
              <select
                id="filter-career-area"
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400 bg-white text-slate-700 cursor-pointer"
                value={filters.career_area}
                onChange={(e) => updateFilter('career_area', e.target.value)}
              >
                {CAREER_AREAS.map(v => (
                  <option key={v} value={v}>{v || 'Todas las áreas'}</option>
                ))}
              </select>
            </div>

            {/* Sector */}
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Sector
              </label>
              <select
                id="filter-sector"
                className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400 bg-white text-slate-700 cursor-pointer"
                value={filters.sector}
                onChange={(e) => updateFilter('sector', e.target.value)}
              >
                {SECTORS.map(v => (
                  <option key={v} value={v}>{v || 'Público y Privado'}</option>
                ))}
              </select>
            </div>

            {/* Active filter chips */}
            {activeFilterCount > 0 && (
              <div className="col-span-2 md:col-span-4 flex flex-wrap gap-2 pt-1">
                {Object.entries(filters).filter(([, v]) => v !== '').map(([key, value]) => (
                  <span
                    key={key}
                    className="flex items-center gap-1.5 bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold px-2.5 py-1 rounded-full"
                  >
                    {value}
                    <button type="button" onClick={() => updateFilter(key, '')} className="hover:text-blue-900">
                      <X size={11} />
                    </button>
                  </span>
                ))}
                {location && (
                  <span className="flex items-center gap-1.5 bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold px-2.5 py-1 rounded-full">
                    📍 {location}
                    <button type="button" onClick={() => setLocation('')} className="hover:text-blue-900">
                      <X size={11} />
                    </button>
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </form>
    </div>
  );
};

export default SearchBar;
