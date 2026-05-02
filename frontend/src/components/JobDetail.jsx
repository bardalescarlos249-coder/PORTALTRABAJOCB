import React from 'react';
import { X, Building2, MapPin, DollarSign, Calendar, ExternalLink, Briefcase, Tag, Clock } from 'lucide-react';

const JobDetail = ({ job, onClose }) => {
  if (!job) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm sm:p-6">
      <div 
        className="bg-apple-surface w-full max-w-3xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-apple-border/50 bg-gray-50/50">
          <div className="pr-8">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-apple-text leading-tight">{job.title}</h2>
              <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-gray-200 text-gray-700 capitalize">
                {job.source}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-apple-textMuted text-sm font-medium">
              <span className="flex items-center"><Building2 className="w-4 h-4 mr-1.5" /> {job.company || 'Confidencial'}</span>
              <span className="flex items-center"><MapPin className="w-4 h-4 mr-1.5" /> {job.location_raw || 'Perú'}</span>
              <span className="flex items-center text-green-600 bg-green-50 px-2 rounded-md"><DollarSign className="w-4 h-4 mr-1" /> {job.salary_raw || 'No especificado'}</span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 -m-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
              <span className="text-xs text-apple-textMuted uppercase font-semibold flex items-center mb-1"><Briefcase className="w-3.5 h-3.5 mr-1" /> Nivel</span>
              <p className="font-medium text-apple-text capitalize">{job.seniority || 'No especificado'}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
              <span className="text-xs text-apple-textMuted uppercase font-semibold flex items-center mb-1"><Clock className="w-3.5 h-3.5 mr-1" /> Modalidad</span>
              <p className="font-medium text-apple-text capitalize">{job.modality || 'No especificado'}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
              <span className="text-xs text-apple-textMuted uppercase font-semibold flex items-center mb-1"><Tag className="w-3.5 h-3.5 mr-1" /> Jornada</span>
              <p className="font-medium text-apple-text capitalize">{job.job_type || 'No especificado'}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
              <span className="text-xs text-apple-textMuted uppercase font-semibold flex items-center mb-1"><Calendar className="w-3.5 h-3.5 mr-1" /> Publicado</span>
              <p className="font-medium text-apple-text">{job.publication_date_raw || 'Reciente'}</p>
            </div>
          </div>

          <div className="space-y-6">
            {job.description && (
              <section>
                <h3 className="text-lg font-semibold text-apple-text mb-3">Descripción del puesto</h3>
                <div className="text-apple-textMuted text-sm leading-relaxed whitespace-pre-wrap">
                  {job.description}
                </div>
              </section>
            )}

            {job.requirements && (
              <section>
                <h3 className="text-lg font-semibold text-apple-text mb-3">Requisitos</h3>
                <div className="text-apple-textMuted text-sm leading-relaxed whitespace-pre-wrap bg-yellow-50/50 p-4 rounded-xl border border-yellow-100/50">
                  {job.requirements}
                </div>
              </section>
            )}

            {job.skills_detected && job.skills_detected.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-apple-text mb-3">Habilidades / Herramientas detectadas</h3>
                <div className="flex flex-wrap gap-2">
                  {job.skills_detected.map(skill => (
                    <span key={skill} className="px-3 py-1 bg-blue-50 text-blue-700 text-sm font-medium rounded-lg border border-blue-100">
                      {skill}
                    </span>
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-apple-border/50 bg-gray-50/50 flex justify-end">
          <button onClick={onClose} className="apple-btn-secondary mr-3">
            Cerrar
          </button>
          <a 
            href={job.original_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="apple-btn-primary"
          >
            Ver oferta original <ExternalLink className="w-4 h-4 ml-2" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default JobDetail;
