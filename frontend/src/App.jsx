import React from 'react';
import styles from './styles/styles';
import useViewerState from './hooks/useViewerState';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import CtViewport from './components/CtViewport';

function App() {
  const patientId = 'TEST-ID-12345678';
  const {
    currentSlice,
    allSlices,
    backendError,
    isVoiceActive,
    micLevel,
    selectedCell,
    zoomLevel,
    imageOffset,
    zoomOrigin,
  } = useViewerState();

  return (
    <div style={styles.container}>
      <Sidebar slices={allSlices} currentIndex={currentSlice.index} />

      <div style={styles.mainContent}>
        <TopBar
          patientId={patientId}
          sliceName={currentSlice.sliceName}
          sliceIndex={currentSlice.index}
          zoomLevel={zoomLevel}
          selectedCell={selectedCell}
          backendError={backendError}
          isVoiceActive={isVoiceActive}
          micLevel={micLevel}
        />

        <CtViewport
          imageUrl={currentSlice.imageUrl}
          sliceIndex={currentSlice.index}
          zoomLevel={zoomLevel}
          imageOffset={imageOffset}
          zoomOrigin={zoomOrigin}
          selectedCell={selectedCell}
        />
      </div>
    </div>
  );
}

export default App;
