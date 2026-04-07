import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', icon: 'gavel', label: 'Case Prediction' },
  { path: '/upload', icon: 'upload_file', label: 'Upload & Analyze' },
  { path: '/history', icon: 'history', label: 'History' },
];

export default function Layout() {
  const location = useLocation();
  const [hoveredNav, setHoveredNav] = useState(null);

  return (
    <div className="min-h-screen flex" style={{ background: '#111318', color: '#e2e2e9' }}>
      {/* ═══ Sidebar ═══ */}
      <aside className="fixed left-0 top-0 h-full w-60 flex flex-col z-50"
        style={{
          background: 'linear-gradient(180deg, #13151a 0%, #0e1015 100%)',
          borderRight: '1px solid rgba(78, 70, 54, 0.12)',
        }}
      >
        {/* Logo */}
        <div className="px-5 pt-7 pb-8">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, #d4a843, #f2c35b)',
                boxShadow: '0 0 20px rgba(212, 168, 67, 0.2)',
              }}
            >
              <span className="material-symbols-outlined text-[#111318] text-lg"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >balance</span>
            </div>
            <div>
              <div className="font-['Newsreader'] text-lg font-bold tracking-tight"
                style={{ color: '#d4a843' }}
              >Judicial AI</div>
              <div className="font-['Inter'] text-[9px] uppercase tracking-[0.2em]"
                style={{ color: '#9a8f7d' }}
              >Legal Intelligence</div>
            </div>
          </div>
          <div className="mt-5 h-px"
            style={{ background: 'linear-gradient(90deg, rgba(212, 168, 67, 0.3), transparent)' }}
          />
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map((item, i) => {
            const isActive = location.pathname === item.path;
            const isHovered = hoveredNav === i;

            return (
              <Link key={i} to={item.path}
                onMouseEnter={() => setHoveredNav(i)}
                onMouseLeave={() => setHoveredNav(null)}
                className="flex items-center px-3 py-2.5 rounded-lg relative transition-all duration-200"
                style={{
                  background: isActive
                    ? 'linear-gradient(90deg, rgba(212, 168, 67, 0.12), rgba(212, 168, 67, 0.03))'
                    : isHovered ? 'rgba(255, 255, 255, 0.03)' : 'transparent',
                }}
              >
                {isActive && (
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-l"
                    style={{
                      background: 'linear-gradient(180deg, #f2c35b, #d4a843)',
                      boxShadow: '0 0 8px rgba(212, 168, 67, 0.4)',
                    }}
                  />
                )}
                <span className="material-symbols-outlined mr-3 text-lg transition-colors duration-200"
                  style={{
                    color: isActive ? '#f2c35b' : isHovered ? '#d2c5b1' : '#9a8f7d',
                    fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0",
                  }}
                >{item.icon}</span>
                <span className="font-['Inter'] text-[11px] uppercase tracking-[0.15em] transition-colors duration-200"
                  style={{
                    color: isActive ? '#f2c35b' : isHovered ? '#e2e2e9' : '#9a8f7d',
                    fontWeight: isActive ? 700 : 500,
                  }}
                >{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Bottom */}
        <div className="px-4 py-5">
          <div className="h-px mb-4"
            style={{ background: 'linear-gradient(90deg, rgba(78, 70, 54, 0.25), transparent)' }}
          />
          <div className="px-2">
            <p className="font-['Inter'] text-[9px] uppercase tracking-[0.15em]" style={{ color: '#9a8f7d' }}>
              Powered by XGBoost + InLegalBERT
            </p>
          </div>
        </div>
      </aside>

      {/* ═══ Main Content ═══ */}
      <main className="ml-60 w-full min-h-screen flex flex-col" style={{ background: '#111318' }}>
        {/* Header */}
        <header className="sticky top-0 z-40 flex justify-between items-center w-full px-8 h-14"
          style={{
            background: 'rgba(17, 19, 24, 0.85)',
            backdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(78, 70, 54, 0.1)',
          }}
        >
          <span className="font-['Newsreader'] text-base font-bold tracking-tight uppercase"
            style={{ color: '#d4a843' }}
          >Judicial AI System</span>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full"
            style={{
              background: 'rgba(68, 226, 205, 0.08)',
              border: '1px solid rgba(68, 226, 205, 0.15)',
            }}
          >
            <div className="w-1.5 h-1.5 rounded-full animate-pulse"
              style={{ background: '#44e2cd' }}
            />
            <span className="font-['Inter'] text-[10px] uppercase tracking-[0.15em] font-bold"
              style={{ color: '#44e2cd' }}
            >System Ready</span>
          </div>
        </header>

        <div className="flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
