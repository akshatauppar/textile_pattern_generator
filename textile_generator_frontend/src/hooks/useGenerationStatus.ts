import { useEffect, useState } from 'react';
import { socketService } from '../services/socketService';

export function useGenerationStatus(generationId: number | null) {
  const [status, setStatus] = useState<'pending' | 'processing' | 'completed' | 'failed'>('pending');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!generationId) return;

    // Connect to WebSocket
    socketService.connect();

    // Join generation room
    socketService.joinGeneration(generationId);

    // Listen for updates
    const handleUpdate = (data: any) => {
      if (data.generation_id === generationId) {
        setStatus(data.status);
        if (data.data?.image_url) {
          setImageUrl(data.data.image_url);
        }
        if (data.data?.error) {
          setError(data.data.error);
        }
      }
    };

    socketService.on('generation_update', handleUpdate);

    return () => {
      socketService.leaveGeneration(generationId);
    };
  }, [generationId]);

  return { status, imageUrl, error };
}
