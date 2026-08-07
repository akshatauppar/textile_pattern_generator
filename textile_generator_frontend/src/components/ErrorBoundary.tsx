import React from 'react';
import toast from 'react-hot-toast';

interface State { hasError: boolean }

export class ErrorBoundary extends React.Component<React.PropsWithChildren, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.error(error);
    toast.error('Something went wrong. Please refresh.');
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen grid place-items-center text-center text-slate-700">
          <div className="space-y-3">
            <p className="text-2xl font-bold text-slate-900">Unexpected error</p>
            <p className="text-slate-500">Please refresh the page or try again later.</p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
