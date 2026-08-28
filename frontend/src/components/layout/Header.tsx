'use client';

import { useAuthStore } from '@/store/authStore';

import { ThemeToggle } from '@/components/ThemeToggle';

export function Header() {
  const user = useAuthStore((state) => state.user);

  return (
    <header className="flex h-16 items-center justify-between px-6 bg-card border-b border-border">
      <div className="flex-1">
        {/* Espacio para breadcrumbs o búsqueda futura */}
      </div>
      <div className="flex items-center gap-6">
        <ThemeToggle />
        <div className="flex items-center gap-4">
          <div className="text-sm text-right">
            <p className="font-medium text-foreground">{user?.email || 'Usuario'}</p>
            <p className="text-xs text-muted-foreground">{user?.role || 'Operador'}</p>
          </div>
          <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
            {user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </div>
    </header>
  );
}
