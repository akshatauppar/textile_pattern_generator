import clsx from 'clsx';
import type { StyleId } from '../../types';

const styles: { id: StyleId; name: string; icon: string; description: string }[] = [
  { id: 'bandhani', name: 'Bandhani', icon: '🎯', description: 'Tie-dye circular motifs' },
  { id: 'batik', name: 'Batik', icon: '🎨', description: 'Wax-resist dye art' },
  { id: 'ikat', name: 'Ikat', icon: '⚡', description: 'Blurred resist weaves' },
  { id: 'block_print', name: 'Block Print', icon: '🪵', description: 'Hand-carved wood stamps' },
  { id: 'paisley', name: 'Paisley', icon: '🍃', description: 'Curved kalka swirls' },
];

interface Props {
  value: StyleId;
  onChange: (style: StyleId) => void;
}

export function StyleSelector({ value, onChange }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">Textile Style</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">Select artisanal technique</p>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
        {styles.map((style) => {
          const active = value === style.id;
          return (
            <button
              key={style.id}
              type="button"
              onClick={() => onChange(style.id)}
              className={clsx(
                'w-full text-left rounded-2xl border p-3 transition-all',
                'shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary-500',
                active
                  ? 'border-primary-500 bg-primary-50/80 text-primary-800 dark:border-primary-500 dark:bg-primary-950/40 dark:text-primary-300 ring-2 ring-primary-500/20'
                  : 'border-slate-200 bg-white/80 text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800/80 dark:text-slate-300',
              )}
            >
              <div className="flex items-center gap-2.5">
                <span className="text-2xl p-1.5 rounded-xl bg-slate-100 dark:bg-slate-700/60">{style.icon}</span>
                <div className="truncate">
                  <p className="text-xs font-bold leading-tight truncate">{style.name}</p>
                  <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate mt-0.5">{style.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
