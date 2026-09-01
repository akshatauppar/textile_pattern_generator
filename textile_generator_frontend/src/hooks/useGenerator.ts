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
  }, []);

  // Poll generation status when pendingId is active
  useEffect(() => {
    if (state.pendingId === null) return;

    let isMounted = true;
    let pollInterval: any;

    const pollStatus = async () => {
      try {
        const statusData = await getGenerationStatus(state.pendingId!);
        if (!isMounted) return;

        if (statusData.status === 'completed') {
          const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
          setState((prev) => ({
            ...prev,
            previewUrl: `${baseUrl}${statusData.image_url}`,
            loading: false,
            pendingId: null,
            status: statusData,
          }));
          toast.success('Pattern ready!');
          clearInterval(pollInterval);
        } else if (statusData.status === 'failed') {
          setState((prev) => ({
            ...prev,
            loading: false,
            pendingId: null,
            status: statusData,
          }));
          toast.error(statusData.error_message || 'Generation failed');
          clearInterval(pollInterval);
        } else {
          setState((prev) => ({
            ...prev,
            status: statusData,
          }));
        }
      } catch (err) {
        console.error('[useGenerator] Error polling status:', err);
      }
    };

    // Poll immediately, then every 3 seconds
    pollStatus();
    pollInterval = setInterval(pollStatus, 3000);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [state.pendingId]);

  const generate = useCallback(async (payload: GenerationRequest) => {
    setState((prev) => ({ ...prev, loading: true, previewUrl: null, pendingId: null }));
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
        // For SDXL/LoRA, start generation and save the pending ID
        result = await startGeneration(payload);
        setState((prev) => ({
          ...prev,
          pendingId: result.id,
          loading: true,
          status: result,
        }));
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
