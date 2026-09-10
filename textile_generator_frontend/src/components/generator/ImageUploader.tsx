import { useState, useRef } from 'react';
import { PhotoIcon, XMarkIcon, SparklesIcon } from '@heroicons/react/24/outline';

interface Props {
  referenceImage: string | null;
  onChange: (image: string | null) => void;
}

const sampleReferences = [
  { label: 'Royal Indigo Batik', url: '/static/bandhani_blue.png' },
  { label: 'Bandhani Dot Knot', url: '/static/sample_0_bandhani.png' },
  { label: 'Ikat Chevron Weave', url: '/static/sample_1_ikat.png' },
  { label: 'Emerald Block Print', url: '/static/bandhani_green.png' },
];

export function ImageUploader({ referenceImage, onChange }: Props) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.type.startsWith('image/')) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      onChange(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          Reference Image <span className="text-xs font-normal text-slate-400">(Optional)</span>
        </label>
        <span className="text-[11px] text-slate-500 dark:text-slate-400">
          Style conditioning (Figure 5.7)
        </span>
      </div>

      {referenceImage ? (
        <div className="relative rounded-2xl border border-primary-300 dark:border-primary-700 bg-primary-50/40 dark:bg-primary-950/20 p-3 flex items-center gap-4">
          <img
            src={referenceImage}
            alt="Reference preview"
            className="h-16 w-16 rounded-xl object-cover border border-slate-200 dark:border-slate-700 shadow-sm"
          />
          <div className="flex-1 truncate">
            <p className="text-xs font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <SparklesIcon className="h-4 w-4 text-primary-500" /> Reference Applied
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
              Colors & motif structure will guide the generative process.
            </p>
          </div>
          <button
            type="button"
            onClick={() => onChange(null)}
            className="rounded-xl p-1.5 text-slate-400 hover:text-rose-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Remove reference image"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative rounded-2xl border-2 border-dashed p-4 text-center cursor-pointer transition-all ${
            dragActive
              ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-950/30 scale-[0.99]'
              : 'border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/40 hover:border-primary-400 hover:bg-white dark:hover:bg-slate-800'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png, image/jpeg, image/webp"
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
          <div className="flex flex-col items-center justify-center gap-1.5">
            <div className="h-9 w-9 rounded-xl bg-primary-100/80 dark:bg-primary-900/40 flex items-center justify-center text-primary-600 dark:text-primary-300">
              <PhotoIcon className="h-5 w-5" />
            </div>
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">
              Upload a file or drag and drop
            </p>
            <p className="text-[10px] text-slate-400">PNG, JPG up to 10MB</p>
          </div>
        </div>
      )}

      {/* Quick sample reference chips */}
      {!referenceImage && (
        <div className="flex items-center gap-2 pt-0.5">
          <span className="text-[10px] text-slate-400 whitespace-nowrap">Try samples:</span>
          <div className="flex flex-wrap gap-1.5">
            {sampleReferences.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => onChange(sample.url)}
                className="text-[10px] px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-primary-50 text-slate-600 hover:text-primary-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 transition-all border border-slate-200 dark:border-slate-700"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
