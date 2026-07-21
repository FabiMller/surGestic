import React, { useState, useEffect, useRef } from 'react';

function App() {
  const patientId = 'TEST-ID-12345678';
  const [currentSlice, setCurrentSlice] = useState({ index: 0, imageUrl: '', sliceName: '' });
  const [allSlices, setAllSlices] = useState([]);
  const [backendError, setBackendError] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false); 
  const [micLevel, setMicLevel] = useState(0); 
  const [selectedCell, setSelectedCell] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [imageOffset, setImageOffset] = useState({ x: 0, y: 0 });
  const [zoomOrigin, setZoomOrigin] = useState({ x: 50, y: 50 });

  const thumbnailRefs = useRef({});

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/current-slice');
        if (!response.ok) throw new Error('API Error');
        
        const data = await response.json();
        
        if (data.all_slices) {
          setAllSlices(data.all_slices);
        }

        setCurrentSlice({
          index: data.index,
          imageUrl: data.image_url,
          sliceName: data.slice_name
        });
        
        setIsVoiceActive(!!data.is_voice_active);
        setMicLevel(data.mic_level || 0); 
        setSelectedCell(data.selected_cell || null);
        setZoomLevel(data.zoom_level || 1);
        setImageOffset({ x: data.offset_x || 0, y: data.offset_y || 0 });
        setZoomOrigin({ x: data.zoom_origin_x ?? 50, y: data.zoom_origin_y ?? 50 });
        setBackendError(false);
      } catch (error) {
        setBackendError(true);
        setIsVoiceActive(false);
        setMicLevel(0);
      }
    }, 50);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (thumbnailRefs.current[currentSlice.index]) {
      thumbnailRefs.current[currentSlice.index].scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [currentSlice.index]);

  const styles = {
    container: {
      backgroundColor: '#05070f',
      color: '#94a3b8',
      height: '100vh',
      width: '100vw',
      display: 'flex',
      fontFamily: 'SF Pro Display, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      margin: 0,
      padding: 0,
      overflow: 'hidden',
      userSelect: 'none',
    },
    sidebar: {
      width: '260px',
      height: '100vh',
      backgroundColor: '#0c0f1d',
      borderRight: '1px solid #1e293b',
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box',
    },
    slicesSection: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflowY: 'auto',
      padding: '15px 10px 5px 10px',
      gap: '10px',
      borderBottom: '1px solid #1e293b',
    },
    sidebarHeader: {
      fontSize: '0.75rem',
      textTransform: 'uppercase',
      letterSpacing: '2px',
      color: '#64748b',
      paddingLeft: '5px',
      marginBottom: '2px',
      fontWeight: 'bold',
    },
    thumbnailWrapper: {
      position: 'relative',
      borderRadius: '4px',
      overflow: 'hidden',
      backgroundColor: '#000',
      border: '2px solid transparent',
      transition: 'all 0.2s ease',
      aspectRatio: '16/9',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
    },
    thumbnailActive: {
      border: '2px solid #38bdf8',
      boxShadow: '0 0 12px rgba(56, 189, 248, 0.4)',
    },
    thumbnailImg: {
      width: '100%',
      height: '100%',
      objectFit: 'cover',
      opacity: 0.6,
    },
    thumbnailImgActive: {
      opacity: 1,
    },
    thumbnailLabel: {
      position: 'absolute',
      bottom: '4px',
      left: '6px',
      fontSize: '0.65rem',
      backgroundColor: 'rgba(0,0,0,0.7)',
      padding: '2px 6px',
      borderRadius: '4px',
      color: '#fff',
      fontFamily: 'monospace',
    },
    aiSection: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      padding: '12px',
      backgroundColor: 'rgba(12, 15, 29, 0.95)',
      boxSizing: 'border-box',
      overflow: 'hidden',
      position: 'relative',
    },
    aiHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '10px'
    },
    aiTitle: {
      fontSize: '0.75rem',
      textTransform: 'uppercase',
      letterSpacing: '1.5px',
      color: '#38bdf8',
      fontWeight: 'bold',
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
    },
    aiBadge: {
      fontSize: '0.6rem',
      backgroundColor: 'rgba(56, 189, 248, 0.15)',
      color: '#38bdf8',
      border: '1px solid rgba(56, 189, 248, 0.3)',
      padding: '2px 6px',
      borderRadius: '10px',
      fontWeight: 'bold',
    },
    aiContentBox: {
      flex: 1,
      backgroundColor: '#05070f',
      border: '1px solid #1e293b',
      borderRadius: '6px',
      padding: '10px',
      overflowY: 'auto',
      fontSize: '0.78rem',
      lineHeight: '1.5',
      color: '#cbd5e1',
      fontFamily: 'monospace',
    },
    mainContent: {
      flex: 1,
      height: '100vh',
      backgroundColor: '#000',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      minWidth: 0,
      boxSizing: 'border-box',
    },
    topBar: {
      height: '65px',
      width: '100%',
      backgroundColor: 'rgba(12, 15, 29, 0.95)',
      borderBottom: '1px solid #1e293b',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      boxSizing: 'border-box',
      zIndex: 10,
    },
    metaOverlay: {
      fontFamily: 'monospace',
      fontSize: '0.85rem',
      color: '#38bdf8',
      lineHeight: '1.3',
      display: 'flex',
      alignItems: 'center',
      gap: '24px',
    },
    metaVal: {
      color: '#fff',
      fontSize: '1rem',
      fontWeight: 'bold',
    },
    metaSubInline: {
      color: '#64748b',
      fontSize: '0.78rem',
      borderLeft: '1px solid #1e293b',
      paddingLeft: '16px',
    },
    rightStatusContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    },
    statusLedContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      backgroundColor: '#05070f',
      padding: '6px 12px',
      borderRadius: '20px',
      border: '1px solid #1e293b',
      fontSize: '0.8rem',
      fontWeight: '500',
      letterSpacing: '0.5px',
    },
    statusLed: {
      width: '10px',
      height: '10px',
      borderRadius: '50%',
      backgroundColor: backendError ? '#ef4444' : '#10b981',
      boxShadow: backendError ? '0 0 10px #ef4444' : '0 0 10px #10b981',
      transition: 'background-color 0.3s ease',
    },
    micHud: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      backgroundColor: '#05070f',
      padding: '6px 14px',
      borderRadius: '20px',
      border: isVoiceActive ? '1px solid #ef4444' : '1px solid #1e293b',
      boxShadow: isVoiceActive ? '0 0 12px rgba(239, 68, 68, 0.4)' : 'none',
      width: '140px',
      boxSizing: 'border-box',
      transition: 'all 0.2s ease',
    },
    micLabel: {
      fontSize: '0.7rem',
      fontFamily: 'monospace',
      color: isVoiceActive ? '#ef4444' : '#64748b', 
      fontWeight: 'bold',
      transition: 'all 0.2s ease',
    },
    micBarContainer: {
      flex: 1,
      height: '6px',
      backgroundColor: '#1e293b',
      borderRadius: '3px',
      overflow: 'hidden',
    },
    micBarFill: {
      height: '100%',
      width: `${isVoiceActive ? Math.min(micLevel * 4, 100) : 0}%`, 
      backgroundColor: '#ef4444', 
      boxShadow: '0 0 8px rgba(239, 68, 68, 0.6)',
      transition: 'width 0.15s ease-out', 
    },
    imageArea: {
      flex: 1,
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
    },
    imageContainer: {
      position: 'relative',
      width: '100%',
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
    },
    activeImage: {
      maxHeight: '100%',
      maxWidth: '100%',
      width: '100%',
      height: '100%',
      objectFit: 'contain',
      display: 'block',
      transformOrigin: '50% 50%',
      transition: 'transform 0.18s ease-out',
    },
    gridOverlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gridTemplateRows: 'repeat(4, 1fr)',
      pointerEvents: 'none',
    },
    gridCell: {
      position: 'relative',
      borderRight: '1px solid rgba(255, 255, 255, 0.15)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
    },
    selectedGridCell: {
      boxShadow: 'inset 0 0 0 1px rgba(255, 255, 255, 0.6)',
      backgroundColor: 'rgba(56, 189, 248, 0.05)',
    },
    rowLabel: {
      position: 'absolute',
      left: '10px',
      top: '50%',
      transform: 'translateY(-50%)',
      fontSize: '0.85rem',
      fontWeight: 'bold',
      color: 'rgba(56, 189, 248, 0.9)', 
      fontFamily: 'monospace',
      textShadow: '1px 1px 3px #000',
    },
    colLabel: {
      position: 'absolute',
      bottom: '10px',
      left: '50%',
      transform: 'translateX(-50%)',
      fontSize: '0.85rem',
      fontWeight: 'bold',
      color: 'rgba(56, 189, 248, 0.9)',
      fontFamily: 'monospace',
      textShadow: '1px 1px 3px #000',
    }
  };

  const columns = ['A', 'B', 'C', 'D'];
  const rows = ['4', '3', '2', '1'];

  return (
    <div style={styles.container}>
      {/* SIDEBAR */}
      <div style={styles.sidebar}>
        {/* CT SLICES */}
        <div style={styles.slicesSection}>
          <div style={styles.sidebarHeader}>CT Slices ({allSlices.length})</div>
          {allSlices.map((sliceName, idx) => {
            const isActive = idx === currentSlice.index;
            return (
              <div
                key={idx}
                ref={(el) => (thumbnailRefs.current[idx] = el)}
                style={{
                  ...styles.thumbnailWrapper,
                  ...(isActive ? styles.thumbnailActive : {}),
                }}
              >
                <img
                  src={`/ct/${sliceName}`}
                  alt={`Thumb ${idx}`}
                  style={{
                    ...styles.thumbnailImg,
                    ...(isActive ? styles.thumbnailImgActive : {}),
                  }}
                />
                <div style={styles.thumbnailLabel}># {String(idx).padStart(2, '0')}</div>
              </div>
            );
          })}
        </div>

        {/* AI ANALYSIS OVERLAY */}
        <div style={styles.aiSection}>
          <div style={styles.aiHeader}>
            <div style={styles.aiTitle}>
              <div style={{alignItems: 'center', justifyContent: 'center', display: 'flex'}}></div>
              AI-Assistant
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
              • Thorax-Scan Slice #{String(currentSlice.index).padStart(2, '0')}: Dichteinheiten liegen im normalen Hounsfield-Bereich (HU: 30 - 50).
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
      </div>

      {/* MONITOR MAIN CONTENT AREA */}
      <div style={styles.mainContent}>
        {/* TOP BAR / HUD OVERLAY */}
        <div style={styles.topBar}>
          <div style={styles.metaOverlay}>
            <div>
              <div>PATIENT ID: <span style={styles.metaVal}>{patientId}</span></div>
              <div style={{ marginTop: '2px' }}>
                VIEW: <span style={styles.metaVal}>{currentSlice.sliceName || 'Waiting...'}</span>
              </div>
            </div>
            <div style={styles.metaSubInline}>
              INDEX: {currentSlice.index}<br />
              MODE: MPR 2D | ZOOM: {zoomLevel.toFixed(1)}x<br />
              GRID: 4x4 {selectedCell ? `[SEL: ${selectedCell}]` : ''}
            </div>
          </div>

          <div style={styles.rightStatusContainer}>
            <div style={styles.statusLedContainer}>
              <div style={styles.statusLed}></div>
              <span style={{ color: backendError ? '#ef4444' : '#10b981' }}>
                {backendError ? 'SERVER DISCONNECTED' : 'SERVER ONLINE'}
              </span>
            </div>
            <div style={styles.micHud}>
              <span style={styles.micLabel}>{isVoiceActive ? 'REC' : 'MIC'}</span>
              <div style={styles.micBarContainer}>
                <div style={styles.micBarFill}></div>
              </div>
            </div>
          </div>
        </div>

        {/* CT IMAGE DISPLAY AREA (begins below the top bar) */}
        <div style={styles.imageArea}>
          {currentSlice.imageUrl ? (
            <div style={styles.imageContainer}>
              <img
                src={currentSlice.imageUrl}
                alt="Active CT Slice"
                style={{
                  ...styles.activeImage,
                  transform: `translate(${imageOffset.x}%, ${imageOffset.y}%) scale(${zoomLevel})`,
                  transformOrigin: `${zoomOrigin.x}% ${zoomOrigin.y}%`,
                }}
                key={currentSlice.index}
              />
              <div style={styles.gridOverlay}>
                {rows.map((row, rowIndex) =>
                  columns.map((col, colIndex) => {
                    const isRightEdge = col === 'D';
                    const isBottomEdge = row === '1';
                    
                    const showRowLabel = colIndex === 0;
                    const showColLabel = rowIndex === 3;
                    const isSelected = `${col}${row}` === selectedCell;

                    return (
                      <div
                        key={`${col}${row}`}
                        style={{
                          ...styles.gridCell,
                          ...(isSelected ? styles.selectedGridCell : {}),
                          borderRight: isRightEdge ? 'none' : styles.gridCell.borderRight,
                          borderBottom: isBottomEdge ? 'none' : styles.gridCell.borderBottom,
                        }}
                      >
                        {showRowLabel && <span style={styles.rowLabel}>{row}</span>}
                        {showColLabel && <span style={styles.colLabel}>{col}</span>}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          ) : (
            <div style={{ color: '#475569', fontSize: '1.2rem', letterSpacing: '1px', fontFamily: 'monospace' }}>
              NO IMAGE STREAM SIGNAL
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;