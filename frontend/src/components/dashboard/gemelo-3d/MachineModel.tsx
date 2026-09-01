import { Html } from '@react-three/drei';
import { useRef } from 'react';
import { Mesh, Group, MathUtils } from 'three';
import { useFrame } from '@react-three/fiber';

interface MachineProps {
  position: [number, number, number];
  riskLevel: string;
  label: string;
}

export default function MachineModel({ position, riskLevel, label }: MachineProps) {
  const groupRef = useRef<Group>(null);
  const haloRef = useRef<Mesh>(null);

  // Risk color
  let riskColor = '#3b82f6'; // blue default
  if (riskLevel === 'MEDIO') riskColor = '#eab308';
  if (riskLevel === 'ALTO') riskColor = '#ef4444';

  useFrame(({ clock }, delta) => {
    // Smooth position LERP animation
    if (groupRef.current) {
      groupRef.current.position.x = MathUtils.lerp(groupRef.current.position.x, position[0], delta * 3.5);
      groupRef.current.position.y = MathUtils.lerp(groupRef.current.position.y, position[1], delta * 3.5);
      groupRef.current.position.z = MathUtils.lerp(groupRef.current.position.z, position[2], delta * 3.5);
    }

    if (haloRef.current && (riskLevel === 'MEDIO' || riskLevel === 'ALTO')) {
      const speed = riskLevel === 'ALTO' ? 8 : 3;
      const pulse = Math.sin(clock.elapsedTime * speed);
      haloRef.current.scale.x = 1 + pulse * 0.08;
      haloRef.current.scale.z = 1 + pulse * 0.08;
      (haloRef.current.material as any).opacity = 0.4 + pulse * 0.2;
    }
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Risk halo on floor */}
      {riskLevel !== 'BAJO' && (
        <mesh ref={haloRef} position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[1.6, 2.4, 32]} />
          <meshBasicMaterial color={riskColor} transparent opacity={0.45} />
        </mesh>
      )}

      {/* Main body of LHD loader */}
      <mesh position={[0, 0.6, 0]} castShadow>
        <boxGeometry args={[2.2, 0.9, 1.1]} />
        <meshStandardMaterial color="#d97706" roughness={0.5} metalness={0.3} />
      </mesh>

      {/* Cab */}
      <mesh position={[0.5, 1.25, 0]} castShadow>
        <boxGeometry args={[0.9, 0.65, 0.9]} />
        <meshStandardMaterial color="#92400e" roughness={0.4} metalness={0.2} />
      </mesh>

      {/* Cab window (dark glass) */}
      <mesh position={[0.95, 1.25, 0]}>
        <boxGeometry args={[0.05, 0.4, 0.7]} />
        <meshStandardMaterial color="#1e3a5f" transparent opacity={0.7} metalness={0.6} />
      </mesh>

      {/* Front arm / bucket */}
      <mesh position={[-1.4, 0.5, 0]} rotation={[0, 0, -0.2]} castShadow>
        <boxGeometry args={[0.5, 0.15, 1.1]} />
        <meshStandardMaterial color="#78350f" roughness={0.6} metalness={0.4} />
      </mesh>

      {/* Bucket */}
      <mesh position={[-1.7, 0.3, 0]} castShadow>
        <boxGeometry args={[0.4, 0.45, 1.2]} />
        <meshStandardMaterial color="#57534e" roughness={0.7} metalness={0.5} />
      </mesh>

      {/* Wheels */}
      {([-0.7, 0.7] as number[]).map((xOff, i) =>
        ([-0.6, 0.6] as number[]).map((zOff, j) => (
          <mesh key={`${i}-${j}`} position={[xOff, 0.28, zOff]} rotation={[Math.PI / 2, 0, 0]} castShadow>
            <cylinderGeometry args={[0.28, 0.28, 0.22, 16]} />
            <meshStandardMaterial color="#1c1917" roughness={0.9} />
          </mesh>
        ))
      )}

      {/* Status light on top - color indicates risk */}
      <mesh position={[0.5, 1.65, 0]}>
        <sphereGeometry args={[0.12, 8, 8]} />
        <meshStandardMaterial color={riskColor} emissive={riskColor} emissiveIntensity={0.8} />
      </mesh>

      {/* Label */}
      <Html position={[0, 2.2, 0]} center distanceFactor={8}>
        <div className={`px-2 py-1 rounded text-xs font-bold text-white shadow-lg whitespace-nowrap ${
          riskLevel === 'ALTO' ? 'bg-red-600' :
          riskLevel === 'MEDIO' ? 'bg-amber-500 text-black' :
          'bg-blue-600'
        }`}>
          {label}
        </div>
      </Html>
    </group>
  );
}
