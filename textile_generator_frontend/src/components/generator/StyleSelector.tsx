import clsx from 'clsx';
import type { StyleId } from '../../types';

const styles: { id: StyleId; name: string; icon: string; description: string }[] = [
  { id: 'bandhani', name: 'Bandhani', icon: '🎯', description: 'Tie-dye circular motifs' },
  { id: 'batik', name: 'Batik', icon: '🎨', description: 'Wax-resist dyeing' },
  { id: 'ikat', name: 'Ikat', icon: '⚡', description: 'Blurred resist dye' },
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
        <p className="text-xs text-slate-500 dark:text-slate-400">Pick one</p>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {styles.map((style) => {
          const active = value === style.id;
          return (
            <button
              key={style.id}
              type="button"
              onClick={() => onChange(style.id)}
              className={clsx(
                'w-full text-left rounded-xl border px-4 py-3 transition-all',
                'shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary-500',
                active
                  ? 'border-primary-200 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-900/20 dark:text-primary-300'
                  : 'border-slate-200 bg-white text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300',
              )}
            >
              <div className="flex flex-col items-center gap-2">
                <span className="text-2xl">{style.icon}</span>
                <div className="text-center">
                  <p className="text-sm font-semibold">{style.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{style.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
