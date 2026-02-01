import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'
import { LogIntegration } from './components/LogIntegration'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <LogIntegration />
    <App />
  </React.StrictMode>,
)