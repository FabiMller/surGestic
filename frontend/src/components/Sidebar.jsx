import React from 'react';
import styles from '../styles/styles';
import ThumbnailList from './ThumbnailList';
import AiPanel from './AiPanel';

export default function Sidebar({ slices, currentIndex }) {
  return (
    <div style={styles.sidebar}>
      <div style={{ ...styles.sidebarHeader, padding: '15px 10px 5px 15px' }}>
        CT Slices ({slices.length})
      </div>

      <ThumbnailList slices={slices} currentIndex={currentIndex} />
      <AiPanel sliceIndex={currentIndex} />
    </div>
  );
}
