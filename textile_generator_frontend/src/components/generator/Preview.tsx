import { motion } from 'framer-motion';
import type { GenerationStatus } from '../../types';

interface Props {
  previewUrl: string | null;
  status: GenerationStatus | null;
  loading: boolean;
}

export function Preview({ previewUrl, status, loading }: Props) {
  const stateLabel = (() => {
    if (loading) return 'Generating...';
    if (status?.status === 'completed') return 'Completed';
    if (status?.status === 'failed') return 'Failed';
    if (status?.status === 'processing') return 'Processing...';
    return 'Ready to generate';
  })();

  return (
    <div className="card-surface rounded-3xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-primary-600">Preview</p>
          <h2 className="text-xl font-bold text-slate-900">See the result</h2>
        </div>
        <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">Seamless tile</span>
      </div>

      <div className="aspect-square rounded-2xl border border-slate-200 bg-white/70 overflow-hidden relative">
        {previewUrl ? (
          <motion.img
            key={previewUrl}
            src={previewUrl}
            alt="Generated textile"
            initial={{ opacity: 0.4, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 grid place-items-center text-sm text-slate-500">
            <div className="text-center space-y-2">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary-50 to-secondary-50 border border-slate-100 mx-auto" />
              <p>No image yet</p>
            </div>
          </div>
        )}
        {loading && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] grid place-items-center text-sm text-slate-700">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-primary-500 animate-pulse" />
              <span>Generating...</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-sm text-slate-600">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-primary-500" />
          <span>{stateLabel}</span>
        </div>
        {status?.seed && <span className="text-xs text-slate-500">Seed: {status.seed}</span>}
      </div>
    </div>
  );
}
