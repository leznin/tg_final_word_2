import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import MiniAppUserSearch from './pages/MiniAppUserSearch'
import './index.css'

function MiniApp() {
  return (
    <Routes>
      <Route path="/mini-app/user-search" element={<MiniAppUserSearch />} />
      <Route path="*" element={<Navigate to="/mini-app/user-search" replace />} />
    </Routes>
  )
}

export default MiniApp
