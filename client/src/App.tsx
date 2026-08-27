import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import AuthPage from './pages/AuthPage'
import ChatPage from './pages/ChatPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-base)',
        flexDirection: 'column',
        gap: 16,
      }}>
        <div style={{
          width: 48,
          height: 48,
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
          borderRadius: 12,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 24,
          animation: 'typingBounce 1.2s infinite',
        }}>
          🎓
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Loading AI Sensei…</p>
      </div>
    )
  }

  return user ? <>{children}</> : <Navigate to="/auth" replace />
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/auth" element={user ? <Navigate to="/" replace /> : <AuthPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
