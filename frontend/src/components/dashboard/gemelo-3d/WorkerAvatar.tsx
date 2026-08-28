'use client';

import { useGLTF, Html } from '@react-three/drei';
import { useRef } from 'react';
import { Group, Mesh } from 'three';
import { useFrame } from '@react-three/fiber';

interface WorkerProps {
  position: [number, number, number];
  riskLevel: string; // 'BAJO', 'MEDIO', 'ALTO'
  label: string;
}

export default function WorkerAvatar({ position, riskLevel, label }: WorkerProps) {
  const group = useRef<Group>(null);
  const haloRef = useRef<Mesh>(null);
  
  // Use a generic sample human model
  const { scene } = useGLTF('https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/man/model.gltf');

  // Determine risk colors
  let color = '#22c55e'; // Green for BAJO
  if (riskLevel === 'MEDIO') color = '#eab308'; // Yellow for MEDIO
  if (riskLevel === 'ALTO') color = '#ef4444'; // Red for ALTO

  useFrame(({ clock }) => {
    if (haloRef.current && (riskLevel === 'MEDIO' || riskLevel === 'ALTO')) {
      // Pulsating effect for medium and high risk
      const speed = riskLevel === 'ALTO' ? 10 : 3;
      haloRef.current.scale.x = 1 + Math.sin(clock.elapsedTime * speed) * 0.1;
      haloRef.current.scale.z = 1 + Math.sin(clock.elapsedTime * speed) * 0.1;
      haloRef.current.material.opacity = 0.5 + Math.sin(clock.elapsedTime * speed) * 0.3;
    }
  });

  return (
    <group position={position} ref={group}>
      {/* Risk Halo Indicator */}
      <mesh ref={haloRef} position={[0, 0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.5, 0.8, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.6} />
      </mesh>

      {/* The 3D Model */}
      <primitive object={scene.clone()} scale={1} position={[0, 0, 0]} />

      {/* HTML Label */}
      <Html position={[0, 2.2, 0]} center>
        <div className={`px-2 py-1 rounded text-xs font-bold text-white shadow-lg ${
          riskLevel === 'ALTO' ? 'bg-destructive' : 
          riskLevel === 'MEDIO' ? 'bg-amber-500 text-black' : 
          'bg-emerald-600'
        }`}>
          {label}
        </div>
      </Html>
    </group>
  );
}

useGLTF.preload('https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/man/model.gltf');
