import React, { useState, useEffect } from 'react';

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('jai_history') || '[]');
    setHistory(stored);
  }, []);

  const handleDelete = (index) => {
    const updated = [...history];
    updated.splice(index, 1);
    setHistory(updated);
    localStorage.setItem('jai_history', JSON.stringify(updated));
  };

  const handleClearAll = () => {
    setHistory([]);
    localStorage.removeItem('jai_history');
  };

  const formatDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <div className="p-8 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="font-['Newsreader'] text-3xl font-bold mb-2" style={{ color: '#e2e2e9' }}>
            Analysis History
          </h1>
          <p className="font-['Noto_Serif'] text-sm" style={{ color: '#9a8f7d' }}>
            Your previous predictions and document analyses.
          </p>
        </div>
        {history.length > 0 && (
          <button onClick={handleClearAll}
            className="flex items-center gap-1 px-4 py-2 font-['Inter'] text-xs uppercase tracking-[0.1em] transition-colors duration-200"
            style={{
              color: '#ffb4ab',
              background: 'none',
              border: '1px solid rgba(255, 180, 171, 0.2)',
              cursor: 'pointer',
            }}
          >
            <span className="material-symbols-outlined text-sm">delete_sweep</span>
            Clear All
          </button>
        )}
      </div>

      {/* ═══ History List ═══ */}
      {history.length === 0 ? (
        <div className="p-16 text-center" style={{ background: '#1a1b21' }}>
          <span className="material-symbols-outlined text-5xl mb-4 block" style={{ color: '#33353a' }}>history</span>
          <p className="font-['Newsreader'] text-xl mb-2" style={{ color: '#e2e2e9' }}>No history yet</p>
          <p className="font-['Noto_Serif'] text-sm" style={{ color: '#9a8f7d' }}>
            Your predictions and document analyses will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item, i) => (
            <div key={i} className="flex items-center gap-4 p-4 transition-all duration-200 group"
              style={{
                background: '#1a1b21',
                border: '1px solid rgba(78, 70, 54, 0.08)',
              }}
            >
              {/* Type Icon */}
              <div className="w-10 h-10 flex items-center justify-center shrink-0"
                style={{
                  background: item.type === 'prediction'
                    ? 'rgba(212, 168, 67, 0.1)' : 'rgba(68, 226, 205, 0.1)',
                }}
              >
                <span className="material-symbols-outlined text-lg"
                  style={{ color: item.type === 'prediction' ? '#d4a843' : '#44e2cd' }}
                >{item.type === 'prediction' ? 'gavel' : 'description'}</span>
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-['Inter'] text-xs font-bold uppercase"
                    style={{ color: item.type === 'prediction' ? '#d4a843' : '#44e2cd' }}
                  >{item.type === 'prediction' ? 'Prediction' : 'Upload'}</span>
                  {item.caseType && (
                    <span className="font-['Inter'] text-[10px] px-2 py-0.5"
                      style={{ background: '#282a2f', color: '#9a8f7d' }}
                    >{item.caseType}</span>
                  )}
                  {item.prediction && (
                    <span className="font-['Inter'] text-[10px] px-2 py-0.5 font-bold"
                      style={{
                        background: item.prediction.outcome === 1
                          ? 'rgba(68, 226, 205, 0.1)' : 'rgba(255, 180, 171, 0.1)',
                        color: item.prediction.outcome === 1 ? '#44e2cd' : '#ffb4ab',
                      }}
                    >{item.prediction.outcome === 1 ? 'Accepted' : 'Rejected'}
                      {' · '}
                      {(item.prediction.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <p className="font-['Noto_Serif'] text-sm truncate" style={{ color: '#d2c5b1' }}>
                  {item.fileName || item.query}
                </p>
              </div>

              {/* Date */}
              <span className="font-['Inter'] text-[10px] shrink-0" style={{ color: '#9a8f7d' }}>
                {formatDate(item.date)}
              </span>

              {/* Delete */}
              <button onClick={() => handleDelete(i)}
                className="opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              >
                <span className="material-symbols-outlined text-lg" style={{ color: '#9a8f7d' }}>close</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
