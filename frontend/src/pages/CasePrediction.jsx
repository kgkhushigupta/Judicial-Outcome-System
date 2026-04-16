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

      if (!resp.ok) throw new Error('Backend not reachable. Make sure Flask server is running.');

      const data = await resp.json();
      setResults(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const outcome = results?.prediction?.outcome;
  const confidence = results?.prediction?.confidence || 0;

  return (
    <div className="p-8 max-w-6xl mx-auto text-white">

      {/* HEADER */}
      <h1 className="text-3xl font-bold mb-6">Judicial AI System</h1>

      {/* CASE TYPE SELECT */}
      <div className="mb-4">
        <label className="block mb-2 text-sm text-gray-400">Case Type</label>
        <select
          value={caseType}
          onChange={(e) => setCaseType(e.target.value)}
          className="w-full p-3 bg-gray-800 border border-gray-700"
        >
          <option>Criminal</option>
          <option>Civil</option>
          <option>Family</option>
          <option>Labour</option>
          <option>Constitutional</option>
        </select>
      </div>

      {/* TEXT INPUT */}
      <textarea
        rows="10"
        placeholder="Enter case facts..."
        value={facts}
        onChange={(e) => setFacts(e.target.value)}
        className="w-full p-4 bg-gray-800 border border-gray-700 mb-6"
      />

      {/* BUTTON */}
      <button
        onClick={handlePredict}
        disabled={loading}
        className="px-6 py-3 bg-yellow-500 text-black font-bold"
      >
        {loading ? 'Analyzing...' : 'Predict Outcome'}
      </button>

      {/* ERROR */}
      {error && (
        <div className="mt-4 text-red-400">
          {error}
        </div>
      )}

      {/* RESULTS */}
      {results && (
        <div className="mt-8 p-6 bg-gray-900 border border-gray-800">

          {/* OUTCOME */}
          <h2 className="text-2xl font-bold mb-2">
            {outcome === 1 ? 'ACCEPTED / ALLOWED' : 'REJECTED / DISMISSED'}
          </h2>

          {/* CONFIDENCE (ORIGINAL — UNTOUCHED) */}
          <p className="text-lg mb-4">
            Confidence: {(confidence).toFixed(1)}%
          </p>

          {/* SECTIONS */}
          <div className="mb-4">
            <h3 className="font-bold mb-1">Sections Detected</h3>
            {results.statute_codes?.length > 0 ? (
              results.statute_codes.map((s, i) => (
                <p key={i}>
                  Section {s.section} {s.act}
                </p>
              ))
            ) : (
              <p>No specific statute codes detected in text</p>
            )}
          </div>

          {/* EXPLANATION */}
          <div>
            <h3 className="font-bold mb-1">Explanation</h3>
            <p>{results.explanation}</p>
          </div>

        </div>
      )}
    </div>
  );
}