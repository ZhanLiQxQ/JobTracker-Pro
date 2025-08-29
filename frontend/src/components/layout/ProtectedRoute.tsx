import React from 'react';
import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({
  children,
  roles
}: {
  children: React.ReactNode;
  roles?: string[];
}) => {
  const token = localStorage.getItem('token');
  const userRoles = JSON.parse(localStorage.getItem('roles') || '[]');

  if (!token) return <Navigate to="/login" replace />;
  if (roles && !roles.some(r => userRoles.includes(r))) {
    return <Navigate to="/403" replace />;
  }
  return children;
};