import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { RoleProtectedRoute } from './components/RoleProtectedRoute';
import { Dashboard } from './pages/Dashboard';
import { Chats } from './pages/Chats';
import { UsersChats } from './pages/UsersChats';
import { Moderators } from './pages/Moderators';
import { ChatDetail } from './pages/ChatDetail';
import { OpenRouter } from './pages/OpenRouter';
import { AIModerationPayments } from './pages/AIModerationPayments';
import { Broadcast } from './pages/Broadcast';
import { UserVerification } from './pages/UserVerification';
import { Login } from './pages/Login';
import { AdminUsers } from './pages/AdminUsers';
import SearchStats from './pages/SearchStats';
import { UserRole } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if ((error as any)?.response?.status === 401) {
          return false;
        }
        return failureCount < 3;
      },
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <Dashboard />
              </RoleProtectedRoute>
            } />
            <Route path="chats" element={<Chats />} />
            <Route path="chats/:chatId" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN, UserRole.MANAGER]}>
                <ChatDetail />
              </RoleProtectedRoute>
            } />
            <Route path="users-chats" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <UsersChats />
              </RoleProtectedRoute>
            } />
            <Route path="moderators" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <Moderators />
              </RoleProtectedRoute>
            } />
            <Route path="admin-users" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <AdminUsers />
              </RoleProtectedRoute>
            } />
            <Route path="ai-moderation-payments" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <AIModerationPayments />
              </RoleProtectedRoute>
            } />
            <Route path="openrouter" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <OpenRouter />
              </RoleProtectedRoute>
            } />
            <Route path="broadcast" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <Broadcast />
              </RoleProtectedRoute>
            } />
            <Route path="user-verification" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                <UserVerification />
              </RoleProtectedRoute>
            } />
            <Route path="search-stats" element={
              <RoleProtectedRoute allowedRoles={[UserRole.ADMIN, UserRole.MANAGER]}>
                <SearchStats />
              </RoleProtectedRoute>
            } />
            <Route path="*" element={<Navigate to="/chats" replace />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;