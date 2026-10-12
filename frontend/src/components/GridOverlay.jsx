import React from 'react';
import styles from '../styles/styles';

const columns = ['A', 'B', 'C', 'D'];
const rows = ['4', '3', '2', '1'];

export default function GridOverlay({ selectedCell }) {
  return (
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
  );
}
