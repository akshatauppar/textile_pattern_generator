import { useEffect } from 'react';
import type { RefObject } from 'react';
import { StyleSelector } from './StyleSelector';
import { ColorPicker } from './ColorPicker';
import { PromptInput } from './PromptInput';
import { AdvancedOptions } from './AdvancedOptions';
import { motion } from 'framer-motion';
import type { StyleId } from '../../types';

interface Props {
  prompt: string;
  style: StyleId;
  primaryColor: string;
  secondaryColor: string;
  steps: number;
  guidance: number;
  seed: number | null;
  loading: boolean;
  promptRef: RefObject<HTMLTextAreaElement>;
  onPrompt: (v: string) => void;
  onStyle: (v: StyleId) => void;
  onPrimary: (v: string) => void;
  onSecondary: (v: string) => void;
  onSteps: (v: number) => void;
  onGuidance: (v: number) => void;
  onSeed: (v: number | null) => void;
  onGenerate: () => void;
  disableGenerate?: boolean;
  stylesLoaded: boolean;
}

export function ControlPanel(props: Props) {
  const {
    prompt,
    style,
    primaryColor,
    secondaryColor,
    steps,
    guidance,
    seed,
    loading,
    onPrompt,
    onStyle,
    onPrimary,
    onSecondary,
    onSteps,
    onGuidance,
    onSeed,
    onGenerate,
    disableGenerate,
    stylesLoaded,
    promptRef,
  } = props;

  useEffect(() => {
    // Could add analytics or focus management here
  }, []);

  return (
    <div className="card-surface rounded-3xl p-6 space-y-6" id="generator">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-primary-600">Generator</p>
          <h2 className="text-xl font-bold text-slate-900">Craft your textile</h2>
        </div>
        <span className="px-3 py-1 rounded-full bg-primary-50 text-primary-700 text-xs font-semibold">1024×1024 seamless</span>
      </div>

      <StyleSelector value={style} onChange={onStyle} />
      <PromptInput ref={promptRef} value={prompt} onChange={onPrompt} />
      <ColorPicker primary={primaryColor} secondary={secondaryColor} onPrimaryChange={onPrimary} onSecondaryChange={onSecondary} />
      <AdvancedOptions steps={steps} guidance={guidance} seed={seed} onStepsChange={onSteps} onGuidanceChange={onGuidance} onSeedChange={onSeed} />

      <div className="flex flex-col gap-3">
        <motion.button
          type="button"
          whileTap={{ scale: 0.98 }}
          disabled={loading || disableGenerate || !stylesLoaded}
          onClick={onGenerate}
          className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold py-3 shadow-lg shadow-primary-500/30 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate pattern'}
        </motion.button>
        <p className="text-xs text-slate-500">Generation takes ~30-60s on first run as the model warms up.</p>
      </div>
    </div>
  );
}
