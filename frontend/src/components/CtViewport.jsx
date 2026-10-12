import React from 'react';
import styles from '../styles/styles';
import GridOverlay from './GridOverlay';

export default function CtViewport({
  imageUrl,
  sliceIndex,
  zoomLevel,
  imageOffset,
  zoomOrigin,
  selectedCell,
}) {
  return (
    <div style={styles.imageArea}>
      {imageUrl ? (
        <div style={styles.imageContainer}>
          <img
            src={imageUrl}
            alt="Active CT Slice"
            style={{
              ...styles.activeImage,
              transform: `translate(${imageOffset.x}%, ${imageOffset.y}%) scale(${zoomLevel})`,
              transformOrigin: `${zoomOrigin.x}% ${zoomOrigin.y}%`,
            }}
            key={sliceIndex}
          />
          <GridOverlay selectedCell={selectedCell} />
        </div>
      ) : (
        <div style={{ color: '#475569', fontSize: '1.2rem', letterSpacing: '1px', fontFamily: 'monospace' }}>
          NO IMAGE STREAM SIGNAL
        </div>
      )}
    </div>
  );
}
