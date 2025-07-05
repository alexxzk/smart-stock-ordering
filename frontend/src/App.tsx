import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { AppStateProvider } from './contexts/AppStateContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Forecasting from './pages/Forecasting'
import Inventory from './pages/Inventory'
import Suppliers from './pages/Suppliers'
import Integrations from './pages/Integrations'
import POSIntegrations from './pages/POSIntegrations'
import Orders from './pages/Orders'
import Login from './pages/Login'
import TestPage from './pages/TestPage'
import DebugTest from './pages/DebugTest'
import ProtectedRoute from './components/ProtectedRoute'
import PrivacyConsent from './components/PrivacyConsent'
import PrivacyPolicy from './components/PrivacyPolicy'

function App() {
  return (
    <AuthProvider>
      <AppStateProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="/debug-test" element={<DebugTest />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="forecasting" element={<Forecasting />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="suppliers" element={<Suppliers />} />
            <Route path="integrations" element={<Integrations />} />
            <Route path="pos-integrations" element={<POSIntegrations />} />
            <Route path="orders" element={<Orders />} />
          </Route>
        </Routes>
        <PrivacyConsent />
      </AppStateProvider>
    </AuthProvider>
  )
}

export default App 