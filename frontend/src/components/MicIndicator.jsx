import React from 'react';
import styles from '../styles/styles';

export default function MicIndicator({ isVoiceActive, micLevel }) {
  const hudStyle = {
    ...styles.micHud,
    border: isVoiceActive ? '1px solid #ef4444' : '1px solid #1e293b',
    boxShadow: isVoiceActive ? '0 0 12px rgba(239, 68, 68, 0.4)' : 'none',
  };

  const labelStyle = {
    ...styles.micLabel,
    color: isVoiceActive ? '#ef4444' : '#64748b',
  };

  const barFillStyle = {
    ...styles.micBarFill,
    width: `${isVoiceActive ? Math.min(micLevel * 4, 100) : 0}%`,
  };

  return (
    <div style={hudStyle}>
      <span style={labelStyle}>{isVoiceActive ? 'REC' : 'MIC'}</span>
      <div style={styles.micBarContainer}>
        <div style={barFillStyle}></div>
      </div>
    </div>
  );
}
