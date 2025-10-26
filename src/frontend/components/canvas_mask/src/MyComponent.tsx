import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Streamlit, withStreamlitConnection, ComponentProps } from 'streamlit-component-lib';

interface StreamlitProps extends ComponentProps {
  args: {
    imageUrl: string;
    imageWidth?: number;
    imageHeight?: number;
  };
}

const MyComponent: React.FC<StreamlitProps> = ({ args }) => {
  const imageCanvasRef = useRef<HTMLCanvasElement>(null);
  const drawCanvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [canvasSize, setCanvasSize] = useState({ 
    width: args.imageWidth || 800, 
    height: args.imageHeight || 600 
  });

  // Tell Streamlit we're ready to start receiving data
  useEffect(() => {
    Streamlit.setFrameHeight();
  }, []);

  useEffect(() => {
    const imageCanvas = imageCanvasRef.current;
    const drawCanvas = drawCanvasRef.current;
    
    if (!imageCanvas || !drawCanvas || !args.imageUrl) return;

    const imageCtx = imageCanvas.getContext('2d');
    const drawCtx = drawCanvas.getContext('2d', { willReadFrequently: true });
    
    if (!imageCtx || !drawCtx) return;

    const bgImage = new Image();
    
    bgImage.onload = () => {
      const actualWidth = bgImage.width;
      const actualHeight = bgImage.height;
      
      setCanvasSize({ width: actualWidth, height: actualHeight });
      
      imageCanvas.width = drawCanvas.width = actualWidth;
      imageCanvas.height = drawCanvas.height = actualHeight;
      
      imageCtx.drawImage(bgImage, 0, 0);

      drawCtx.strokeStyle = 'rgba(0, 150, 255, 0.7)';
      drawCtx.lineWidth = 25;
      drawCtx.lineCap = 'round';
      drawCtx.lineJoin = 'round';
      
      // Update Streamlit frame height after image loads
      Streamlit.setFrameHeight();
    };
    
    bgImage.src = args.imageUrl;
  }, [args.imageUrl]);

  const getMousePos = useCallback((canvas: HTMLCanvasElement, evt: MouseEvent) => {
    const rect = canvas.getBoundingClientRect();
    return { x: evt.clientX - rect.left, y: evt.clientY - rect.top };
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const drawCanvas = drawCanvasRef.current;
    const drawCtx = drawCanvas?.getContext('2d', { willReadFrequently: true });
    
    if (!drawCanvas || !drawCtx) return;
    
    setIsDrawing(true);
    const pos = getMousePos(drawCanvas, e.nativeEvent);
    drawCtx.beginPath();
    drawCtx.moveTo(pos.x, pos.y);
  }, [getMousePos]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    
    const drawCanvas = drawCanvasRef.current;
    const drawCtx = drawCanvas?.getContext('2d', { willReadFrequently: true });
    
    if (!drawCanvas || !drawCtx) return;
    
    const pos = getMousePos(drawCanvas, e.nativeEvent);
    drawCtx.lineTo(pos.x, pos.y);
    drawCtx.stroke();
  }, [isDrawing, getMousePos]);

  const handleMouseUp = useCallback(() => {
    setIsDrawing(false);
  }, []);

  const handleMouseOut = useCallback(() => {
    setIsDrawing(false);
  }, []);

  const confirmMask = useCallback(() => {
    const drawCanvas = drawCanvasRef.current;
    const drawCtx = drawCanvas?.getContext('2d', { willReadFrequently: true });
    
    if (!drawCanvas || !drawCtx) return;

    // Create a new canvas to generate the black and white mask
    const maskCanvas = document.createElement('canvas');
    maskCanvas.width = drawCanvas.width;
    maskCanvas.height = drawCanvas.height;
    const maskCtx = maskCanvas.getContext('2d');
    
    if (!maskCtx) return;

    const drawingData = drawCtx.getImageData(0, 0, drawCanvas.width, drawCanvas.height);
    const pixels = drawingData.data;
    const maskImageData = maskCtx.createImageData(drawCanvas.width, drawCanvas.height);
    const maskPixels = maskImageData.data;

    for (let i = 0; i < pixels.length; i += 4) {
      if (pixels[i + 3] > 0) { // If pixel has been drawn on
        maskPixels[i] = 255; 
        maskPixels[i + 1] = 255; 
        maskPixels[i + 2] = 255; 
        maskPixels[i + 3] = 255;
      } else {
        maskPixels[i] = 0; 
        maskPixels[i + 1] = 0; 
        maskPixels[i + 2] = 0; 
        maskPixels[i + 3] = 255;
      }
    }
    
    maskCtx.putImageData(maskImageData, 0, 0);
    const maskDataUrl = maskCanvas.toDataURL('image/png');
    
    console.log("Mask Data ready");
    
    // Send the confirmed mask data to Streamlit
    Streamlit.setComponentValue(maskDataUrl);
    console.log("Mask Data sent to Streamlit");
  }, []);

  const clearCanvas = useCallback(() => {
    const drawCanvas = drawCanvasRef.current;
    const drawCtx = drawCanvas?.getContext('2d', { willReadFrequently: true });
    
    if (!drawCanvas || !drawCtx) return;
    
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
  }, []);

  return (
    <div style={{ 
      margin: 0, 
      padding: 0, 
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div 
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: `${canvasSize.width}px`,
          maxHeight: `${canvasSize.height}px`,
          border: '1px solid #ccc',
          margin: 'auto',
          height: `${canvasSize.height}px`
        }}
      >
        <canvas 
          ref={imageCanvasRef}
          style={{ position: 'absolute', top: 0, left: 0 }}
        />
        <canvas 
          ref={drawCanvasRef}
          style={{ position: 'absolute', top: 0, left: 0, cursor: 'crosshair' }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseOut={handleMouseOut}
        />
      </div>
      
      <div style={{ marginTop: '10px' }}>
        <button
          onClick={confirmMask}
          style={{
            marginRight: '10px',
            padding: '8px 16px',
            fontSize: '16px',
            cursor: 'pointer',
            borderRadius: '5px',
            border: '1px solid #4F8BF9',
            backgroundColor: '#4F8BF9',
            color: 'white'
          }}
        >
          Confirm Mask
        </button>
        
        <button
          onClick={clearCanvas}
          style={{
            padding: '8px 16px',
            fontSize: '16px',
            cursor: 'pointer',
            borderRadius: '5px',
            border: '1px solid #f44336',
            backgroundColor: '#f44336',
            color: 'white'
          }}
        >
          Clear
        </button>
      </div>
    </div>
  );
};

export default withStreamlitConnection(MyComponent);