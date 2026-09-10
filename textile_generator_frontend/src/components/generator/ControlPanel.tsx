import type { RefObject } from 'react';
import { StyleSelector } from './StyleSelector';
import { ImageUploader } from './ImageUploader';
import { ColorPicker } from './ColorPicker';
import { PromptInput } from './PromptInput';
import { AdvancedOptions } from './AdvancedOptions';
import { motion } from 'framer-motion';
import { SparklesIcon, BoltIcon } from '@heroicons/react/24/solid';
import type { StyleId } from '../../types';

interface Props {
  prompt: string;
  style: StyleId;
  primaryColor: string;
  secondaryColor: string;
  steps: number;
  guidance: number;
  seed: number | null;
  imageSize: number;
  referenceImage: string | null;
  loading: boolean;
  promptRef: RefObject<HTMLTextAreaElement>;
  onPrompt: (v: string) => void;
  onStyle: (v: StyleId) => void;
  onPrimary: (v: string) => void;
  onSecondary: (v: string) => void;
  onSteps: (v: number) => void;
  onGuidance: (v: number) => void;
  onSeed: (v: number | null) => void;
  onImageSize: (v: number) => void;
  onReferenceImage: (v: string | null) => void;
  onGenerate: () => void;
  disableGenerate?: boolean;
  stylesLoaded: boolean;
}

const promptSuggestions = [
  'intricate geometric floral pattern with symmetry',
  'royal bandhani tie-dye circular motifs in gold and crimson',
  'batik wax-resist with organic crackle veins and lotus flowers',
  'delicate Jaipuri botanical block print with blooming buta',
  'ornate kashmiri paisley kalka teardrops with zardozi swirls',
];

export function ControlPanel(props: Props) {
  const {
    prompt,
    style,
    primaryColor,
    secondaryColor,
    steps,
    guidance,
    seed,
    imageSize,
    referenceImage,
    loading,
    onPrompt,
    onStyle,
    onPrimary,
    onSecondary,
    onSteps,
    onGuidance,
    onSeed,
    onImageSize,
    onReferenceImage,
    onGenerate,
    disableGenerate,
    stylesLoaded,
    promptRef,
  } = props;

  return (
    <div className="card-surface rounded-3xl p-6 space-y-6 shadow-xl border border-slate-200/80 dark:border-slate-800" id="generator">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-primary-600 dark:text-primary-400 flex items-center gap-1.5">
            <SparklesIcon className="h-3.5 w-3.5" /> Generator Studio
          </span>
          <h2 className="text-2xl font-black text-slate-900 dark:text-slate-100 mt-0.5">
            Craft your textile
          </h2>
        </div>
        <span className="px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/60 border border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300 text-xs font-bold">
          {imageSize}&times;{imageSize} seamless
        </span>
      </div>

      {/* 1. Style Selection (Figure 5.4-5.5) */}
      <StyleSelector value={style} onChange={onStyle} />

      {/* 2. Reference Image Upload (Figure 5.7) */}
      <ImageUploader referenceImage={referenceImage} onChange={onReferenceImage} />

      {/* 3. Prompt Input with Quick Chips */}
      <div className="space-y-2">
        <PromptInput ref={promptRef} value={prompt} onChange={onPrompt} />
        <div className="flex flex-wrap gap-1.5 items-center pt-1">
          <span className="text-[10px] text-slate-400 font-semibold">Try prompt:</span>
          {promptSuggestions.slice(0, 3).map((sugg) => (
            <button
              key={sugg}
              type="button"
              onClick={() => onPrompt(sugg)}
              className="text-[10px] px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-primary-50 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 truncate max-w-[200px] transition-all border border-slate-200 dark:border-slate-700"
              title={sugg}
            >
              {sugg}
            </button>
          ))}
        </div>
      </div>

      {/* 4. Color Picker (Figure 5.6) */}
      <ColorPicker
        primary={primaryColor}
        secondary={secondaryColor}
        onPrimaryChange={onPrimary}
        onSecondaryChange={onSecondary}
      />

      {/* 5. Advanced Options & Checkpoint Selection */}
      <AdvancedOptions
        steps={steps}
        guidance={guidance}
        seed={seed}
        imageSize={imageSize}
        onStepsChange={onSteps}
        onGuidanceChange={onGuidance}
        onSeedChange={onSeed}
        onImageSizeChange={onImageSize}
      />

      {/* 6. Generate CTA Button */}
      <div className="flex flex-col gap-3 pt-2">
        <motion.button
          type="button"
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          disabled={loading || disableGenerate || !stylesLoaded}
          onClick={onGenerate}
          className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600 text-white font-bold py-4 text-base shadow-xl shadow-primary-500/25 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <>
              <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Synthesizing Pattern...</span>
            </>
          ) : (
            <>
              <BoltIcon className="h-5 w-5" />
              <span>Generate Pattern</span>
            </>
          )}
        </motion.button>
        <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 px-1">
          <span>Inference: ~0.8s GPU / 3.2s CPU fallback</span>
          <span>Checkpoint: snapshot-000480.pkl</span>
        </div>
      </div>
    </div>
  );
}
