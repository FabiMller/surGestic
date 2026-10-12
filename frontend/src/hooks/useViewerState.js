import { useState, useEffect } from 'react';

export default function useViewerState() {
  const [currentSlice, setCurrentSlice] = useState({ index: 0, imageUrl: '', sliceName: '' });
  const [allSlices, setAllSlices] = useState([]);
  const [backendError, setBackendError] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [micLevel, setMicLevel] = useState(0);
  const [selectedCell, setSelectedCell] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [imageOffset, setImageOffset] = useState({ x: 0, y: 0 });
  const [zoomOrigin, setZoomOrigin] = useState({ x: 50, y: 50 });

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/current-slice');
        if (!response.ok) throw new Error('API Error');

        const data = await response.json();

        if (data.all_slices && data.all_slices.length > 0) {
          const sortedSlices = [...data.all_slices].sort((a, b) =>
            a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' })
          );
          setAllSlices(sortedSlices);
        }

        setCurrentSlice({
          index: data.index,
          imageUrl: data.image_url,
          sliceName: data.slice_name,
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

  return {
    currentSlice,
    allSlices,
    backendError,
    isVoiceActive,
    micLevel,
    selectedCell,
    zoomLevel,
    imageOffset,
    zoomOrigin,
  };
}
