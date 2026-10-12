import React from 'react';
import styles from '../styles/styles';

export default function AiPanel({ sliceIndex }) {
  return (
    <div style={styles.aiSection}>
      <div style={styles.aiHeader}>
        <div style={styles.aiTitle}>
          <div style={{ alignItems: 'center', justifyContent: 'center', display: 'flex' }}></div>
          AI-Assistant (Demo)
        </div>
        <span style={styles.aiBadge}>LIVE</span>
      </div>

      <div style={styles.aiContentBox}>
        <p style={{ margin: '0 0 8px 0', color: '#38bdf8', fontWeight: 'bold' }}>
          [AUTOMATED CT FINDINGS]
        </p>
        <p style={{ margin: '0 0 8px 0' }}>
          • Segment 4A: Keine Auffälligkeiten im Weichgewebe festgestellt.
        </p>
        <p style={{ margin: '0 0 8px 0' }}>
          • Thorax-Scan Slice #{String(sliceIndex).padStart(2, '0')}: Dichteinheiten liegen im normalen Hounsfield-Bereich (HU: 30 - 50).
        </p>
        <p style={{ margin: '0 0 8px 0' }}>
          • Hinweis: Leichte Asymmetrie im lateralen Bereich beobachtet. Manuelle Nachprüfung in Raster B2 empfohlen.
        </p>
        <p style={{ margin: '0 0 8px 0', color: '#64748b' }}>
          --- Zusätzliche Protokolldaten ---
        </p>
        <p style={{ margin: '0 0 8px 0' }}>
          Algorithmus: MedVision-v2.4
          <br />
          Konfidenz: 94.8%
          <br />
          Status: Validiert
        </p>
        <p style={{ margin: 0 }}>
          Klicken oder navigieren Sie per Sprachbefehl zu Grid "B2", um die Vergrößerung automatisch auf die Auffälligkeit zu fokussieren.
        </p>
      </div>
    </div>
  );
}
