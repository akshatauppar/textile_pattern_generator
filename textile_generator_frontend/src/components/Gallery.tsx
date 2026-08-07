import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { UpscaleButton } from './UpscaleButton';
import { DownloadButton } from './DownloadButton';
import toast from 'react-hot-toast';

interface GalleryItem {
  id: number;
  prompt: string;
  image_url: string;
  created_at: string;
  current_url?: string;
}

export function Gallery() {
  const { token } = useAuth();
  const [generations, setGenerations] = useState<GalleryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (token) {
      fetchHistory();
    }
  }, [token]);

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGenerations(response.data.generations);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to load history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpscaleComplete = (generationId: number, newUrl: string, scale: number) => {
    setGenerations(gens =>
      gens.map(gen =>
        gen.id === generationId ? { ...gen, current_url: newUrl } : gen
      )
    );
    toast.success(`Upscaled to ${scale}×`);
  };

  if (!token) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 dark:text-slate-300">Sign in to view your generation history</p>
      </div>
    );
  }

  if (isLoading) {
    return <div className="text-center py-12">Loading history...</div>;
  }

  if (generations.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No generations yet. Create one to get started!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {generations.map(gen => (
        <div key={gen.id} className="card-surface rounded-lg overflow-hidden hover:shadow-xl transition-shadow">
          <img
            src={gen.current_url || gen.image_url}
            alt={gen.prompt}
            className="w-full h-64 object-cover"
          />
          <div className="p-4">
            <p className="text-sm text-slate-600 line-clamp-2 mb-3">{gen.prompt}</p>
            <div className="flex gap-2">
              <UpscaleButton
                generationId={gen.id}
                currentUrl={gen.current_url || gen.image_url}
                onUpscaleComplete={(url) => handleUpscaleComplete(gen.id, url, 2)}
              />
              <DownloadButton
                imageUrl={gen.current_url || gen.image_url}
                filename={`textile_pattern_${gen.id}.png`}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
