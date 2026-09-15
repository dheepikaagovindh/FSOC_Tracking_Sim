import React from 'react';
import { CheckCircle2, AlertTriangle, RefreshCw, Radio } from 'lucide-react';

export default function StatusBadge({ status, backendOnline = true }) {
  if (!backendOnline) {
    return (
      <div className="status-pill error" title="Backend service not reachable">
        <Radio size={14} className="pulse-dot" />
        <span>OFFLINE (DEMO MODE)</span>
      </div>
    );
  }

  switch (status) {
    case 'SCENARIO_READY':
    case 'READY':
      return (
        <div className="status-pill ready">
          <CheckCircle2 size={14} />
          <span>✓ SCENARIO READY</span>
        </div>
      );
    case 'SYNCING':
      return (
        <div className="status-pill syncing">
          <RefreshCw size={14} className="pulse-dot" />
          <span>SYNCING...</span>
        </div>
      );
    case 'ERROR':
      return (
        <div className="status-pill error">
          <AlertTriangle size={14} />
          <span>CONFIG ERROR</span>
        </div>
      );
    default:
      return (
        <div className="status-pill syncing">
          <span className="pulse-dot" />
          <span>{status || 'INITIALIZING'}</span>
        </div>
      );
  }
}
