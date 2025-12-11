import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  // CORREÇÃO CRÍTICA (2025-12-09): Desabilitar StrictMode temporariamente
  // StrictMode causa double-renders em desenvolvimento, causando loops infinitos
  // TODO: Reabilitar após corrigir todos os problemas de re-renders
  <App />
)
