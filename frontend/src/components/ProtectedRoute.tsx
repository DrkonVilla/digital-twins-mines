'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

// Rutas públicas que pueden ser visitadas sin usuario autenticado
const PUBLIC_ROUTES = [
  '/dashboard',
  '/gemelo-digital'
];

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((state) => state.token);
  const router = useRouter();
  const pathname = usePathname();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    // Si ya estamos en el cliente, no hay token y la ruta NO es pública -> redirigir a login
    if (isClient && !token) {
        const isPublic = PUBLIC_ROUTES.some(route => pathname.startsWith(route));
        if (!isPublic) {
            router.push('/login');
        }
    }
  }, [isClient, token, router, pathname]);

  if (!isClient) return null; // Avoid hydration mismatch

  // Renderizar si hay token o si es una ruta pública
  const isPublic = PUBLIC_ROUTES.some(route => pathname.startsWith(route));
  if (!token && !isPublic) return null; // Wait for redirect

  return <>{children}</>;
}
