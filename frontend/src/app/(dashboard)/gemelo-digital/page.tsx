'use client';

import dynamic from 'next/dynamic';
import { Card, CardContent } from '@/components/ui/card';
import { SimulateButton } from '@/components/dashboard/SimulateButton';

// Import the 3D scene dynamically to avoid SSR issues with WebGL
const Scene3D = dynamic(() => import('@/components/dashboard/gemelo-3d/Scene3D'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] flex items-center justify-center bg-muted/20 border rounded-lg">
      <p className="text-muted-foreground animate-pulse">Cargando Gemelo Digital 3D...</p>
    </div>
  )
});

export default function GemeloDigitalPage() {
  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Gemelo Digital 3D</h2>
          <p className="text-muted-foreground">Monitor en tiempo real del frente de extracción subterránea.</p>
        </div>
        <div>
          <SimulateButton size="default" variant="default" />
        </div>
      </div>
      
      <Card className="flex-1 min-h-[600px] flex flex-col">
        <CardContent className="flex-1 p-0 relative overflow-hidden rounded-b-xl">
          <Scene3D />
        </CardContent>
      </Card>
    </div>
  );
}
