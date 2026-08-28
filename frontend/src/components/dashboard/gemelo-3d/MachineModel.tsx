'use client';

import { useGLTF, Html } from '@react-three/drei';
import { useRef } from 'react';
import { Group, Mesh } from 'three';
import { useFrame } from '@react-three/fiber';

interface MachineProps {
  position: [number, number, number];
  riskLevel: string; // 'BAJO', 'MEDIO', 'ALTO'
  label: string;
}

export default function MachineModel({ position, riskLevel, label }: MachineProps) {
  const group = useRef<Group>(null);
  const haloRef = useRef<Mesh>(null);
  
  // Use a generic sample vehicle model
  const { scene } = useGLTF('https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/car/model.gltf');

  // Determine risk colors
  let color = '#3b82f6'; // Default blue for machine
  if (riskLevel === 'MEDIO') color = '#eab308';
  if (riskLevel === 'ALTO') color = '#ef4444';

  useFrame(({ clock }) => {
    if (haloRef.current && (riskLevel === 'MEDIO' || riskLevel === 'ALTO')) {
      const speed = riskLevel === 'ALTO' ? 10 : 3;
      haloRef.current.scale.x = 1 + Math.sin(clock.elapsedTime * speed) * 0.05;
      haloRef.current.scale.z = 1 + Math.sin(clock.elapsedTime * speed) * 0.05;
      haloRef.current.material.opacity = 0.4 + Math.sin(clock.elapsedTime * speed) * 0.2;
    }
  });

  return (
    <group position={position} ref={group}>
      {/* Risk Halo Indicator */}
      {riskLevel !== 'BAJO' && (
        <mesh ref={haloRef} position={[0, 0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[1.5, 2.5, 32]} />
          <meshBasicMaterial color={color} transparent opacity={0.5} />
        </mesh>
      )}

      {/* The 3D Model */}
      {/* The car is a bit large, scaling it down */}
      <primitive object={scene.clone()} scale={1.2} position={[0, 0, 0]} />

      {/* HTML Label */}
      <Html position={[0, 3, 0]} center>
        <div className={`px-2 py-1 rounded text-xs font-bold text-white shadow-lg ${
          riskLevel === 'ALTO' ? 'bg-destructive' : 
          riskLevel === 'MEDIO' ? 'bg-amber-500 text-black' : 
          'bg-blue-600'
        }`}>
          {label}
        </div>
      </Html>
    </group>
  );
}

useGLTF.preload('https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/car/model.gltf');
