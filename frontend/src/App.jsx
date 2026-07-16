import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [currentSlice, setCurrentSlice] = useState({ index: 0, imageUrl: '', sliceName: '' });
  const [allSlices, setAllSlices] = useState([]);
  const [backendError, setBackendError] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false); 
  const [micLevel, setMicLevel] = useState(0); 
  
  const thumbnailRefs = useRef({});

  // API polling at an accelerated 50ms interval for low-latency updates
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
        setBackendError(false);
      } catch (error) {
        setBackendError(true);
        setIsVoiceActive(false);
        setMicLevel(0);
      }
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Automatic sidebar scrolling to keep the active thumbnail visible
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
      width: '240px',
      height: '100vh',
      backgroundColor: '#0c0f1d',
      borderRight: '1px solid #1e293b',
      display: 'flex',
      flexDirection: 'column',
      overflowY: 'auto',
      padding: '15px 10px',
      boxSizing: 'border-box',
      gap: '12px',
    },
    sidebarHeader: {
      fontSize: '0.75rem',
      textTransform: 'uppercase',
      letterSpacing: '2px',
      color: '#64748b',
      paddingLeft: '5px',
      marginBottom: '5px',
    },
    thumbnailWrapper: {
      position: 'relative',
      borderRadius: '4px',
      overflow: 'hidden',
      backgroundColor: '#000',
      border: '2px solid transparent',
      transition: 'all 0.2s ease',
      cursor: 'pointer',
      aspectRatio: '16/9',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
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
    },
    mainContent: {
      flex: 1,
      height: '100vh',
      backgroundColor: '#000',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      alignItems: 'center',
      justifyContent: 'center',
    },
    imageContainer: {
      position: 'relative',
      maxHeight: '92vh',
      maxWidth: '95%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    activeImage: {
      maxHeight: '92vh',
      maxWidth: '100%',
      objectFit: 'contain',
      display: 'block',
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
    },
    metaOverlay: {
      position: 'absolute',
      top: '20px',
      left: '20px',
      pointerEvents: 'none',
      fontFamily: 'monospace',
      fontSize: '0.85rem',
      color: '#38bdf8',
      lineHeight: '1.4',
      textShadow: '1px 1px 2px #000',
      zIndex: 10,
    },
    rightStatusContainer: {
      position: 'absolute',
      top: '20px',
      right: '20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-end',
      gap: '8px',
      zIndex: 10,
    },
    statusLedContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      backgroundColor: 'rgba(12, 15, 29, 0.85)',
      padding: '6px 12px',
      borderRadius: '20px',
      border: '1px solid #1e293b',
      backdropFilter: 'blur(4px)',
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
      backgroundColor: 'rgba(12, 15, 29, 0.85)',
      padding: '6px 14px',
      borderRadius: '20px',
      border: isVoiceActive ? '1px solid #ef4444' : '1px solid #1e293b',
      boxShadow: isVoiceActive ? '0 0 12px rgba(239, 68, 68, 0.4)' : 'none',
      backdropFilter: 'blur(4px)',
      width: '150px',
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
      // Smooth CSS transitions bridge the gap between rapid API polls
      transition: 'width 0.15s ease-out', 
    }
  };

  const columns = ['A', 'B', 'C', 'D'];
  const rows = ['4', '3', '2', '1'];

  return (
    <div style={styles.container}>
      {/* SIDEBAR: Thumbnails */}
      <div style={styles.sidebar}>
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

      {/* MONITOR AREA */}
      <div style={styles.mainContent}>
        <div style={styles.metaOverlay}>
          <div>CURRENT VIEW</div>
          <div style={{ color: '#fff', fontSize: '1.1rem', fontWeight: 'bold' }}>
            {currentSlice.sliceName || 'Waiting for signal...'}
          </div>
          <div style={{ color: '#64748b', marginTop: '5px' }}>
            INDEX: {currentSlice.index}<br />
            MODE: MPR 2D<br />
            GRID: 4x4 (A1-D4)
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

        {/* CT image with cleaned 4x4 chessboard grid */}
        {currentSlice.imageUrl ? (
          <div style={styles.imageContainer}>
            <img
              src={currentSlice.imageUrl}
              alt="Active CT Slice"
              style={styles.activeImage}
              key={currentSlice.index}
            />
            <div style={styles.gridOverlay}>
              {rows.map((row, rowIndex) =>
                columns.map((col, colIndex) => {
                  const isRightEdge = col === 'D';
                  const isBottomEdge = row === '4';
                  
                  // Row labels (1-4) on the left edge only
                  const showRowLabel = colIndex === 0;
                  // Column labels (A-D) on the bottom edge only
                  const showColLabel = rowIndex === 3;

                  return (
                    <div
                      key={`${col}${row}`}
                      style={{
                        ...styles.gridCell,
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
          <div style={{ color: '#475569', fontSize: '1.2rem', letterSpacing: '1px' }}>
            NO IMAGE STREAM SIGNAL
          </div>
        )}
      </div>
    </div>
  );
}

export default App;