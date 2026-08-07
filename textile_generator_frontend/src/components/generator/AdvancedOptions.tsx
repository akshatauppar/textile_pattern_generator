import { Disclosure } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface Props {
  steps: number;
  guidance: number;
  seed: number | null;
  onStepsChange: (val: number) => void;
  onGuidanceChange: (val: number) => void;
  onSeedChange: (val: number | null) => void;
}

export function AdvancedOptions({ steps, guidance, seed, onStepsChange, onGuidanceChange, onSeedChange }: Props) {
  return (
    <Disclosure>
      {({ open }) => (
        <div className="rounded-xl border border-slate-200 bg-white/80 shadow-sm">
          <Disclosure.Button className="flex w-full items-center justify-between px-4 py-3 text-sm font-semibold text-slate-700">
            Advanced options
            <ChevronDownIcon className={`h-5 w-5 text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`} />
          </Disclosure.Button>
          <Disclosure.Panel className="border-t border-slate-200 px-4 py-3 space-y-4 text-sm text-slate-700">
            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1">
                <span className="text-xs text-slate-500">Steps</span>
                <input
                  type="number"
                  value={steps}
                  onChange={(e) => onStepsChange(Number(e.target.value))}
                  min={10}
                  max={50}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
                />
              </label>
              <label className="space-y-1">
                <span className="text-xs text-slate-500">Guidance</span>
                <input
                  type="number"
                  step="0.1"
                  value={guidance}
                  onChange={(e) => onGuidanceChange(Number(e.target.value))}
                  min={1}
                  max={15}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
                />
              </label>
            </div>
            <label className="space-y-1 block">
              <span className="text-xs text-slate-500">Seed (optional)</span>
              <input
                type="number"
                value={seed ?? ''}
                onChange={(e) => onSeedChange(e.target.value ? Number(e.target.value) : null)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
                placeholder="Random if empty"
              />
            </label>
          </Disclosure.Panel>
        </div>
      )}
    </Disclosure>
  );
}
