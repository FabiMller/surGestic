import React from 'react';
import styles from '../styles/styles';

export default function ServerStatus({ backendError }) {
  const ledStyle = {
    ...styles.statusLed,
    backgroundColor: backendError ? '#ef4444' : '#10b981',
    boxShadow: backendError ? '0 0 10px #ef4444' : '0 0 10px #10b981',
  };

  return (
    <div style={styles.statusLedContainer}>
      <div style={ledStyle}></div>
      <span style={{ color: backendError ? '#ef4444' : '#10b981' }}>
        {backendError ? 'SERVER DISCONNECTED' : 'SERVER ONLINE'}
      </span>
    </div>
  );
}
