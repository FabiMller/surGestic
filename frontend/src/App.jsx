import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [currentSlice, setCurrentSlice] = useState({ index: 0, imageUrl: '', sliceName: '' });
  const [allSlices, setAllSlices] = useState([]);
  const [backendError, setBackendError] = useState(false);
  const thumbnailRefs = useRef({});

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/current-slice');
        if (!response.ok) throw new Error('API Fehler');
        
        const data = await response.json();
        
        if (data.all_slices) {
          setAllSlices(data.all_slices);
        }

        setCurrentSlice({
          index: data.index,
          imageUrl: data.image_url,
          sliceName: data.slice_name
        });
        setBackendError(false);
      } catch (error) {
        setBackendError(true);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  // automatic scroll to the active thumbnail in the sidebar when the current slice changes
  useEffect(() => {
    if (thumbnailRefs.current[currentSlice.index]) {
      thumbnailRefs.current[currentSlice.index].scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [currentSlice.index]);

  // Styles for the components
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
    activeImage: {
      maxHeight: '92vh',
      maxWidth: '95%',
      objectFit: 'contain',
      display: 'block',
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
    },
    statusLedContainer: {
      position: 'absolute',
      top: '20px',
      right: '20px',
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
    }
  };

  return (
    <div style={styles.container}>
      {/* LINKSEITE: Rechteckige Miniaturansichten untereinander */}
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
              {/* Zweistellige Formatierung in JavaScript korrigiert */}
              <div style={styles.thumbnailLabel}># {String(idx).padStart(2, '0')}</div>
            </div>
          );
        })}
      </div>

      {/* RECHTS / MITTE: Haupt-OP-Monitor */}
      <div style={styles.mainContent}>
        {/* Medizinische Metadaten oben links */}
        <div style={styles.metaOverlay}>
          <div>CURRENT VIEW</div>
          <div style={{ color: '#fff', fontSize: '1.1rem', fontWeight: 'bold' }}>
            {currentSlice.sliceName || 'Warte auf Signal...'}
          </div>
          <div style={{ color: '#64748b', marginTop: '5px' }}>
            INDEX: {currentSlice.index}<br />
            MODE: MPR 2D<br />
            ZOOM: FIT
          </div>
        </div>

        {/* Server Status LED oben rechts */}
        <div style={styles.statusLedContainer}>
          <div style={styles.statusLed}></div>
          <span style={{ color: backendError ? '#ef4444' : '#10b981' }}>
            {backendError ? 'SERVER DISCONNECTED' : 'SERVER ONLINE'}
          </span>
        </div>

        {/* Das große ausgewählte Hauptbild */}
        {currentSlice.imageUrl ? (
          <img
            src={currentSlice.imageUrl}
            alt="Ausgewähltes CT Bild"
            style={styles.activeImage}
            key={currentSlice.index} // 🔥 Das 'key' Attribut zwingt React das Bild sofort neu zu rendern!
          />
        ) : (
          <div style={{ color: '#475569', fontSize: '1.2rem', letterSpacing: '1px' }}>
            KEIN BILDSTREAMSIGNAL
          </div>
        )}
      </div>
    </div>
  );
}

export default App;