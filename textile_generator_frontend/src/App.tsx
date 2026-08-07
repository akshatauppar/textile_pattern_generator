import { useEffect, useRef, useState } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { ControlPanel } from './components/generator/ControlPanel';
import { Preview } from './components/generator/Preview';
import { HealthCard } from './components/HealthCard';
import { Footer } from './components/Footer';
import { HistoryPanel } from './components/HistoryPanel';
import { AuthModal } from './components/AuthModal';
import { useGenerator } from './hooks/useGenerator';
import { useTextureGANGenerator } from './hooks/useTextureGANGenerator';
import { USE_TEXTUREGAN } from './config/apiToggle';
import { useAuth } from './hooks/useAuth';
import { ThemeProvider } from './context/ThemeContext';
import type { StyleId } from './types';

function AppContent() {
  const generator = USE_TEXTUREGAN ? useTextureGANGenerator() : useGenerator();
  const { styles, loading, previewUrl, status, defaultStyle, generate } = generator;
  const { token, logout } = useAuth();

  const [prompt, setPrompt] = useState('intricate geometric floral pattern');
  const [style, setStyle] = useState<StyleId>('bandhani');
  const [primaryColor, setPrimaryColor] = useState('#6366F1');
  const [secondaryColor, setSecondaryColor] = useState('#EC4899');
  const [steps, setSteps] = useState(10);
  const [guidance, setGuidance] = useState(7.5);
  const [seed, setSeed] = useState<number | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const promptRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (defaultStyle) setStyle(defaultStyle);
  }, [defaultStyle]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const activeEl = document.activeElement as HTMLElement | null;
      const isTypingTarget =
        activeEl?.tagName === 'INPUT' ||
        activeEl?.tagName === 'TEXTAREA' ||
        activeEl?.isContentEditable;

      if (e.key === 'g' && !isTypingTarget) {
        e.preventDefault();
        onGenerate();
      }
      if (e.key === '/' && !isTypingTarget) {
        e.preventDefault();
        promptRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  });

  function hexToRgb(hex: string): [number, number, number] {
    const h = hex.replace('#', '');
    return [parseInt(h.substring(0, 2), 16), parseInt(h.substring(2, 4), 16), parseInt(h.substring(4, 6), 16)];
  }

  const onGenerate = () => {
    if (USE_TEXTUREGAN) {
      generate({
        prompt,
        primary_color: hexToRgb(primaryColor),
        secondary_color: hexToRgb(secondaryColor),
        seed,
        num_samples: 1,
      });
    } else {
      // Clamp steps to max 30 for SDXL/Euler
      const safeSteps = Math.min(steps, 30);
      generate({
        prompt,
        style,
        color_1: primaryColor,
        color_2: secondaryColor,
        seed,
        num_inference_steps: safeSteps,
        guidance_scale: guidance,
      });
    }
  };

  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100">
      <Header onLogin={() => setAuthOpen(true)} onLogout={logout} token={token} />
      <main className="pt-16">
        <Hero />

        <section className="py-10" id="generator">
          <div className="w-full px-4 space-y-4">
            <HealthCard />
            <div className="grid lg:grid-cols-2 gap-8 items-start">
              <ControlPanel
                prompt={prompt}
                style={style}
                primaryColor={primaryColor}
                secondaryColor={secondaryColor}
                steps={steps}
                guidance={guidance}
                seed={seed}
                loading={loading}
                promptRef={promptRef}
                onPrompt={setPrompt}
                onStyle={setStyle}
                onPrimary={setPrimaryColor}
                onSecondary={setSecondaryColor}
                onSteps={setSteps}
                onGuidance={setGuidance}
                onSeed={setSeed}
                onGenerate={onGenerate}
                disableGenerate={!prompt || prompt.length < 3}
                stylesLoaded={styles.length > 0}
              />
              <Preview previewUrl={previewUrl} status={status} loading={loading} />
            </div>
            <HistoryPanel />
          </div>
        </section>

      </main>
      <Footer />
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
