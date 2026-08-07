import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useState } from 'react';
import { useAuth } from '../hooks/useAuth';

interface Props {
  open: boolean;
  onClose: () => void;
}

export function AuthModal({ open, onClose }: Props) {
  const { login, register, loading } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async () => {
    if (mode === 'login') {
      await login(username, password);
      onClose();
    } else {
      await register(username, email, password);
      setMode('login');
    }
  };

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-slate-900/40" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl">
                <Dialog.Title className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  {mode === 'login' ? 'Log in' : 'Create account'}
                </Dialog.Title>
                <p className="text-sm text-slate-500 dark:text-slate-300 mb-4">Access history and manage your generations.</p>

                <div className="space-y-3 text-sm text-slate-700 dark:text-slate-200">
                  <label className="block space-y-1">
                    <span className="text-xs text-slate-500 dark:text-slate-300">Username</span>
                    <input
                      className="w-full rounded-lg border border-slate-200 px-3 py-2 focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </label>
                  {mode === 'register' && (
                    <label className="block space-y-1">
                      <span className="text-xs text-slate-500 dark:text-slate-300">Email</span>
                      <input
                        className="w-full rounded-lg border border-slate-200 px-3 py-2 focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                    </label>
                  )}
                  <label className="block space-y-1">
                    <span className="text-xs text-slate-500 dark:text-slate-300">Password</span>
                    <input
                      type="password"
                      className="w-full rounded-lg border border-slate-200 px-3 py-2 focus:border-primary-300 focus:ring-2 focus:ring-primary-500"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </label>
                </div>

                <div className="mt-5 flex items-center justify-between text-sm text-slate-600 dark:text-slate-300">
                  <button type="button" className="text-primary-600" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
                    {mode === 'login' ? 'Need an account? Register' : 'Have an account? Log in'}
                  </button>
                  <button
                    type="button"
                    disabled={loading || !username || !password || (mode === 'register' && !email)}
                    onClick={handleSubmit}
                    className="rounded-lg bg-gradient-to-r from-primary-500 to-secondary-500 px-4 py-2 text-white font-semibold shadow-md disabled:opacity-60"
                  >
                    {loading ? 'Working...' : mode === 'login' ? 'Log in' : 'Register'}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
