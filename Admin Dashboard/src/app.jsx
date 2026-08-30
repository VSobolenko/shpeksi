import React from 'react'
import AdminLayout from 'layouts/Admin.jsx'
import AuthLayout from 'layouts/Auth.jsx'
import { PrivateRoute } from './views/PrivateRoute'
import { Routes, Route, Navigate, HashRouter } from 'react-router-dom'
function App() {
  return (
    <HashRouter>
      <Routes>
        <Route
          path="/admin/*"
          element={
            <PrivateRoute>
              <AdminLayout />
            </PrivateRoute>
          }
        />
        <Route path="/auth/*" element={<AuthLayout />} />
        <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </HashRouter>
  )
}
export default App
