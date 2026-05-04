import React, { useState, useEffect } from 'react';
import { Bell, Plus, Trash2, Edit2, Check, X, Save, RefreshCw } from 'lucide-react';
import { apiBase } from '../api/client';

export default function AlertsManager() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [statusMsg, setStatusMsg] = useState(null); // {type: 'success'|'error', text: '...'}

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    keyword: '',
    frequency: 'daily'
  });

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiBase}/api/subscriptions`);
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      } else {
        setStatusMsg({ type: 'error', text: `Error del servidor (${res.status}). Verifica que Render esté activo.` });
      }
    } catch (e) {
      setStatusMsg({ type: 'error', text: 'No se pudo conectar con el servidor. Puede estar iniciando (espera 1 min).' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setStatusMsg(null);
    try {
      const url = editingId
        ? `${apiBase}/api/subscriptions/${editingId}`
        : `${apiBase}/api/subscriptions`;

      const res = await fetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        setShowForm(false);
        setEditingId(null);
        setFormData({ name: '', email: '', keyword: '', frequency: 'daily' });
        setStatusMsg({ type: 'success', text: `✅ Alerta guardada correctamente para ${formData.email}` });
        fetchAlerts();
      } else {
        const errText = await res.text();
        setStatusMsg({ type: 'error', text: `Error al guardar (${res.status}): ${errText}` });
      }
    } catch (e) {
      setStatusMsg({ type: 'error', text: 'No se pudo conectar con el servidor. Intenta en 1 minuto.' });
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (alert) => {
    setFormData({
      name: alert.name,
      email: alert.email,
      keyword: alert.keyword,
      frequency: alert.frequency
    });
    setEditingId(alert.id);
    setShowForm(true);
    setStatusMsg(null);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("¿Seguro que deseas eliminar esta alerta?")) return;
    try {
      const res = await fetch(`${apiBase}/api/subscriptions/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setStatusMsg({ type: 'success', text: '🗑️ Alerta eliminada.' });
        fetchAlerts();
      }
    } catch (e) {
      setStatusMsg({ type: 'error', text: 'Error al eliminar.' });
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Bell size={20} className="text-blue-600" />
            Alertas Automáticas (Correos)
          </h2>
          <p className="text-sm text-slate-500 mt-1">Configura quién recibe las ofertas y qué buscan.</p>
        </div>
        
        {!showForm && (
          <button 
            onClick={() => {
              setFormData({ name: '', email: '', keyword: '', frequency: 'daily' });
              setEditingId(null);
              setShowForm(true);
              setStatusMsg(null);
            }}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
          >
            <Plus size={16} /> Nueva Alerta
          </button>
        )}
      </div>

      {/* Status Message Banner */}
      {statusMsg && (
        <div className={`mb-4 px-4 py-3 rounded-xl text-sm font-medium flex items-center justify-between ${
          statusMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          <span>{statusMsg.text}</span>
          <button onClick={() => setStatusMsg(null)} className="ml-3 opacity-60 hover:opacity-100">✕</button>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-slate-50 p-5 rounded-xl border border-slate-200 mb-6 animate-in fade-in slide-in-from-top-4">
          <h3 className="text-sm font-bold text-slate-800 mb-4">{editingId ? 'Editar Alerta' : 'Crear Nueva Alerta'}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Nombre Destinatario</label>
              <input required value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})} className="w-full text-sm border-slate-200 rounded-lg p-2.5 focus:ring-blue-500 focus:border-blue-500" placeholder="Ej: Carlos Bardales" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Correo Electrónico</label>
              <input required type="email" value={formData.email} onChange={e=>setFormData({...formData, email: e.target.value})} className="w-full text-sm border-slate-200 rounded-lg p-2.5 focus:ring-blue-500 focus:border-blue-500" placeholder="correo@empresa.com" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Puesto a Buscar (Keyword)</label>
              <input required value={formData.keyword} onChange={e=>setFormData({...formData, keyword: e.target.value})} className="w-full text-sm border-slate-200 rounded-lg p-2.5 focus:ring-blue-500 focus:border-blue-500" placeholder="Ej: Python Developer" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Frecuencia</label>
              <select value={formData.frequency} onChange={e=>setFormData({...formData, frequency: e.target.value})} className="w-full text-sm border-slate-200 rounded-lg p-2.5 focus:ring-blue-500 focus:border-blue-500">
                <option value="daily">Diaria</option>
                <option value="weekly">Semanal</option>
              </select>
            </div>
          </div>
          <div className="flex items-center justify-end gap-3 border-t border-slate-200 pt-4 mt-2">
            <button type="button" onClick={() => setShowForm(false)} className="text-sm font-semibold text-slate-600 hover:text-slate-800 px-3 py-2">
              Cancelar
            </button>
            <button type="submit" disabled={saving} className="flex items-center gap-2 bg-slate-900 hover:bg-black disabled:opacity-60 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors">
              {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />}
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center p-8 text-slate-400">
          <RefreshCw size={24} className="animate-spin" />
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center p-8 border-2 border-dashed border-slate-200 rounded-xl">
          <p className="text-slate-500 font-medium">No hay alertas configuradas aún.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 border-y border-slate-200">
              <tr>
                <th className="px-4 py-3 font-semibold">Nombre</th>
                <th className="px-4 py-3 font-semibold">Correo</th>
                <th className="px-4 py-3 font-semibold">Búsqueda</th>
                <th className="px-4 py-3 font-semibold">Frecuencia</th>
                <th className="px-4 py-3 font-semibold text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {alerts.map(a => (
                <tr key={a.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-900">{a.name}</td>
                  <td className="px-4 py-3 text-slate-600">{a.email}</td>
                  <td className="px-4 py-3"><span className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-md font-medium text-xs">{a.keyword}</span></td>
                  <td className="px-4 py-3 text-slate-500 capitalize">{a.frequency === 'daily' ? 'Diaria' : 'Semanal'}</td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => handleEdit(a)} className="text-slate-400 hover:text-blue-600 p-1.5 transition-colors"><Edit2 size={16} /></button>
                    <button onClick={() => handleDelete(a.id)} className="text-slate-400 hover:text-red-600 p-1.5 transition-colors ml-1"><Trash2 size={16} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
