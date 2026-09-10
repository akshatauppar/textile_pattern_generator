interface Props {
  primary: string;
  secondary: string;
  onPrimaryChange: (val: string) => void;
  onSecondaryChange: (val: string) => void;
}

const indianPalettes = [
  { name: 'Bandhani Sindhoor', primary: '#881337', secondary: '#F59E0B' },
  { name: 'Indigo Royal', primary: '#1E3A8A', secondary: '#FEF08A' },
  { name: 'Peacock & Ochre', primary: '#0F766E', secondary: '#FBBF24' },
  { name: 'Terracotta & Ivory', primary: '#C2410C', secondary: '#FEF3C7' },
  { name: 'Zardozi Plum', primary: '#581C87', secondary: '#FDE047' },
  { name: 'Ajrakh Crimson', primary: '#991B1B', secondary: '#1E293B' },
];

export function ColorPicker({ primary, secondary, onPrimaryChange, onSecondaryChange }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          Color Palette <span className="text-xs font-normal text-slate-400">(Figure 5.6)</span>
        </label>
        <span className="text-xs text-slate-500 dark:text-slate-400">Primary & Secondary</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Primary Color */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-800/70 p-2.5 flex items-center gap-3">
          <input
            type="color"
            value={primary}
            onChange={(e) => onPrimaryChange(e.target.value)}
            className="h-9 w-9 rounded-xl border-0 cursor-pointer bg-transparent p-0"
          />
          <div className="truncate">
            <span className="text-[10px] uppercase font-bold text-slate-400 block leading-tight">Primary</span>
            <span className="text-xs font-mono font-semibold text-slate-800 dark:text-slate-200">{primary}</span>
          </div>
        </div>

        {/* Secondary Color */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-800/70 p-2.5 flex items-center gap-3">
          <input
            type="color"
            value={secondary}
            onChange={(e) => onSecondaryChange(e.target.value)}
            className="h-9 w-9 rounded-xl border-0 cursor-pointer bg-transparent p-0"
          />
          <div className="truncate">
            <span className="text-[10px] uppercase font-bold text-slate-400 block leading-tight">Secondary</span>
            <span className="text-xs font-mono font-semibold text-slate-800 dark:text-slate-200">{secondary}</span>
          </div>
        </div>
      </div>

      {/* Preset Swatches */}
      <div className="space-y-1.5 pt-1">
        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">
          Heritage Color Themes:
        </span>
        <div className="flex flex-wrap gap-2">
          {indianPalettes.map((pal) => (
            <button
              key={pal.name}
              type="button"
              onClick={() => {
                onPrimaryChange(pal.primary);
                onSecondaryChange(pal.secondary);
              }}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-100 dark:bg-slate-800 hover:scale-105 transition-all text-xs border border-slate-200 dark:border-slate-700"
              title={pal.name}
            >
              <span className="h-3 w-3 rounded-full border border-black/10 shadow-sm" style={{ backgroundColor: pal.primary }} />
              <span className="h-3 w-3 rounded-full border border-black/10 shadow-sm" style={{ backgroundColor: pal.secondary }} />
              <span className="text-[10px] font-medium text-slate-700 dark:text-slate-300">{pal.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
