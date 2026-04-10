import React, { useState } from 'react';

const API = 'http://localhost:5000/api/analyze';

export default function CasePrediction() {
  const [caseType, setCaseType] = useState('Criminal');
  const [facts, setFacts] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!facts.trim()) {
      setError('Please enter the case facts before predicting.');
      return;
    }
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const resp = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ caseText: facts }),
      });
      if (!resp.ok) throw new Error('Backend not reachable. Make sure Flask server is running on port 5000.');
      const data = await resp.json();
      if (data.error) throw new Error(data.error);
      // Save to history
      const history = JSON.parse(localStorage.getItem('jai_history') || '[]');
      history.unshift({
        id: data.case_id,
        type: 'prediction',
        caseType,
        query: facts.slice(0, 120),
        prediction: data.prediction,
        date: new Date().toISOString(),
      });
      localStorage.setItem('jai_history', JSON.stringify(history.slice(0, 50)));
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const outcome = results?.prediction?.outcome;
  const confidence = results?.prediction?.confidence;
  const isAccepted = outcome === 1;

  return (
    <div className="p-8 max-w-6xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-['Newsreader'] text-3xl font-bold mb-2" style={{ color: '#e2e2e9' }}>
          Case Outcome Prediction
        </h1>
        <p className="font-['Noto_Serif'] text-sm" style={{ color: '#9a8f7d' }}>
          Enter the case details below. The system will analyze using XGBoost + InLegalBERT and provide a prediction with full reasoning.
        </p>
      </div>

      {/* ═══ Input Form ═══ */}
      <form onSubmit={handlePredict} className="space-y-6 mb-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Case Type */}
          <div>
            <label className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold block mb-2"
              style={{ color: '#d4a843' }}
            >Case Type</label>
            <select value={caseType} onChange={(e) => setCaseType(e.target.value)}
              className="w-full px-4 py-3 font-['Inter'] text-sm outline-none transition-colors duration-200"
              style={{
                background: '#1a1b21',
                color: '#e2e2e9',
                border: '1px solid rgba(78, 70, 54, 0.2)',
                cursor: 'pointer',
              }}
            >
              <option>Criminal</option>
              <option>Civil</option>
              <option>Constitutional</option>
              <option>Administrative</option>
              <option>Family</option>
              <option>Labour</option>
            </select>
          </div>
        </div>

        {/* Case Facts */}
        <div>
          <label className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold block mb-2"
            style={{ color: '#d4a843' }}
          >Case Facts / Judgment Text</label>
          <textarea
            rows="10"
            placeholder="Paste the case facts, judgment text, or describe the case scenario here..."
            value={facts}
            onChange={(e) => setFacts(e.target.value)}
            className="w-full px-4 py-3 font-['Noto_Serif'] text-sm leading-relaxed outline-none resize-vertical transition-colors duration-200"
            style={{
              background: '#1a1b21',
              color: '#e2e2e9',
              border: '1px solid rgba(78, 70, 54, 0.2)',
              minHeight: '180px',
            }}
            onFocus={(e) => e.target.style.borderColor = 'rgba(212, 168, 67, 0.5)'}
            onBlur={(e) => e.target.style.borderColor = 'rgba(78, 70, 54, 0.2)'}
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <button type="submit" disabled={loading}
            className="flex items-center gap-2 px-8 py-3 font-['Inter'] text-sm font-bold uppercase tracking-[0.1em] transition-all duration-200 btn-press"
            style={{
              background: loading ? 'rgba(212, 168, 67, 0.5)' : 'linear-gradient(135deg, #d4a843, #f2c35b)',
              color: '#111318',
              border: 'none',
              cursor: loading ? 'wait' : 'pointer',
              boxShadow: '0 2px 16px rgba(212, 168, 67, 0.2)',
            }}
          >
            {loading && <span className="material-symbols-outlined loader text-lg">sync</span>}
            {loading ? 'Analyzing...' : 'Predict Outcome'}
          </button>
          {loading && (
            <span className="font-['Inter'] text-xs italic" style={{ color: '#9a8f7d' }}>
              Processing through NLP → Embedding → FAISS → XGBoost pipeline...
            </span>
          )}
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3"
            style={{ background: 'rgba(255, 180, 171, 0.08)', border: '1px solid rgba(255, 180, 171, 0.2)' }}
          >
            <span className="material-symbols-outlined text-sm" style={{ color: '#ffb4ab' }}>error</span>
            <span className="font-['Inter'] text-sm" style={{ color: '#ffb4ab' }}>{error}</span>
          </div>
        )}
      </form>

      {/* ═══ Results Section (appears after prediction) ═══ */}
      {results && (
        <div className="animate-fade-in-up space-y-8">
          {/* Divider */}
          <div className="flex items-center gap-4">
            <div className="flex-1 h-px" style={{ background: 'rgba(78, 70, 54, 0.2)' }} />
            <span className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold" style={{ color: '#d4a843' }}>
              Analysis Results
            </span>
            <div className="flex-1 h-px" style={{ background: 'rgba(78, 70, 54, 0.2)' }} />
          </div>

          {/* ── Prediction Card ── */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Outcome */}
            <div className="lg:col-span-2 p-8 relative overflow-hidden"
              style={{
                background: 'linear-gradient(145deg, #1a1b21, #1e1f25)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              }}
            >
              <div className="flex items-start justify-between mb-6">
                <div>
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] mb-2" style={{ color: '#9a8f7d' }}>
                    Predicted Outcome
                  </p>
                  <h2 className="font-['Newsreader'] text-4xl font-bold"
                    style={{ color: isAccepted ? '#44e2cd' : '#ffb4ab' }}
                  >
                    {isAccepted ? 'ACCEPTED / ALLOWED' : 'REJECTED / DISMISSED'}
                  </h2>
                </div>
                <div className="text-center px-6 py-4"
                  style={{ background: '#282a2f' }}
                >
                  <span className="font-['Inter'] text-2xl font-black block" style={{ color: '#e2e2e9' }}>
                    {(confidence * 100).toFixed(1)}%
                  </span>
                  <span className="font-['Inter'] text-[9px] uppercase tracking-[0.15em]" style={{ color: '#9a8f7d' }}>
                    Confidence
                  </span>
                </div>
              </div>

              {/* Sections Detected */}
              {results.sections && (
                <div className="space-y-3 mt-6">
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold" style={{ color: '#d4a843' }}>
                    Sections Detected
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {results.statute_codes?.map((sc, i) => (
                      <span key={i} className="px-3 py-1 font-['Inter'] text-xs font-semibold"
                        style={{
                          background: 'rgba(212, 168, 67, 0.1)',
                          border: '1px solid rgba(212, 168, 67, 0.25)',
                          color: '#f2c35b',
                        }}
                      >Section {sc.section} {sc.act}</span>
                    ))}
                    {(!results.statute_codes || results.statute_codes.length === 0) && (
                      <span className="font-['Noto_Serif'] text-sm italic" style={{ color: '#9a8f7d' }}>
                        No specific statute codes detected in text
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Key Entities */}
              {results.entities && results.entities.length > 0 && (
                <div className="mt-6 space-y-3">
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold" style={{ color: '#d4a843' }}>
                    Key Entities Extracted
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {results.entities.map((ent, i) => (
                      <span key={i} className="px-2 py-1 font-['Inter'] text-[11px]"
                        style={{
                          background: '#282a2f',
                          color: '#d2c5b1',
                          border: '1px solid rgba(78, 70, 54, 0.15)',
                        }}
                      >{ent.text || ent[0]} <span style={{ color: '#9a8f7d', fontSize: '9px' }}>({ent.label || ent[1]})</span></span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Factor Importance */}
            <div className="p-6"
              style={{
                background: '#1a1b21',
                border: '1px solid rgba(78, 70, 54, 0.1)',
              }}
            >
              <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-6" style={{ color: '#d4a843' }}>
                Influencing Factors
              </p>
              <div className="space-y-5">
                {results.feature_importance?.slice(0, 6).map(([feat, gain], i) => (
                  <div key={i}>
                    <div className="flex justify-between items-end mb-1">
                      <span className="font-['Inter'] text-[11px]" style={{ color: '#e2e2e9' }}>
                        {feat.replace(/_/g, ' ')}
                      </span>
                      <span className="font-['Inter'] text-[10px] font-bold" style={{ color: '#44e2cd' }}>
                        {gain.toFixed(3)}
                      </span>
                    </div>
                    <div className="h-[2px]" style={{ background: '#33353a' }}>
                      <div className="h-full transition-all duration-700"
                        style={{
                          width: `${Math.min(gain * 300, 100)}%`,
                          background: 'linear-gradient(90deg, #44e2cd, rgba(68, 226, 205, 0.4))',
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Top Keywords */}
              {results.top_keywords && results.top_keywords.length > 0 && (
                <div className="mt-8 pt-6" style={{ borderTop: '1px solid rgba(78, 70, 54, 0.1)' }}>
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-3" style={{ color: '#d4a843' }}>
                    Top Keywords (TF-IDF)
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {results.top_keywords.slice(0, 8).map(([kw, score], i) => (
                      <span key={i} className="px-2 py-0.5 font-['Inter'] text-[10px]"
                        style={{ background: '#282a2f', color: '#d2c5b1' }}
                      >{kw}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ── Legal Reasoning (WHY this outcome) ── */}
          <div className="p-8"
            style={{
              background: 'linear-gradient(145deg, #1a1b21, #1e1f25)',
              borderLeft: '4px solid #d4a843',
            }}
          >
            <h3 className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-4" style={{ color: '#d4a843' }}>
              Legal Reasoning — Why This Outcome?
            </h3>
            <p className="font-['Noto_Serif'] leading-relaxed mb-6" style={{ color: '#e2e2e9' }}>
              {results.explanation}
            </p>

            {/* Reasoning Trail */}
            {results.reasoning_trail && results.reasoning_trail.length > 0 && (
              <div className="mt-6 pt-6" style={{ borderTop: '1px solid rgba(78, 70, 54, 0.12)' }}>
                <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-4" style={{ color: '#44e2cd' }}>
                  Step-by-Step Reasoning Trail
                </p>
                <div className="space-y-3">
                  {results.reasoning_trail.map((step, i) => (
                    <div key={i} className="flex items-start gap-3 pl-2">
                      <span className="font-['Inter'] text-[10px] font-bold mt-1 shrink-0"
                        style={{ color: '#d4a843', minWidth: '20px' }}
                      >{i + 1}.</span>
                      <p className="font-['Noto_Serif'] text-sm leading-relaxed" style={{ color: '#d2c5b1' }}>
                        {step}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Similar Precedents ── */}
          {results.similar_precedents && results.similar_precedents.length > 0 && (
            <div>
              <h3 className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-4" style={{ color: '#d4a843' }}>
                Similar Precedent Cases (FAISS)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {results.similar_precedents.map((p, i) => (
                  <div key={i} className="p-5 transition-all duration-200 card-hover"
                    style={{
                      background: '#1a1b21',
                      border: '1px solid rgba(78, 70, 54, 0.12)',
                    }}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <span className="font-['Inter'] text-xs font-bold" style={{ color: '#e2e2e9' }}>
                        Case #{p.id}
                      </span>
                      <span className="px-2 py-0.5 font-['Inter'] text-[10px] font-bold"
                        style={{
                          background: p.label === 1 ? 'rgba(68, 226, 205, 0.1)' : 'rgba(255, 180, 171, 0.1)',
                          color: p.label === 1 ? '#44e2cd' : '#ffb4ab',
                        }}
                      >{p.label === 1 ? 'Accepted' : 'Rejected'}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-3">
                      <div className="flex-1 h-[2px]" style={{ background: '#33353a' }}>
                        <div className="h-full" style={{
                          width: `${p.similarity}%`,
                          background: 'linear-gradient(90deg, #d4a843, #f2c35b)',
                        }} />
                      </div>
                      <span className="font-['Inter'] text-xs font-bold" style={{ color: '#d4a843' }}>
                        {p.similarity}%
                      </span>
                    </div>
                    <p className="font-['Noto_Serif'] text-xs leading-relaxed line-clamp-3"
                      style={{ color: '#9a8f7d' }}
                    >{p.text_preview}</p>
                  </div>
                ))}
              </div>
            </div>
          )}



          {/* Disclaimer */}
          <div className="flex items-center gap-2 py-4" style={{ borderTop: '1px solid rgba(78, 70, 54, 0.08)' }}>
            <span className="material-symbols-outlined text-sm" style={{ color: '#9a8f7d' }}>info</span>
            <p className="font-['Inter'] text-[10px]" style={{ color: '#9a8f7d' }}>
              AI-assisted analysis. This is a decision-support tool — final judgment rests with the judiciary.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
