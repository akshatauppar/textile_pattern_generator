import { Disclosure } from '@headlessui/react';
import { ChevronDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface Props {
  steps: number;
  guidance: number;
  seed: number | null;
  imageSize: number;
  onStepsChange: (val: number) => void;
  onGuidanceChange: (val: number) => void;
  onSeedChange: (val: number | null) => void;
  onImageSizeChange: (val: number) => void;
}

export function AdvancedOptions({
  steps,
  guidance,
  seed,
  imageSize,
  onStepsChange,
  onGuidanceChange,
  onSeedChange,
  onImageSizeChange,
}: Props) {
  const randomizeSeed = () => {
    const random = Math.floor(Math.random() * 2147483647);
    onSeedChange(random);
  };

  return (
    <Disclosure>
      {({ open }) => (
        <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white/60 dark:bg-slate-800/60 shadow-sm overflow-hidden">
          <Disclosure.Button className="flex w-full items-center justify-between px-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            <span>Advanced Model & Checkpoint Settings</span>
            <ChevronDownIcon className={`h-4 w-4 text-slate-500 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
          </Disclosure.Button>
          <Disclosure.Panel className="border-t border-slate-200 dark:border-slate-700 px-4 py-3 space-y-3.5 text-xs text-slate-700 dark:text-slate-300">
            {/* Resolution Selector */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">Synthesis Resolution</span>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { size: 256, label: '256×256 (Trained)' },
                  { size: 512, label: '512×512 (Standard)' },
                  { size: 1024, label: '1024×1024 (HD)' },
                ].map((item) => (
                  <button
                    key={item.size}
                    type="button"
                    onClick={() => onImageSizeChange(item.size)}
                    className={`py-1.5 px-2 rounded-xl text-center text-xs font-semibold border transition-all ${
                      imageSize === item.size
                        ? 'bg-primary-500 text-white border-primary-600 shadow-sm'
                        : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Checkpoint info */}
            <div className="rounded-xl bg-slate-100 dark:bg-slate-900/60 p-2.5 border border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">StyleGAN2-ADA Snapshot:</span>
                <span className="font-mono font-bold text-primary-600 dark:text-primary-400">network-snapshot-000480.pkl</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Kimg ~ 560 (Bandhani dots refined, Batik wax crackle stabilized)
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1 block">
                <span className="text-[11px] font-semibold text-slate-500">Denoising Steps</span>
                <input
                  type="number"
                  value={steps}
                  onChange={(e) => onStepsChange(Math.max(1, Math.min(30, Number(e.target.value))))}
                  min={1}
                  max={30}
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-mono focus:ring-2 focus:ring-primary-500"
                />
              </label>
              <label className="space-y-1 block">
                <span className="text-[11px] font-semibold text-slate-500">Truncation &psi; / Guidance</span>
                <input
                  type="number"
                  step="0.1"
                  value={guidance}
                  onChange={(e) => onGuidanceChange(Number(e.target.value))}
                  min={0}
                  max={15}
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-mono focus:ring-2 focus:ring-primary-500"
                />
              </label>
            </div>

            {/* Seed input */}
            <label className="space-y-1 block">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-500">Latent Seed</span>
                <button
                  type="button"
                  onClick={randomizeSeed}
                  className="text-[11px] text-primary-600 dark:text-primary-400 font-semibold flex items-center gap-1 hover:underline"
                >
                  <ArrowPathIcon className="h-3 w-3" /> Randomize
                </button>
              </div>
              <input
                type="number"
                value={seed ?? ''}
                onChange={(e) => onSeedChange(e.target.value ? Number(e.target.value) : null)}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-mono focus:ring-2 focus:ring-primary-500"
                placeholder="Random seed generated automatically"
              />
            </label>
          </Disclosure.Panel>
        </div>
      )}
    </Disclosure>
  );
}
