import { useCallback, useEffect, useMemo, useState } from 'react';
import { getStyles } from '../services/api';
import { startTextureGANGeneration } from '../services/api.texturegan';
import { USE_TEXTUREGAN } from '../config/apiToggle';
import type { GenerationRequest, GenerationStatus, StyleOption } from '../types';
import toast from 'react-hot-toast';

interface GeneratorState {
  styles: StyleOption[];
  loading: boolean;
  pendingId: number | null;
  previewUrl: string | null;
  status: GenerationStatus | null;
}

export function useTextureGANGenerator() {
  const [state, setState] = useState<GeneratorState>({
    styles: [],
    loading: false,
    pendingId: null,
    previewUrl: null,
    status: null,
  });

  useEffect(() => {
    // Use the real API for styles if not TextureGAN, else stub
    if (USE_TEXTUREGAN) {
      setState((prev) => ({
        ...prev,
        styles: [
          { id: 'default', name: 'Default', description: 'Default GAN style' },
          { id: 'gan', name: 'GAN', description: 'GAN-based pattern' },
        ],
      }));
    } else {
      getStyles()
        .then((styles) => setState((prev) => ({ ...prev, styles })))
        .catch(() => toast.error('Unable to load styles'));
    }
  }, []);

  const generate = useCallback(async (payload: GenerationRequest) => {
    setState((prev) => ({ ...prev, loading: true, previewUrl: null }));
    try {
      // Ensure color fields are always arrays for TextureGAN
      const safePayload = {
        ...payload,
        primary_color: Array.isArray(payload.primary_color)
          ? payload.primary_color
          : [255, 255, 255],
        secondary_color: Array.isArray(payload.secondary_color)
          ? payload.secondary_color
          : [0, 0, 0],
      };
      const result = await startTextureGANGeneration(safePayload);
      if (result.results && result.results[0]?.image_base64) {
        setState((prev) => ({
          ...prev,
          previewUrl: `data:image/png;base64,${result.results[0].image_base64}`,
          loading: false,
          status: { ...prev.status, status: 'completed' } as GenerationStatus,
        }));
        toast.success('Pattern ready');
      } else {
        throw new Error('No image returned');
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Generation failed';
      toast.error(message);
      setState((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  const defaultStyle = useMemo(() => state.styles[0]?.id || 'default', [state.styles]);

  return {
    ...state,
    defaultStyle,
    generate,
  };
}
