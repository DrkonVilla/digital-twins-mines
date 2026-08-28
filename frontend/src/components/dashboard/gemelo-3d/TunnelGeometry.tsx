'use client';

import { DoubleSide } from 'three';
import { useRef } from 'react';
import { Mesh } from 'three';

export default function TunnelGeometry() {
  const meshRef = useRef<Mesh>(null);

  return (
    <group>
      {/* Suelo del túnel */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color="#2a2a2a" roughness={0.9} />
      </mesh>

      {/* Paredes del túnel (Medio Cilindro ahuecado) */}
      <mesh position={[0, 0, 0]} rotation={[0, 0, 0]} receiveShadow castShadow>
        {/* Un cilindro cortado por la mitad */}
        <cylinderGeometry args={[15, 15, 100, 32, 1, true, 0, Math.PI]} />
        {/* Lo rotamos para que parezca una bóveda */}
        <meshStandardMaterial color="#3a3028" roughness={0.8} side={DoubleSide} />
      </mesh>
    </group>
  );
}
