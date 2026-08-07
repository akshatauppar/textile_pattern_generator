import { ArrowDownTrayIcon } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';

interface DownloadButtonProps {
  imageUrl: string;
  filename: string;
}

export function DownloadButton({ imageUrl, filename }: DownloadButtonProps) {
  const handleDownload = async () => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Downloaded successfully');
    } catch (error) {
      toast.error('Download failed');
    }
  };

  return (
    <button
      onClick={handleDownload}
      className="flex items-center gap-2 px-3 py-1.5 bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium hover:bg-slate-300 transition-all"
    >
      <ArrowDownTrayIcon className="w-4 h-4" />
      Download
    </button>
  );
}
