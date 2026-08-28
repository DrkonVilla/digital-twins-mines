'use client';

import { Html } from '@react-three/drei';
import { useRef } from 'react';
import { Mesh } from 'three';
import { useFrame } from '@react-three/fiber';

interface WorkerProps {
  position: [number, number, number];
  riskLevel: string; // 'BAJO', 'MEDIO', 'ALTO'
  label: string;
}

export default function WorkerAvatar({ position, riskLevel, label }: WorkerProps) {
  const haloRef = useRef<Mesh>(null);

  // Color mapping
  let color = '#22c55e';
  if (riskLevel === 'MEDIO') color = '#eab308';
  if (riskLevel === 'ALTO') color = '#ef4444';

  useFrame(({ clock }) => {
    if (haloRef.current && (riskLevel === 'MEDIO' || riskLevel === 'ALTO')) {
      const speed = riskLevel === 'ALTO' ? 8 : 3;
      const pulse = Math.sin(clock.elapsedTime * speed);
      haloRef.current.scale.x = 1 + pulse * 0.15;
      haloRef.current.scale.z = 1 + pulse * 0.15;
      (haloRef.current.material as any).opacity = 0.5 + pulse * 0.3;
    }
  });

  return (
    <group position={position}>
      {/* Risk halo on the floor */}
      <mesh ref={haloRef} position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.55, 0.85, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.6} />
      </mesh>

      {/* Body: torso */}
      <mesh position={[0, 0.75, 0]} castShadow>
        <cylinderGeometry args={[0.2, 0.2, 0.7, 12]} />
        <meshStandardMaterial color={color} roughness={0.4} metalness={0.1} />
      </mesh>

      {/* Head */}
      <mesh position={[0, 1.3, 0]} castShadow>
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial color="#f5cba7" roughness={0.8} />
      </mesh>

      {/* Helmet */}
      <mesh position={[0, 1.46, 0]} castShadow>
        <sphereGeometry args={[0.24, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial color="#facc15" roughness={0.3} />
      </mesh>

      {/* Left arm */}
      <mesh position={[-0.28, 0.85, 0]} rotation={[0, 0, 0.3]} castShadow>
        <cylinderGeometry args={[0.07, 0.07, 0.5, 8]} />
        <meshStandardMaterial color={color} roughness={0.5} />
      </mesh>

      {/* Right arm */}
      <mesh position={[0.28, 0.85, 0]} rotation={[0, 0, -0.3]} castShadow>
        <cylinderGeometry args={[0.07, 0.07, 0.5, 8]} />
        <meshStandardMaterial color={color} roughness={0.5} />
      </mesh>

      {/* Left leg */}
      <mesh position={[-0.12, 0.23, 0]} castShadow>
        <cylinderGeometry args={[0.09, 0.09, 0.45, 8]} />
        <meshStandardMaterial color="#374151" roughness={0.8} />
      </mesh>

      {/* Right leg */}
      <mesh position={[0.12, 0.23, 0]} castShadow>
        <cylinderGeometry args={[0.09, 0.09, 0.45, 8]} />
        <meshStandardMaterial color="#374151" roughness={0.8} />
      </mesh>

      {/* Label */}
      <Html position={[0, 1.9, 0]} center distanceFactor={8}>
        <div className={`px-2 py-1 rounded text-xs font-bold text-white shadow-lg whitespace-nowrap ${
          riskLevel === 'ALTO' ? 'bg-red-600' :
          riskLevel === 'MEDIO' ? 'bg-amber-500 text-black' :
          'bg-emerald-600'
        }`}>
          {label}
        </div>
      </Html>
    </group>
  );
}
