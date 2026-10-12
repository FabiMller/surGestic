import React, { useEffect, useRef } from 'react';
import styles from '../styles/styles';

export default function ThumbnailList({ slices, currentIndex }) {
  const thumbnailRefs = useRef({});

  useEffect(() => {
    if (thumbnailRefs.current[currentIndex]) {
      thumbnailRefs.current[currentIndex].scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [currentIndex]);

  return (
    <div style={styles.slicesSection}>
      {slices.map((sliceName, idx) => {
        const isActive = idx === currentIndex;
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
  );
}
