import { Fragment } from 'react';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { ThemeToggle } from './ThemeToggle';

const navigation = [
  { name: 'Generator', href: '#generator' },
  { name: 'History', href: '#history' },
];

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
          <div className="glass rounded-2xl px-4 py-3 flex items-center justify-between shadow-sm">
            <a href="#" className="flex items-center gap-2">
              <span className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 shadow-md" />
              <div className="leading-tight">
                <p className="text-sm font-medium text-slate-500 dark:text-slate-300">AI Textile</p>
                <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">Pattern Studio</p>
              </div>
            </a>

            <div className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-700 dark:text-slate-200">
              {navigation.map((item) => (
                <a key={item.name} href={item.href} className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                  {item.name}
                </a>
              ))}
            </div>

            <div className="hidden md:flex items-center gap-3">
              <ThemeToggle />
              {token ? (
                <>
                  <span className="text-sm text-slate-600 dark:text-slate-300">Signed in</span>
                  <button
                    onClick={onLogout}
                    className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    Log out
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={onLogin}
                    className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    Log in
                  </button>
                  <button
                    onClick={onLogin}
                    className="text-sm font-semibold px-4 py-2 rounded-lg bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-md shadow-primary-500/30 hover:shadow-lg transition-all"
                  >
                    Get started
                  </button>
                </>
              )}
            </div>

            <div className="md:hidden flex items-center">
              <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500">
                <span className="sr-only">Open main menu</span>
                {open ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
              </Disclosure.Button>
            </div>
          </div>

          <AnimatePresence>
            {open && (
              <Disclosure.Panel as={motion.div} static initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="glass mt-2 rounded-2xl shadow-sm overflow-hidden md:hidden">
                <div className="px-4 pt-2 pb-3 space-y-1 text-sm font-medium text-slate-700">
                  {navigation.map((item) => (
                    <Disclosure.Button key={item.name} as="a" href={item.href} className="block rounded-lg px-3 py-2 hover:bg-slate-100">
                      {item.name}
                    </Disclosure.Button>
                  ))}
                  <div className="border-t border-slate-200 pt-3 flex flex-col gap-2">
                    {token ? (
                      <button className="text-left px-3 py-2 rounded-lg hover:bg-slate-100" onClick={onLogout}>
                        Log out
                      </button>
                    ) : (
                      <>
                        <button className="text-left px-3 py-2 rounded-lg hover:bg-slate-100" onClick={onLogin}>
                          Log in
                        </button>
                        <button
                          onClick={onLogin}
                          className="px-3 py-2 rounded-lg bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-md shadow-primary-500/30"
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
