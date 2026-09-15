import React, { useState, useEffect } from 'react';
import { Crosshair, Sliders, Globe, Camera, Zap, Target, FileText, Activity } from 'lucide-react';
import ScenarioConfigurator from './components/scenario/ScenarioConfigurator';
import VirtualWorldManager from './components/world/VirtualWorldManager';
import VirtualCameraManager from './components/camera/VirtualCameraManager';
import DisturbancePanel from './components/disturbance/DisturbancePanel';
import DetectionPanel from './components/detection/DetectionPanel';
import StatusBadge from './components/scenario/StatusBadge';
import { fetchHealth } from './services/scenarioApi';
import './styles/scenario.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('detection'); // default to 'detection'
  const [simulatorStatus, setSimulatorStatus] = useState('SCENARIO_READY');
  const [backendOnline, setBackendOnline] = useState(true);

  // Poll backend health status periodically
  useEffect(() => {
    async function checkStatus() {
      const health = await fetchHealth();
      if (health.status === 'healthy') {
        setBackendOnline(true);
      } else {
        setBackendOnline(false);
      }
    }
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fsoc-app-root">
      {/* Top Mission Control Header */}
      <header className="app-header">
        <div className="header-container">
          <div className="brand-section">
            <div className="brand-icon">
              <Crosshair size={24} />
            </div>
            <div className="brand-titles">
              <h1>
                <span>FSOC COARSE ALIGNMENT SIMULATOR</span>
                <span className="team-tag">TEAM PHARO — SIH26169</span>
              </h1>
              <p>MISSION CONTROL & DETERMINISTIC VIRTUAL WORLD TESTBED</p>
            </div>
          </div>

          <div className="header-actions">
            <StatusBadge status={simulatorStatus} backendOnline={backendOnline} />
            
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ fontSize: '0.75rem', padding: '6px 12px' }}
              title="Open OpenAPI Swagger Documentation"
            >
              <FileText size={14} />
              <span>API DOCS</span>
            </a>
          </div>
        </div>
      </header>

      {/* Module Navigation Tabs */}
      <nav className="module-nav-bar">
        <button
          type="button"
          className={`nav-tab-btn ${activeTab === 'scenario' ? 'active' : ''}`}
          onClick={() => setActiveTab('scenario')}
        >
          <Sliders size={16} />
          <span>Module 1: Scenario Configuration</span>
        </button>

        <button
          type="button"
          className={`nav-tab-btn ${activeTab === 'world' ? 'active' : ''}`}
          onClick={() => setActiveTab('world')}
        >
          <Globe size={16} />
          <span>Module 2: Virtual World & Platforms</span>
        </button>

        <button
          type="button"
          className={`nav-tab-btn ${activeTab === 'camera' ? 'active' : ''}`}
          onClick={() => setActiveTab('camera')}
        >
          <Camera size={16} />
          <span>Module 3: Virtual Camera & Rendering</span>
        </button>

        <button
          type="button"
          className={`nav-tab-btn ${activeTab === 'disturbance' ? 'active' : ''}`}
          onClick={() => setActiveTab('disturbance')}
        >
          <Zap size={16} />
          <span>Module 4: Disturbance & Noise</span>
        </button>

        <button
          type="button"
          className={`nav-tab-btn ${activeTab === 'detection' ? 'active' : ''}`}
          onClick={() => setActiveTab('detection')}
        >
          <Target size={16} />
          <span>Module 5: Beacon Detection & Centroiding</span>
        </button>
      </nav>

      {/* Main View Area */}
      <main>
        {activeTab === 'scenario' && (
          <ScenarioConfigurator
            onStatusChange={setSimulatorStatus}
            backendOnline={backendOnline}
          />
        )}

        {activeTab === 'world' && (
          <VirtualWorldManager
            backendOnline={backendOnline}
          />
        )}

        {activeTab === 'camera' && (
          <VirtualCameraManager
            backendOnline={backendOnline}
          />
        )}

        {activeTab === 'disturbance' && (
          <DisturbancePanel
            backendOnline={backendOnline}
          />
        )}

        {activeTab === 'detection' && (
          <DetectionPanel
            backendOnline={backendOnline}
          />
        )}
      </main>
    </div>
  );
}
