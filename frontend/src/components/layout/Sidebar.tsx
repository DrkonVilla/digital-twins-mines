'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Users, Truck, Bell, Activity, LogOut, Cuboid } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Gemelo Digital 3D', href: '/gemelo-digital', icon: Cuboid },
  { name: 'Trabajadores', href: '/monitoreo/trabajadores', icon: Users },
  { name: 'Maquinaria', href: '/monitoreo/maquinaria', icon: Truck },
  { name: 'Alertas', href: '/alertas', icon: Bell },
  { name: 'Historial', href: '/historial', icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();
  const logout = useAuthStore((state) => state.logout);

  return (
    <div className="flex h-full w-64 flex-col bg-card border-r border-border">
      <div className="flex h-16 items-center px-6 border-b border-border">
        <h1 className="text-xl font-bold text-primary">M-11 Alert</h1>
      </div>
      <div className="flex-1 py-6 px-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          return (
            <Link key={item.name} href={item.href}>
              <span
                className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-colors ${
                  isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </span>
            </Link>
          );
        })}
      </div>
      <div className="p-4 border-t border-border">
        <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground" onClick={logout}>
          <LogOut className="mr-2 h-5 w-5" />
          Cerrar Sesión
        </Button>
      </div>
    </div>
  );
}
