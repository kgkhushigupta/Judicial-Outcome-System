import React, { useState } from 'react';

export default function HierarchicalArgumentTree({ treeData }) {
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  if (!treeData || !treeData.tree_structure) {
    return null;
  }

  const toggleNode = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const renderTreeNode = (node, nodeId, depth = 0) => {
    const isExpanded = expandedNodes.has(nodeId);
    const hasChildren = node.children && node.children.length > 0;
    const hasEvidence = node.evidence && node.evidence.length > 0;

    // Color based on confidence
    let confidenceColor = 'bg-red-900';
    if (node.confidence >= 0.7) {
      confidenceColor = 'bg-green-900';
    } else if (node.confidence >= 0.5) {
      confidenceColor = 'bg-yellow-900';
    }

    return (
      <div key={nodeId} className="ml-4">
        {/* Node Header */}
        <div
          className="flex items-center gap-2 p-3 bg-gray-800 border border-gray-700 rounded cursor-pointer hover:bg-gray-750 my-2"
          onClick={() => hasChildren && toggleNode(nodeId)}
        >
          {/* Expand button */}
          {hasChildren && (
            <span className="text-gray-400 w-6">
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          {!hasChildren && <span className="w-6"></span>}

          {/* Confidence badge */}
          <div
            className={`${confidenceColor} text-white px-3 py-1 rounded text-sm font-bold min-w-16 text-center`}
          >
            {(node.confidence < 1 ? node.confidence * 100 : node.confidence).toFixed(0)}%
          </div>

          {/* Node name */}
          <div className="flex-1">
            <p className="font-bold text-white">{node.name}</p>
            {node.description && (
              <p className="text-gray-400 text-sm">{node.description}</p>
            )}
          </div>
        </div>

        {/* Evidence list */}
        {hasEvidence && (
          <div className="ml-8 my-2 p-3 bg-gray-850 border-l-2 border-blue-500 rounded">
            <p className="text-gray-300 text-sm font-semibold mb-1">Evidence:</p>
            <ul className="text-gray-400 text-sm space-y-1">
              {node.evidence.map((ev, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-blue-400 mt-0.5">•</span>
                  <span>{ev}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Children */}
        {hasChildren && isExpanded && (
          <div className="border-l-2 border-gray-700">
            {node.children.map((child, idx) =>
              renderTreeNode(child, `${nodeId}-${idx}`, depth + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  const tree = treeData.tree_structure;
  const summary = treeData.summary || {};

  return (
    <div className="mt-8 p-6 bg-gray-900 border border-gray-800 rounded">
      <h2 className="text-2xl font-bold mb-4 text-yellow-400">Hierarchical Legal Argument Tree</h2>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-gray-400 text-sm">Prediction</p>
          <p className="text-xl font-bold text-green-400">
            {summary.outcome === 'ACCEPTED' ? '✓ Accepted' : '✗ Rejected'}
          </p>
        </div>

        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-gray-400 text-sm">Confidence</p>
          <p className="text-xl font-bold text-blue-400">{summary.overall_confidence?.toFixed(1)}%</p>
        </div>

        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-gray-400 text-sm">Main Arguments</p>
          <p className="text-xl font-bold text-purple-400">{summary.main_argument_branches}</p>
        </div>

        <div className="bg-gray-800 p-4 rounded border border-gray-700">
          <p className="text-gray-400 text-sm">Tree Depth</p>
          <p className="text-xl font-bold text-orange-400">{summary.tree_depth}</p>
        </div>
      </div>

      {/* Strength assessments */}
      {summary.precedent_strength && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <p className="text-gray-400 text-sm">Precedent Strength</p>
            <p className="text-sm text-gray-200">{summary.precedent_strength}</p>
          </div>

          <div className="bg-gray-800 p-3 rounded border border-gray-700">
            <p className="text-gray-400 text-sm">Statutory Strength</p>
            <p className="text-sm text-gray-200">{summary.statutory_strength}</p>
          </div>

          {summary.identified_weaknesses && summary.identified_weaknesses.length > 0 && (
            <div className="bg-gray-800 p-3 rounded border border-red-700">
              <p className="text-gray-400 text-sm">Identified Weaknesses</p>
              <ul className="text-sm text-red-300">
                {summary.identified_weaknesses.slice(0, 2).map((w, i) => (
                  <li key={i}>• {w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Tree visualization */}
      <div className="bg-gray-850 p-4 rounded border border-gray-700 overflow-x-auto">
        <p className="text-gray-400 text-sm mb-4">Click on branches to expand/collapse:</p>
        {renderTreeNode(tree, 'root')}
      </div>

      {/* ASCII representation */}
      {treeData.tree_ascii && (
        <div className="mt-6 bg-gray-850 p-4 rounded border border-gray-700">
          <p className="text-gray-400 text-sm mb-2">Text Representation:</p>
          <pre className="text-xs text-gray-300 overflow-x-auto">
            {treeData.tree_ascii}
          </pre>
        </div>
      )}
    </div>
  );
}
