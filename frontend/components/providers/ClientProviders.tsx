'use client';

import { ToastProvider } from '@/components/ui/Toast';
import { type ReactNode } from 'react';

interface ClientProvidersProps {
  children: ReactNode;
}

export function ClientProviders({ children }: ClientProvidersProps) {
  return <ToastProvider>{children}</ToastProvider>;
}
