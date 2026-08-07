import { forwardRef } from 'react';

interface Props {
  value: string;
  onChange: (val: string) => void;
}

export const PromptInput = forwardRef<HTMLTextAreaElement, Props>(({ value, onChange }, ref) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-700">Prompt</p>
        <p className="text-xs text-slate-500">Describe the pattern</p>
      </div>
      <div className="relative">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="e.g., intricate paisley with gold filigree and midnight blue background"
          className="w-full rounded-xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-800 shadow-sm focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
          rows={3}
        />
        <div className="absolute right-3 bottom-3 text-xs text-slate-400">{value.length}/320</div>
      </div>
    </div>
  );
});
PromptInput.displayName = 'PromptInput';
