import { Disclosure } from '@headlessui/react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import { ThemeToggle } from './ThemeToggle';

interface Props {
  onLogin: () => void;
  onLogout: () => void;
  token: string | null;
}

export function Header({ onLogin, onLogout, token }: Props) {
  return (
    <Disclosure as="header" className="fixed top-0 inset-x-0 z-50">
      {({ open }) => (
        <div className="w-full px-4 pt-3">
          <div className="glass rounded-2xl px-4 py-3 flex items-center justify-between shadow-sm border border-slate-200/60 dark:border-slate-800/80">
            {/* Logo */}
            <a href="#" className="flex items-center gap-2.5">
              <span className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary-500 via-secondary-500 to-accent-500 shadow-md flex items-center justify-center text-white font-black text-sm">
                ST
              </span>
              <div className="leading-tight">
                <p className="text-xs font-semibold text-primary-600 dark:text-primary-400">AI Textile</p>
                <p className="text-base font-black text-slate-900 dark:text-slate-100">Pattern Studio</p>
              </div>
            </a>

            {/* Nav links */}
            <div className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-700 dark:text-slate-200">
              <a href="#generator" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                Generator
              </a>
              <a href="#history" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                History
              </a>
            </div>

            {/* Status & Auth buttons */}
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 text-[11px] font-semibold">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                Backend: Healthy
              </div>
              <ThemeToggle />
              {token ? (
                <>
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Signed in</span>
                  <button
                    onClick={onLogout}
                    className="text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-rose-500 transition-colors"
                  >
                    Log out
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={onLogin}
                    className="text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-primary-600 transition-colors"
                  >
                    Log in
                  </button>
                  <button
                    onClick={onLogin}
                    className="text-xs font-bold px-3.5 py-2 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-md shadow-primary-500/25 hover:shadow-lg transition-all"
                  >
                    Get started
                  </button>
                </>
              )}
            </div>

            {/* Mobile menu trigger */}
            <div className="md:hidden flex items-center gap-2">
              <ThemeToggle />
              <Disclosure.Button className="inline-flex items-center justify-center rounded-xl p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 focus:outline-none">
                <span className="sr-only">Open main menu</span>
                {open ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
              </Disclosure.Button>
            </div>
          </div>

          <AnimatePresence>
            {open && (
              <Disclosure.Panel as={motion.div} static initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="glass mt-2 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-800 overflow-hidden md:hidden">
                <div className="px-4 pt-3 pb-4 space-y-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
                  <Disclosure.Button as="a" href="#generator" className="block rounded-xl px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800">
                    Generator
                  </Disclosure.Button>
                  <Disclosure.Button as="a" href="#history" className="block rounded-xl px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800">
                    History
                  </Disclosure.Button>
                  <div className="border-t border-slate-200 dark:border-slate-700 pt-3 flex flex-col gap-2">
                    {token ? (
                      <button className="text-left px-3 py-2 rounded-xl hover:bg-slate-100" onClick={onLogout}>
                        Log out
                      </button>
                    ) : (
                      <>
                        <button className="text-left px-3 py-2 rounded-xl hover:bg-slate-100" onClick={onLogin}>
                          Log in
                        </button>
                        <button
                          onClick={onLogin}
                          className="px-3 py-2.5 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-md text-center font-bold text-xs"
                        >
                          Get started
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </Disclosure.Panel>
            )}
          </AnimatePresence>
        </div>
      )}
    </Disclosure>
  );
}
