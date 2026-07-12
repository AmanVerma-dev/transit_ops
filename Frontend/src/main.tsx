import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { useAuthStore } from './store/useAuthStore'
import './index.css'
import App from './App'

useAuthStore.getState().rehydrate()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
