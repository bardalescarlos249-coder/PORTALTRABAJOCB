export const apiBase = process.env.NODE_ENV === 'production' 
  ? 'https://job-intelligence-api.herokuapp.com' // Cambia esto a la URL de tu API en prod si vas a hostear el backend
  : 'http://localhost:8000';
