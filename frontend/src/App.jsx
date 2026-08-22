import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import History from './pages/History'
import Patients from './pages/Patients'
import AuditLogs from './pages/AuditLogs'
import Layout from './components/Layout'
import MeshBackground from './components/MeshBackground'
import { StudyChatProvider } from './context/StudyChatContext'
import { auth } from './api'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      auth.me()
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token)
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen relative flex items-center justify-center">
        <MeshBackground />
        <div className="w-14 h-14 rounded-full border-2 border-cyan-200 border-t-cyan-600 animate-spin" />
      </div>
    )
  }

  return (
    <BrowserRouter>
      <StudyChatProvider>
      <Routes>
        <Route path="/login" element={
          user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />
        } />
        <Route element={user ? <Layout user={user} onLogout={handleLogout} /> : <Navigate to="/login" />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/history" element={<History />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/audit" element={<AuditLogs />} />
        </Route>
      </Routes>
      </StudyChatProvider>
    </BrowserRouter>
  )
}

export default App
