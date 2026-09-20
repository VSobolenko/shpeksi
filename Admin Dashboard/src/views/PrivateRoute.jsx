import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'

export const PrivateRoute = ({ children }) => {
  const location = useLocation()
  if (!localStorage.getItem('user-pikupo')) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />
  }
  return children
}
