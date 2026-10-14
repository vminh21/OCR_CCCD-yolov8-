import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/facebook_theme.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
