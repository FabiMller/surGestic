import React from 'react';
import styles from '../styles/styles';
import ServerStatus from './ServerStatus';
import MicIndicator from './MicIndicator';

export default function TopBar({
  patientId,
  sliceName,
  sliceIndex,
  zoomLevel,
  selectedCell,
  backendError,
  isVoiceActive,
  micLevel,
}) {
  return (
    <div style={styles.topBar}>
      <div style={styles.metaOverlay}>
        <div>
          <div>PATIENT ID: <span style={styles.metaVal}>{patientId}</span></div>
          <div style={{ marginTop: '2px' }}>
            VIEW: <span style={styles.metaVal}>{sliceName || 'Waiting...'}</span>
          </div>
        </div>
        <div style={styles.metaSubInline}>
          INDEX: {sliceIndex}<br />
          MODE: MPR 2D | ZOOM: {zoomLevel.toFixed(1)}x<br />
          GRID: 4x4 {selectedCell ? `[SEL: ${selectedCell}]` : ''}
        </div>
      </div>

      <div style={styles.rightStatusContainer}>
        <ServerStatus backendError={backendError} />
        <MicIndicator isVoiceActive={isVoiceActive} micLevel={micLevel} />
      </div>
    </div>
  );
}
