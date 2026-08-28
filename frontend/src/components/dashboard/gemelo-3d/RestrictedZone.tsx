'use client';

import { Html } from '@react-three/drei';
import { useRef } from 'react';
import { Mesh } from 'three';
import { useFrame } from '@react-three/fiber';

interface RestrictedZoneProps {
  position: [number, number, number];
  size: [number, number, number];
  name: string;
}

export default function RestrictedZone({ position, size, name }: RestrictedZoneProps) {
  const meshRef = useRef<Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      // Pulse effect on opacity
      meshRef.current.material.opacity = 0.2 + Math.sin(clock.elapsedTime * 2) * 0.1;
    }
  });

  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <boxGeometry args={size} />
        <meshBasicMaterial color="#ef4444" transparent opacity={0.3} depthWrite={false} />
      </mesh>
      
      {/* Etiqueta flotante */}
      <Html position={[0, size[1] / 2 + 0.5, 0]} center>
        <div className="bg-destructive/80 text-white text-xs font-bold px-2 py-1 rounded border border-red-400 whitespace-nowrap">
          ⚠️ {name}
        </div>
      </Html>
    </group>
  );
}
