import { motion } from 'framer-motion';

export function Hero() {
  return (
    <section className="pt-28 pb-16" id="hero">
      <div className="w-full px-4 grid lg:grid-cols-[1.1fr_0.9fr] gap-10 items-center">
        <div className="space-y-6">
          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-5xl font-bold leading-tight"
          >
            <span className="bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 bg-clip-text text-transparent">
              Create seamless textile patterns
            </span>
            <br />
            with AI precision and craft.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-lg text-slate-600 dark:text-slate-300 w-full"
          >
            Blend artisanal styles like Bandhani, Ikat, Block Print, and Paisley into pixel-perfect, tileable fabrics.
            Guided by your prompts, rendered by SDXL LoRA.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="flex flex-wrap gap-3"
          >
            <a
              href="#generator"
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold shadow-lg shadow-primary-500/30 hover:shadow-xl"
            >
              Try the Generator
            </a>
            <a
              href="#gallery"
              className="px-5 py-3 rounded-xl border border-slate-200 bg-white/80 text-slate-800 font-semibold hover:border-primary-300 hover:text-primary-600"
            >
              View Examples
            </a>
          </motion.div>

          <div className="flex flex-wrap gap-4 text-sm text-slate-600">
            <span className="px-3 py-1 rounded-full bg-primary-50 text-primary-700">Tileable 1024×1024</span>
            <span className="px-3 py-1 rounded-full bg-secondary-50 text-secondary-700">4 curated styles</span>
            <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700">GPU-ready</span>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative"
        >
          <div className="card-surface rounded-3xl p-6 overflow-hidden bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-700">
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: 'bandhani', label: 'Bandhani', img: '/static/bandhani_blue.png' },
                { key: 'ikat', label: 'Ikat', img: '/static/sample_1_ikat.png' },
                { key: 'block', label: 'Block Print', img: '/static/bandhani_green.png' },
                { key: 'paisley', label: 'Paisley', img: '/static/ikat_chevron_2x2.png' },
              ].map((item) => (
                <div
                  key={item.key}
                  className="relative h-32 rounded-2xl overflow-hidden bg-gradient-to-br from-primary-50 to-white dark:from-slate-800 dark:to-slate-900 border border-slate-200 dark:border-slate-700"
                >
                  <img
                    src={item.img}
                    alt={item.label}
                    className="absolute inset-0 w-full h-full object-cover object-center"
                  />
                  <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-primary-100/40 dark:from-slate-900/30 dark:to-slate-800/40" />
                  <div className="absolute inset-0 shimmer opacity-30" />
                  <div className="absolute bottom-3 left-3 text-xs font-bold capitalize drop-shadow"
                       style={{ color: 'white', textShadow: '0 1px 6px rgba(0,0,0,0.7)' }}>
                    {item.label}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 text-sm text-slate-500">Live previews appear here after generation.</div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
