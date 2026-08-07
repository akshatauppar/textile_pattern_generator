interface Props {
  primary: string;
  secondary: string;
  onPrimaryChange: (val: string) => void;
  onSecondaryChange: (val: string) => void;
}

export function ColorPicker({ primary, secondary, onPrimaryChange, onSecondaryChange }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-700">Colors</p>
        <p className="text-xs text-slate-500">Optional</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <label className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">
          <input
            type="color"
            value={primary}
            onChange={(e) => onPrimaryChange(e.target.value)}
            className="h-9 w-9 rounded-lg border border-slate-200 cursor-pointer"
            aria-label="Primary color"
          />
          <div>
            <p className="font-semibold">Primary</p>
            <p className="text-xs text-slate-500">Accent tone</p>
          </div>
        </label>
        <label className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">
          <input
            type="color"
            value={secondary}
            onChange={(e) => onSecondaryChange(e.target.value)}
            className="h-9 w-9 rounded-lg border border-slate-200 cursor-pointer"
            aria-label="Secondary color"
          />
          <div>
            <p className="font-semibold">Secondary</p>
            <p className="text-xs text-slate-500">Support tone</p>
          </div>
        </label>
      </div>
    </div>
  );
}
