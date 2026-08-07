import { useCallback, useEffect, useMemo, useState } from 'react';
import { getGenerationStatus, getStyles, startGeneration } from '../services/api';
import { startTextureGANGeneration } from '../services/api.texturegan';
import { USE_TEXTUREGAN } from '../config/apiToggle';
// import { socketService } from '../services/socketService';
import type { GenerationRequest, GenerationStatus, StyleOption } from '../types';
import toast from 'react-hot-toast';

interface GeneratorState {
  styles: StyleOption[];
  loading: boolean;
  pendingId: number | null;
  previewUrl: string | null;
  status: GenerationStatus | null;
}

export function useGenerator() {
  const [state, setState] = useState<GeneratorState>({
    styles: [],
    loading: false,
    pendingId: null,
    previewUrl: null,
    status: null,
  });

  useEffect(() => {
    getStyles()
      .then((styles) => setState((prev) => ({ ...prev, styles })))
      .catch(() => toast.error('Unable to load styles'));
    
    // TEMP: Disable WebSocket for TextureGAN backend
    // socketService.connect();
    // return () => { socketService.disconnect(); };
    return () => {};
  }, []);

  // TEMP: Disable WebSocket updates for TextureGAN backend
  // useEffect(() => { ... }, [state.pendingId]);

  // TEMP: Use direct HTTP for TextureGAN backend
  const generate = useCallback(async (payload: GenerationRequest) => {
    setState((prev) => ({ ...prev, loading: true, previewUrl: null }));
    try {
      let result: any;
      if (USE_TEXTUREGAN) {
        result = await startTextureGANGeneration(payload);
        if (result.results && result.results[0]?.image_base64) {
          setState((prev) => ({
            ...prev,
            previewUrl: `data:image/png;base64,${result.results[0].image_base64}`,
            loading: false,
            status: { ...prev.status, status: 'completed' } as GenerationStatus
          }));
          toast.success('Pattern ready');
        } else {
          throw new Error('No image returned');
        }
        return result;
      } else {
        // For SDXL/LoRA, just start generation and return the result (id)
        result = await startGeneration(payload);
        // Do not expect image in response, just return result (should contain id)
        setState((prev) => ({ ...prev, loading: false }));
        return result;
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Generation failed';
      toast.error(message);
      setState((prev) => ({ ...prev, loading: false }));
      return null;
    }
  }, []);

  const defaultStyle = useMemo(() => state.styles[0]?.id || 'bandhani', [state.styles]);

  return {
    ...state,
    defaultStyle,
    generate,
  };
}
