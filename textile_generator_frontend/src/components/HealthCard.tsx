import { useEffect, useState } from 'react';
import { getHealth } from '../services/api';
import type { ApiHealth } from '../types';
import { motion } from 'framer-motion';

export function HealthCard() {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setError('API unreachable'));
  }, []);

  const statusColor = health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="card-surface rounded-2xl p-4 text-sm text-slate-700 dark:text-slate-200 flex items-center justify-between"
    >
      <div className="flex items-center gap-3">
        <span className={`h-2.5 w-2.5 rounded-full ${statusColor}`} />
        <div>
          <p className="font-semibold text-slate-900 dark:text-slate-100">Backend status</p>
          {error ? <p className="text-amber-600">{error}</p> : <p className="text-slate-500 dark:text-slate-300">{health ? health.status : 'Checking...'}</p>}
        </div>
      </div>
      <div className="flex gap-2 text-xs text-slate-500 dark:text-slate-300">
        <span className="px-2 py-1 rounded-full bg-slate-100">Model: {health?.model_loaded ? 'loaded' : 'cold'}</span>
        <span className="px-2 py-1 rounded-full bg-slate-100">DB: {health?.database || '...'}</span>
      </div>
    </motion.div>
  );
}
