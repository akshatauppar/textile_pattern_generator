import clsx from 'clsx';
import type { PatternId, PatternOption } from '../../types';

interface Props {
  value: PatternId;
  onChange: (pattern: PatternId) => void;
  patterns: PatternOption[];
}

export function PatternSelector({ value, onChange, patterns }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">Pattern Type</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">Select subtype</p>
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as PatternId)}
        className={clsx(
          'w-full rounded-lg border px-4 py-3 transition-all',
          'shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
          'border-slate-200 bg-white text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200',
          'hover:border-slate-300 dark:hover:border-slate-500'
        )}
      >
        {patterns.map((pattern) => (
          <option key={pattern.id} value={pattern.id}>
            {pattern.name} - {pattern.description}
          </option>
        ))}
      </select>
    </div>
  );
}
