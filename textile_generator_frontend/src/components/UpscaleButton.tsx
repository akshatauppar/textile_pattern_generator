import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { ArrowUpIcon } from '@heroicons/react/24/solid';

interface UpscaleProps {
  generationId: number;
  currentUrl: string;
  onUpscaleComplete?: (newUrl: string, scale: number) => void;
}

export function UpscaleButton({ generationId, currentUrl, onUpscaleComplete }: UpscaleProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpscale = async (scale: 2 | 4) => {
    try {
      setIsLoading(true);
      const response = await axios.post('/api/upscale', {
        generation_id: generationId,
        scale
      });

      const { upscaled_url, resolution } = response.data;
      toast.success(`Upscaled to ${resolution}`);
      onUpscaleComplete?.(upscaled_url, scale);
      setIsOpen(false);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Upscaling failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all"
        disabled={isLoading}
      >
        <ArrowUpIcon className="w-4 h-4" />
        Upscale
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-32 bg-white border border-slate-200 rounded-lg shadow-lg z-50">
          <button
            onClick={() => handleUpscale(2)}
            disabled={isLoading}
            className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            2× (2048×2048)
          </button>
          <button
            onClick={() => handleUpscale(4)}
            disabled={isLoading}
            className="w-full px-4 py-2 text-left text-sm border-t border-slate-100 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            4× (4096×4096)
          </button>
        </div>
      )}
    </div>
  );
}
