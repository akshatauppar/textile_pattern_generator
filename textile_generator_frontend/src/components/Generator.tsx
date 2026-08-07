import { useEffect } from 'react';
import { useState, useMemo } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { USE_TEXTUREGAN } from '../config/apiToggle';
import { useTextureGANGenerator } from '../hooks/useTextureGANGenerator';
import { useGenerator } from '../hooks/useGenerator';
import { useGenerationStatus } from '../hooks/useGenerationStatus';
import { UpscaleButton } from './UpscaleButton';
import { DownloadButton } from './DownloadButton';
import { StyleSelector } from './generator/StyleSelector';
import { PatternSelector } from './generator/PatternSelector';
import { motion } from 'framer-motion';
import type { StyleId, PatternId, PatternOption } from '../types';

const PATTERN_OPTIONS: Record<StyleId, PatternOption[]> = {
  'bandhani': [
    { id: 'leheriya' as PatternId, name: 'Leheriya', description: 'Diagonal wavy lines' },
    { id: 'shikari' as PatternId, name: 'Shikari', description: 'Hunting pattern' },
    { id: 'mothra' as PatternId, name: 'Mothra', description: 'Circular motifs' },
    { id: 'rajasthani_tie' as PatternId, name: 'Rajasthani Tie', description: 'Traditional tie' },
    { id: 'mandala' as PatternId, name: 'Mandala', description: 'Circular mandala' },
  ],
  'batik': [
    { id: 'geometric_batik' as PatternId, name: 'Geometric', description: 'Geometric patterns' },
    { id: 'floral_batik' as PatternId, name: 'Floral', description: 'Floral designs' },
    { id: 'traditional_batik' as PatternId, name: 'Traditional', description: 'Indonesian batik' },
    { id: 'wax_resist' as PatternId, name: 'Wax Resist', description: 'Wax resist' },
    { id: 'crackle' as PatternId, name: 'Crackle', description: 'Crackle effect' },
  ],
  'ikat': [
    { id: 'striped_ikat' as PatternId, name: 'Striped', description: 'Striped pattern' },
    { id: 'diamond_ikat' as PatternId, name: 'Diamond', description: 'Diamond motifs' },
    { id: 'blurred_motif' as PatternId, name: 'Blurred Motif', description: 'Blurred edges' },
    { id: 'traditional_ikat' as PatternId, name: 'Traditional', description: 'Traditional weave' },
    { id: 'woven_pattern' as PatternId, name: 'Woven Pattern', description: 'Woven patterns' },
  ],
};

const COLORS = [
  { name: 'Red', hex: '#ff0000' },
  { name: 'Blue', hex: '#0000ff' },
  { name: 'Green', hex: '#00aa00' },
  { name: 'Gold', hex: '#ffd700' },
  { name: 'Black', hex: '#000000' },
  { name: 'White', hex: '#ffffff' },
];

export function Generator() {
  const { token } = useAuth();
  const [prompt, setPrompt] = useState('intricate floral pattern');
  const [style, setStyle] = useState<StyleId>('bandhani');
  const [pattern, setPattern] = useState<PatternId>('leheriya');
  const [color1, setColor1] = useState('#ff0000');
  const [color2, setColor2] = useState('#ffffff');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationId, setGenerationId] = useState<number | null>(null);
  
  // WebSocket status for SDXL/LoRA backend
  const { status: wsStatus, imageUrl: wsImageUrl, error: wsError } = useGenerationStatus(
    !USE_TEXTUREGAN ? generationId : null
  );

  // Compute full image URL for cross-origin if needed
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const fullImageUrl = wsImageUrl && wsImageUrl.startsWith('/api/') ? backendUrl + wsImageUrl : wsImageUrl;

  // Toast on image ready or error
  useEffect(() => {
    if (fullImageUrl) toast.success('Pattern ready!');
    if (wsError) toast.error(wsError);
  }, [fullImageUrl, wsError]);

  // Update pattern when style changes
  useEffect(() => {
    const patterns = PATTERN_OPTIONS[style];
    if (patterns && patterns.length > 0) {
      setPattern(patterns[0].id);
    }
  }, [style]);

  // Use the correct generator hook based on toggle
  const generator = USE_TEXTUREGAN ? useTextureGANGenerator() : useGenerator();
  const { styles, loading, previewUrl, status, generate, error } = generator;

  // Get available patterns for current style
  const availablePatterns = useMemo(() => PATTERN_OPTIONS[style] || [], [style]);

  // Convert hex color to RGB array
  function hexToRgb(hex: string): [number, number, number] {
    const h = hex.replace('#', '');
    return [parseInt(h.substring(0, 2), 16), parseInt(h.substring(2, 4), 16), parseInt(h.substring(4, 6), 16)];
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a description');
      return;
    }
    // Always send color as RGB array for both backends
    if (USE_TEXTUREGAN) {
      generate({
        prompt: prompt.trim(),
        primary_color: hexToRgb(color1),
        secondary_color: hexToRgb(color2),
        seed: undefined,
        num_samples: 1,
      });
    } else {
      // For SDXL/LoRA, start generation and set generationId for WebSocket updates
      setIsGenerating(true);
      try {
        const result = await generate({
          prompt: prompt.trim(),
          style,
          pattern,
          color_1: color1,
          color_2: color2,
          seed: undefined,
          num_inference_steps: 15,
        });
        if (result && result.id) {
          setGenerationId(result.id);
        }
      } finally {
        setIsGenerating(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Panel */}
      <div className="card-surface rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Pattern Description</h3>

        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your textile pattern..."
          disabled={isGenerating}
          className="w-full h-24 p-3 border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 placeholder-slate-400 dark:placeholder-slate-500"
        />

        <StyleSelector value={style} onChange={setStyle} />

        <PatternSelector value={pattern} onChange={setPattern} patterns={availablePatterns} />

        <div>
          <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Colors</label>
          <div className="space-y-3">
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Primary Color</p>
              <div className="flex gap-2 flex-wrap">
                {COLORS.map(c => (
                  <button
                    key={c.hex}
                    onClick={() => setColor1(c.hex)}
                    style={{ backgroundColor: c.hex }}
                    className={`w-8 h-8 rounded-lg border-2 transition-all ${color1 === c.hex ? 'border-slate-900 dark:border-slate-100 ring-2 ring-primary-500' : 'border-slate-300 dark:border-slate-700'}`}
                    title={c.name}
                    disabled={isGenerating}
                  />
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Secondary Color</p>
              <div className="flex gap-2 flex-wrap">
                {COLORS.map(c => (
                  <button
                    key={c.hex}
                    onClick={() => setColor2(c.hex)}
                    style={{ backgroundColor: c.hex }}
                    className={`w-8 h-8 rounded-lg border-2 transition-all ${color2 === c.hex ? 'border-slate-900 dark:border-slate-100 ring-2 ring-primary-500' : 'border-slate-300 dark:border-slate-700'}`}
                    title={c.name}
                    disabled={isGenerating}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || status === 'processing'}
          className="w-full py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating || status === 'processing' ? 'Generating...' : 'Generate Pattern'}
        </button>
      </div>

      {/* Result Panel */}
      {(generationId || wsImageUrl || previewUrl) && (
        <div className="card-surface rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Generated Pattern</h3>

          {/* Show loading spinner for SDXL/LoRA */}
          {!USE_TEXTUREGAN && wsStatus === 'processing' && (
            <motion.div animate={{ opacity: [0.6, 1] }} className="text-center py-8">
              <div className="inline-block">
                <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
              </div>
              <p className="text-slate-600 mt-4">Generating your seamless pattern...</p>
            </motion.div>
          )}

          {/* Show error from WebSocket or generator */}
          {(!USE_TEXTUREGAN && wsError) && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-200">
              {wsError}
            </div>
          )}
          {/* Show error for TextureGAN */}
          {(USE_TEXTUREGAN && error) && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-200">
              {error}
            </div>
          )}

          {/* Show image from WebSocket for SDXL/LoRA, or previewUrl for TextureGAN */}
          {(!USE_TEXTUREGAN && fullImageUrl) && (
            <>
              <img src={fullImageUrl} alt="Generated pattern" className="w-full rounded-lg" />
              <div className="flex gap-3">
                <UpscaleButton
                  generationId={generationId!}
                  currentUrl={fullImageUrl}
                />
                <DownloadButton
                  imageUrl={fullImageUrl}
                  filename={`textile_pattern_${generationId}.png`}
                />
              </div>
            </>
          )}
          {(USE_TEXTUREGAN && previewUrl) && (
            <>
              <img src={previewUrl} alt="Generated pattern" className="w-full rounded-lg" />
              <div className="flex gap-3">
                <UpscaleButton
                  generationId={generationId!}
                  currentUrl={previewUrl}
                />
                <DownloadButton
                  imageUrl={previewUrl}
                  filename={`textile_pattern_${generationId}.png`}
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
