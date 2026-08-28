'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Grid } from '@react-three/drei';
import { PCFShadowMap } from 'three';
import TunnelGeometry from './TunnelGeometry';
import WorkerAvatar from './WorkerAvatar';
import MachineModel from './MachineModel';
import RestrictedZone from './RestrictedZone';
import InfoPanel3D from './InfoPanel3D';
import { useAlertStore } from '@/store/alertStore';
import { Suspense, useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/alerts/ws';

export default function Scene3D() {
  const alerts = useAlertStore((state) => state.alerts);
  const addAlert = useAlertStore((state) => state.addAlert);
  const activeAlert = alerts.length > 0 ? alerts[0] : null;

  const handleWsMessage = useCallback((data: any) => addAlert(data), [addAlert]);
  useWebSocket(WS_URL, handleWsMessage);

  // Derive risk levels for our mock entities
  const workerRisk = activeAlert?.worker_id === 1 ? activeAlert.risk_level : 'BAJO';
  const machineRisk = activeAlert?.machine_id === 1 ? activeAlert.risk_level : 'BAJO';

  return (
    <>
      <Canvas
        camera={{ position: [10, 8, 10], fov: 50 }}
        shadows={{ type: PCFShadowMap }}
        className="w-full h-full"
        gl={{ antialias: true }}
      >
        <color attach="background" args={['#111827']} />

        {/* Luces */}
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[12, 20, 10]}
          intensity={1.2}
          castShadow
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
          shadow-camera-far={80}
          shadow-camera-left={-20}
          shadow-camera-right={20}
          shadow-camera-top={20}
          shadow-camera-bottom={-20}
        />
        <pointLight position={[0, 6, 0]} intensity={0.5} color="#ffe4b5" />

        {/* Entorno y grilla */}
        <Suspense fallback={null}>
          <Environment preset="city" />
          <Grid
            infiniteGrid
            fadeDistance={60}
            sectionColor="#374151"
            cellColor="#1f2937"
            position={[0, -0.01, 0]}
          />

          {/* El Túnel */}
          <TunnelGeometry />

          {/* Zona Restringida */}
          <RestrictedZone position={[5, 0, -5]} size={[10, 4, 10]} name="Zona Carguío" />

          {/* Trabajadores */}
          <WorkerAvatar position={[0, 0, 0]} riskLevel={workerRisk} label="W-001 (Juan)" />
          <WorkerAvatar position={[-5, 0, 8]} riskLevel="BAJO" label="W-002 (Ana)" />

          {/* Maquinaria */}
          <MachineModel position={[4, 0, 0]} riskLevel={machineRisk} label="M-001 (LHD)" />
        </Suspense>

        {/* Controles de cámara */}
        <OrbitControls
          makeDefault
          maxPolarAngle={Math.PI / 2 - 0.05}
          minDistance={2}
          maxDistance={40}
        />
      </Canvas>

      <InfoPanel3D activeAlert={activeAlert} />
    </>
  );
}
