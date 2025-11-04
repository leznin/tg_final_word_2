import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useMobileMenu } from '../../hooks/useMobileMenu';

export const MainLayout: React.FC = () => {
  const { isMobileMenuOpen, isMobile, toggleMobileMenu, closeMobileMenu } = useMobileMenu();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <Sidebar 
          isOpen={isMobile ? isMobileMenuOpen : true}
          isMobile={isMobile}
          onClose={closeMobileMenu}
        />
        <div className="flex-1 min-w-0">
          <Header 
            onMobileMenuToggle={toggleMobileMenu}
            isMobile={isMobile}
          />
          <main className="p-4 md:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};