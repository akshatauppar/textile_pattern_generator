import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';

export function Hero() {
  return (
    <section className="pt-24 pb-12" id="hero">
      <div className="w-full px-4 grid lg:grid-cols-[1.15fr_0.85fr] gap-10 items-center">
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/60 border border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300 text-xs font-bold"
          >
            <SparklesIcon className="h-3.5 w-3.5" /> AI-Powered Textile Design Studio
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-5xl font-black leading-tight tracking-tight text-slate-900 dark:text-white"
          >
            Create seamless textile patterns{' '}
            <span className="bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 bg-clip-text text-transparent block mt-1">
              with AI precision and craft.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-base md:text-lg text-slate-600 dark:text-slate-300 leading-relaxed max-w-2xl"
          >
            Blend artisanal styles like <strong className="text-slate-900 dark:text-white">Bandhani</strong>,{' '}
            <strong className="text-slate-900 dark:text-white">Batik</strong>,{' '}
            <strong className="text-slate-900 dark:text-white">Ikat</strong>,{' '}
            <strong className="text-slate-900 dark:text-white">Block Print</strong>, and{' '}
            <strong className="text-slate-900 dark:text-white">Paisley</strong> into pixel-perfect, tileable fabrics.
            Guided by your prompts and image references, powered by <span className="font-semibold text-primary-600 dark:text-primary-400">StyleGAN2-ADA</span> with adaptive discriminator augmentation.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="flex flex-wrap gap-3 items-center"
          >
            <a
              href="#generator"
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-bold text-sm shadow-xl shadow-primary-500/25 transition-all"
            >
              Try the Generator
            </a>
            <a
              href="#history"
              className="px-5 py-3.5 rounded-2xl border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 text-slate-800 dark:text-slate-200 font-bold text-sm hover:border-primary-400 hover:text-primary-600 dark:hover:text-primary-400 transition-all shadow-sm"
            >
              View History
            </a>
          </motion.div>

          <div className="flex flex-wrap gap-2.5 text-xs font-semibold">
            <span className="px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/40 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800/60">
              Tileable 1024×1024
            </span>
            <span className="px-3 py-1 rounded-full bg-secondary-50 dark:bg-secondary-950/40 text-secondary-700 dark:text-secondary-300 border border-secondary-200 dark:border-secondary-800/60">
              5 Curated Styles
            </span>
            <span className="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/60">
              GPU-ready (0.8s)
            </span>
            <span className="px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800/60">
              StyleGAN2-ADA
            </span>
          </div>
        </div>

        {/* Hero visual card showcasing traditional styles */}
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative"
        >
          <div className="card-surface rounded-3xl p-5 overflow-hidden bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-700/80 shadow-2xl">
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: 'bandhani', label: 'Bandhani Tie-Dye', img: '/static/bandhani_blue.png' },
                { key: 'batik', label: 'Batik Wax Resist', img: '/static/sample_0_bandhani.png' },
                { key: 'ikat', label: 'Ikat Chevron Weave', img: '/static/sample_1_ikat.png' },
                { key: 'block', label: 'Block Print Stamp', img: '/static/bandhani_green.png' },
              ].map((item) => (
                <div
                  key={item.key}
                  className="relative h-32 rounded-2xl overflow-hidden bg-slate-900 border border-slate-200 dark:border-slate-700 group cursor-pointer"
                >
                  <img
                    src={item.img}
                    alt={item.label}
                    className="absolute inset-0 w-full h-full object-cover object-center group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-black/10" />
                  <div
                    className="absolute bottom-2.5 left-3 text-[11px] font-bold text-white drop-shadow-md"
                    style={{ textShadow: '0 1px 6px rgba(0,0,0,0.8)' }}
                  >
                    {item.label}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-3.5 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>Live generated samples &bull; StyleGAN2-ADA</span>
              <span className="text-primary-600 dark:text-primary-400 font-semibold font-mono">1,108 Dataset Images</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
