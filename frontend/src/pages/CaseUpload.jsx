import React, { useState, useRef } from 'react';

const API = 'http://localhost:5000/api/analyze';
const TABS = ['Summary', 'Sections', 'Similar Cases', 'Insights'];

export default function CaseUpload() {
  const fileRef = useRef(null);
  const [file, setFile] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ step: 0, label: '' });
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('Summary');

  const steps = [
    'Extracting text from document...',
    'Detecting legal sections...',
    'Running NLP and entity extraction...',
    'Finding similar precedent cases...',
    'Generating analysis...',
  ];

  const simulateProgress = () => {
    let step = 0;
    setProgress({ step: 0, label: steps[0] });
    const interval = setInterval(() => {
      step++;
      if (step < steps.length) {
        setProgress({ step, label: steps[step] });
      } else {
        clearInterval(interval);
      }
    }, 1500);
    return interval;
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer?.files?.[0] || e.target?.files?.[0];
    if (droppedFile) {
      setFile(droppedFile);
      // Read text from file (for demo, read as text)
      const reader = new FileReader();
      reader.onload = (ev) => {
        setExtractedText(ev.target.result);
      };
      reader.readAsText(droppedFile);
    }
  };

  const handleAnalyze = async () => {
    const textToAnalyze = extractedText.trim();
    if (!textToAnalyze) {
      setError('Please upload a document or paste text first.');
      return;
    }
    setLoading(true);
    setError(null);
    setResults(null);
    const progressInterval = simulateProgress();

    try {
      const resp = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ caseText: textToAnalyze }),
      });
      if (!resp.ok) throw new Error('Backend not reachable. Ensure Flask server is running on port 5000.');
      const data = await resp.json();
      if (data.error) throw new Error(data.error);

      // Save to history
      const history = JSON.parse(localStorage.getItem('jai_history') || '[]');
      history.unshift({
        id: data.case_id,
        type: 'upload',
        fileName: file?.name || 'Pasted text',
        query: textToAnalyze.slice(0, 120),
        date: new Date().toISOString(),
      });
      localStorage.setItem('jai_history', JSON.stringify(history.slice(0, 50)));

      setResults(data);
      setActiveTab('Summary');
    } catch (err) {
      setError(err.message);
    } finally {
      clearInterval(progressInterval);
      setLoading(false);
      setProgress({ step: 0, label: '' });
    }
  };

  const sections = results?.sections || {};
  const hasSections = Object.values(sections).some(v =>
    (Array.isArray(v) ? v.length > 0 : v && v.length > 0)
  );

  return (
    <div className="p-8 max-w-6xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-['Newsreader'] text-3xl font-bold mb-2" style={{ color: '#e2e2e9' }}>
          Document Upload & Analysis
        </h1>
        <p className="font-['Noto_Serif'] text-sm" style={{ color: '#9a8f7d' }}>
          Upload a legal document or paste text — the system will extract sections, detect statutes, find similar cases, and provide insights.
        </p>
      </div>

      {/* ═══ Upload Area ═══ */}
      {!results && (
        <div className="space-y-6">
          {/* Drag & Drop / File Upload */}
          <div
            className="border-2 border-dashed p-12 text-center cursor-pointer transition-colors duration-200"
            style={{
              borderColor: file ? 'rgba(68, 226, 205, 0.4)' : 'rgba(78, 70, 54, 0.25)',
              background: file ? 'rgba(68, 226, 205, 0.03)' : '#1a1b21',
            }}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
          >
            <input ref={fileRef} type="file" accept=".txt,.pdf,.docx" className="hidden" onChange={handleFileDrop} />
            <span className="material-symbols-outlined text-4xl mb-3 block"
              style={{ color: file ? '#44e2cd' : '#9a8f7d' }}
            >{file ? 'check_circle' : 'cloud_upload'}</span>
            {file ? (
              <div>
                <p className="font-['Inter'] text-sm font-bold" style={{ color: '#44e2cd' }}>{file.name}</p>
                <p className="font-['Inter'] text-xs mt-1" style={{ color: '#9a8f7d' }}>
                  {(file.size / 1024).toFixed(1)} KB — Click to replace
                </p>
              </div>
            ) : (
              <div>
                <p className="font-['Inter'] text-sm font-semibold" style={{ color: '#e2e2e9' }}>
                  Drop your document here or click to browse
                </p>
                <p className="font-['Inter'] text-xs mt-1" style={{ color: '#9a8f7d' }}>
                  Supports TXT, PDF, DOCX
                </p>
              </div>
            )}
          </div>

          {/* Or paste text */}
          <div className="flex items-center gap-4">
            <div className="flex-1 h-px" style={{ background: 'rgba(78, 70, 54, 0.15)' }} />
            <span className="font-['Inter'] text-[10px] uppercase tracking-[0.15em]" style={{ color: '#9a8f7d' }}>
              Or paste text directly
            </span>
            <div className="flex-1 h-px" style={{ background: 'rgba(78, 70, 54, 0.15)' }} />
          </div>

          <textarea
            rows="8"
            placeholder="Paste legal document text here..."
            value={extractedText}
            onChange={(e) => setExtractedText(e.target.value)}
            className="w-full px-4 py-3 font-['Noto_Serif'] text-sm leading-relaxed outline-none resize-vertical"
            style={{
              background: '#1a1b21',
              color: '#e2e2e9',
              border: '1px solid rgba(78, 70, 54, 0.2)',
              minHeight: '140px',
            }}
            onFocus={(e) => e.target.style.borderColor = 'rgba(212, 168, 67, 0.5)'}
            onBlur={(e) => e.target.style.borderColor = 'rgba(78, 70, 54, 0.2)'}
          />

          {/* Analyze Button */}
          <div className="flex items-center gap-4">
            <button onClick={handleAnalyze} disabled={loading}
              className="flex items-center gap-2 px-8 py-3 font-['Inter'] text-sm font-bold uppercase tracking-[0.1em] btn-press"
              style={{
                background: loading ? 'rgba(212, 168, 67, 0.5)' : 'linear-gradient(135deg, #d4a843, #f2c35b)',
                color: '#111318',
                border: 'none',
                cursor: loading ? 'wait' : 'pointer',
                boxShadow: '0 2px 16px rgba(212, 168, 67, 0.2)',
              }}
            >
              {loading && <span className="material-symbols-outlined loader text-lg">sync</span>}
              {loading ? 'Processing...' : 'Analyze Document'}
            </button>
          </div>

          {/* Progress Bar */}
          {loading && (
            <div className="p-5 space-y-4"
              style={{ background: '#1a1b21', border: '1px solid rgba(78, 70, 54, 0.12)' }}
            >
              <div className="flex justify-between items-center">
                <span className="font-['Inter'] text-xs font-semibold" style={{ color: '#e2e2e9' }}>
                  {progress.label}
                </span>
                <span className="font-['Inter'] text-xs" style={{ color: '#d4a843' }}>
                  {Math.min(Math.round(((progress.step + 1) / steps.length) * 100), 100)}%
                </span>
              </div>
              <div className="w-full h-1 rounded-full" style={{ background: '#33353a' }}>
                <div className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(((progress.step + 1) / steps.length) * 100, 100)}%`,
                    background: 'linear-gradient(90deg, #d4a843, #f2c35b)',
                  }}
                />
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 p-3"
              style={{ background: 'rgba(255, 180, 171, 0.08)', border: '1px solid rgba(255, 180, 171, 0.2)' }}
            >
              <span className="material-symbols-outlined text-sm" style={{ color: '#ffb4ab' }}>error</span>
              <span className="font-['Inter'] text-sm" style={{ color: '#ffb4ab' }}>{error}</span>
            </div>
          )}
        </div>
      )}

      {/* ═══ Results Section ═══ */}
      {results && (
        <div className="animate-fade-in-up space-y-6">
          {/* Back / New Analysis */}
          <button onClick={() => { setResults(null); setFile(null); setExtractedText(''); }}
            className="flex items-center gap-1 font-['Inter'] text-xs uppercase tracking-[0.1em] transition-colors hover:text-[#f2c35b]"
            style={{ color: '#9a8f7d', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            New Analysis
          </button>

          {/* Tabs */}
          <div className="flex gap-0 border-b" style={{ borderColor: 'rgba(78, 70, 54, 0.15)' }}>
            {TABS.map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className="px-6 py-3 font-['Inter'] text-xs uppercase tracking-[0.15em] font-semibold transition-colors duration-200"
                style={{
                  color: activeTab === tab ? '#f2c35b' : '#9a8f7d',
                  borderBottom: activeTab === tab ? '2px solid #f2c35b' : '2px solid transparent',
                  background: 'none',
                  border: 'none',
                  borderBottom: activeTab === tab ? '2px solid #f2c35b' : '2px solid transparent',
                  cursor: 'pointer',
                }}
              >{tab}</button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="min-h-[300px]">
            {/* SUMMARY TAB */}
            {activeTab === 'Summary' && (
              <div className="space-y-6 animate-fade-in">
                <div className="p-6" style={{ background: '#1a1b21' }}>
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-3" style={{ color: '#d4a843' }}>
                    Document Summary
                  </p>
                  <p className="font-['Noto_Serif'] leading-relaxed" style={{ color: '#e2e2e9' }}>
                    {results.explanation}
                  </p>
                </div>

                {/* Quick Stats Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 text-center" style={{ background: '#1a1b21' }}>
                    <p className="font-['Inter'] text-2xl font-black" style={{ color: '#44e2cd' }}>
                      {results.statute_codes?.length || 0}
                    </p>
                    <p className="font-['Inter'] text-[9px] uppercase tracking-[0.1em]" style={{ color: '#9a8f7d' }}>
                      Statutes Found
                    </p>
                  </div>
                  <div className="p-4 text-center" style={{ background: '#1a1b21' }}>
                    <p className="font-['Inter'] text-2xl font-black" style={{ color: '#d4a843' }}>
                      {results.entities?.length || 0}
                    </p>
                    <p className="font-['Inter'] text-[9px] uppercase tracking-[0.1em]" style={{ color: '#9a8f7d' }}>
                      Entities Extracted
                    </p>
                  </div>
                  <div className="p-4 text-center" style={{ background: '#1a1b21' }}>
                    <p className="font-['Inter'] text-2xl font-black" style={{ color: '#44e2cd' }}>
                      {results.similar_precedents?.length || 0}
                    </p>
                    <p className="font-['Inter'] text-[9px] uppercase tracking-[0.1em]" style={{ color: '#9a8f7d' }}>
                      Similar Cases
                    </p>
                  </div>
                  <div className="p-4 text-center" style={{ background: '#1a1b21' }}>
                    <p className="font-['Inter'] text-2xl font-black" style={{ color: '#d4a843' }}>
                      {results.top_keywords?.length || 0}
                    </p>
                    <p className="font-['Inter'] text-[9px] uppercase tracking-[0.1em]" style={{ color: '#9a8f7d' }}>
                      Keywords
                    </p>
                  </div>
                </div>

                {/* Key Entities */}
                {results.entities && results.entities.length > 0 && (
                  <div className="p-6" style={{ background: '#1a1b21' }}>
                    <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-3" style={{ color: '#d4a843' }}>
                      Extracted Entities
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {results.entities.map((ent, i) => (
                        <span key={i} className="px-3 py-1 font-['Inter'] text-xs"
                          style={{ background: '#282a2f', color: '#d2c5b1' }}
                        >{ent[0]} <span style={{ color: '#9a8f7d', fontSize: '9px' }}>({ent[1]})</span></span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* SECTIONS TAB */}
            {activeTab === 'Sections' && (
              <div className="space-y-4 animate-fade-in">
                {/* Statute Codes */}
                {results.statute_codes && results.statute_codes.length > 0 && (
                  <div className="p-6" style={{ background: '#1a1b21' }}>
                    <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-3" style={{ color: '#d4a843' }}>
                      Detected Statute Codes
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {results.statute_codes.map((sc, i) => (
                        <span key={i} className="px-3 py-1.5 font-['Inter'] text-sm font-semibold"
                          style={{
                            background: 'rgba(212, 168, 67, 0.1)',
                            border: '1px solid rgba(212, 168, 67, 0.25)',
                            color: '#f2c35b',
                          }}
                        >Section {sc.section} {sc.act}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Document Sections */}
                {hasSections && Object.entries(sections).map(([key, value], i) => {
                  const content = Array.isArray(value) ? value.join(', ') : value;
                  if (!content) return null;
                  return (
                    <div key={i} className="p-5"
                      style={{
                        background: '#1a1b21',
                        borderLeft: `3px solid ${key === 'Decision' ? '#44e2cd' : key === 'Statutes' ? '#d4a843' : 'rgba(78, 70, 54, 0.3)'}`,
                      }}
                    >
                      <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-2"
                        style={{ color: key === 'Decision' ? '#44e2cd' : '#d4a843' }}
                      >{key}</p>
                      <p className="font-['Noto_Serif'] text-sm leading-relaxed" style={{ color: '#d2c5b1' }}>
                        {content}
                      </p>
                    </div>
                  );
                })}

                {!hasSections && results.statute_codes?.length === 0 && (
                  <div className="p-8 text-center" style={{ background: '#1a1b21' }}>
                    <p className="font-['Noto_Serif'] italic" style={{ color: '#9a8f7d' }}>
                      No formal sections detected in the document.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* SIMILAR CASES TAB */}
            {activeTab === 'Similar Cases' && (
              <div className="space-y-4 animate-fade-in">
                {results.similar_precedents && results.similar_precedents.length > 0 ? (
                  results.similar_precedents.map((p, i) => (
                    <div key={i} className="p-5 flex gap-6"
                      style={{ background: '#1a1b21', border: '1px solid rgba(78, 70, 54, 0.1)' }}
                    >
                      <div className="shrink-0 text-center" style={{ minWidth: '80px' }}>
                        <p className="font-['Inter'] text-2xl font-black" style={{ color: '#d4a843' }}>
                          {p.similarity}%
                        </p>
                        <p className="font-['Inter'] text-[9px] uppercase" style={{ color: '#9a8f7d' }}>
                          Similarity
                        </p>
                        <div className="mt-2 px-2 py-0.5 font-['Inter'] text-[10px] font-bold"
                          style={{
                            background: p.label === 1 ? 'rgba(68, 226, 205, 0.1)' : 'rgba(255, 180, 171, 0.1)',
                            color: p.label === 1 ? '#44e2cd' : '#ffb4ab',
                          }}
                        >{p.label === 1 ? 'Accepted' : 'Rejected'}</div>
                      </div>
                      <div className="flex-1">
                        <p className="font-['Inter'] text-xs font-bold mb-2" style={{ color: '#e2e2e9' }}>
                          Case #{p.id}
                        </p>
                        <p className="font-['Noto_Serif'] text-sm leading-relaxed" style={{ color: '#d2c5b1' }}>
                          {p.text_preview}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center" style={{ background: '#1a1b21' }}>
                    <p className="font-['Noto_Serif'] italic" style={{ color: '#9a8f7d' }}>
                      No similar cases found in the database.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* INSIGHTS TAB */}
            {activeTab === 'Insights' && (
              <div className="space-y-6 animate-fade-in">
                {/* Keywords */}
                <div className="p-6" style={{ background: '#1a1b21' }}>
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-3" style={{ color: '#d4a843' }}>
                    Top Keywords (TF-IDF)
                  </p>
                  <div className="space-y-2">
                    {results.top_keywords?.slice(0, 10).map(([kw, score], i) => (
                      <div key={i} className="flex items-center gap-3">
                        <span className="font-['Inter'] text-xs font-medium" style={{ color: '#e2e2e9', minWidth: '140px' }}>
                          {kw}
                        </span>
                        <div className="flex-1 h-[2px]" style={{ background: '#33353a' }}>
                          <div className="h-full" style={{
                            width: `${Math.min(parseFloat(score) * 500, 100)}%`,
                            background: 'linear-gradient(90deg, #d4a843, #f2c35b)',
                          }} />
                        </div>
                        <span className="font-['Inter'] text-[10px] font-bold" style={{ color: '#9a8f7d' }}>
                          {parseFloat(score).toFixed(3)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Prediction Insight */}
                <div className="p-6"
                  style={{
                    background: results.prediction?.outcome === 1
                      ? 'rgba(68, 226, 205, 0.04)' : 'rgba(255, 180, 171, 0.04)',
                    borderLeft: `3px solid ${results.prediction?.outcome === 1 ? '#44e2cd' : '#ffb4ab'}`,
                  }}
                >
                  <p className="font-['Inter'] text-[10px] uppercase tracking-[0.2em] font-bold mb-2" style={{ color: '#d4a843' }}>
                    Pattern Analysis
                  </p>
                  <p className="font-['Noto_Serif'] leading-relaxed" style={{ color: '#e2e2e9' }}>
                    Based on the document analysis and comparison with {results.similar_precedents?.length || 0} similar past cases,
                    the text patterns indicate a {results.prediction?.outcome === 1 ? 'favorable' : 'unfavorable'} outcome
                    with {((results.prediction?.confidence || 0) * 100).toFixed(1)}% confidence.
                    {results.similar_precedents?.filter(p => p.label === results.prediction?.outcome).length > 0 &&
                      ` ${results.similar_precedents.filter(p => p.label === results.prediction.outcome).length} out of ${results.similar_precedents.length} similar cases had the same outcome.`
                    }
                  </p>
                </div>


              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
