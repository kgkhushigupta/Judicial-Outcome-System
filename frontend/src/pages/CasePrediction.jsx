import React, { useState } from 'react';
import HierarchicalArgumentTree from './HierarchicalArgumentTree';

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

          {/* TEMPORAL DRIFT ALERT */}
          {results.temporal_drift?.has_drift && (
            <div className="mb-6 p-4 border border-yellow-600 bg-yellow-900 bg-opacity-30 rounded flex items-start gap-3">
              <span className="text-yellow-500 text-xl">⚠️</span>
              <div>
                <h3 className="text-yellow-500 font-bold mb-1">Temporal Legal Drift Detected</h3>
                <p className="text-gray-200">{results.temporal_drift.alert_message}</p>
                <div className="flex gap-4 mt-2 text-sm text-gray-400">
                  <span>Pre-{results.temporal_drift.threshold_year} Acceptance: {results.temporal_drift.old_acceptance_rate}%</span>
                  <span>Post-{results.temporal_drift.threshold_year} Acceptance: {results.temporal_drift.new_acceptance_rate}%</span>
                </div>
              </div>
            </div>
          )}

          {/* ACTIVE BIAS MITIGATION ALERT */}
          {results.bias_mitigation_log?.applied && (
            <div className="mb-6 p-4 border border-indigo-600 bg-indigo-900 bg-opacity-30 rounded flex items-start gap-3">
              <span className="text-indigo-400 text-xl">🛡️</span>
              <div>
                <h3 className="text-indigo-400 font-bold mb-1">Active Bias Correction Applied</h3>
                <p className="text-gray-200">{results.bias_mitigation_log.reason}</p>
                <div className="flex gap-4 mt-2 text-sm text-indigo-300">
                  <span>Adjustment: {results.bias_mitigation_log.adjustment > 0 ? '+' : ''}{results.bias_mitigation_log.adjustment}%</span>
                  <span>Demographic Filter: {Object.entries(results.bias_mitigation_log.demographics_detected).map(([k,v]) => `${k}=${v}`).join(', ')}</span>
                </div>
              </div>
            </div>
          )}

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

          {/* HIERARCHICAL ARGUMENT TREE */}
          {results.hierarchical_argument_tree && (
            <HierarchicalArgumentTree treeData={results.hierarchical_argument_tree} />
          )}

        </div>
      )}
    </div>
  );
}