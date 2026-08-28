'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Grid, Stats } from '@react-three/drei';
import TunnelGeometry from './TunnelGeometry';
import WorkerAvatar from './WorkerAvatar';
import MachineModel from './MachineModel';
import RestrictedZone from './RestrictedZone';
import InfoPanel3D from './InfoPanel3D';
import { useAlertStore } from '@/store/alertStore';
import { Suspense } from 'react';

export default function Scene3D() {
  // We will get the active alerts to determine the risk level of the worker/machine
  const alerts = useAlertStore((state) => state.alerts);
  const activeAlert = alerts.length > 0 ? alerts[0] : null;

  // Derive risk levels for our mock entities
  const workerRisk = activeAlert?.worker_id === 1 ? activeAlert.risk_level : 'BAJO';
  const machineRisk = activeAlert?.machine_id === 1 ? activeAlert.risk_level : 'BAJO';

  return (
    <>
      <Canvas
        camera={{ position: [10, 10, 10], fov: 50 }}
        shadows
        className="w-full h-full"
      >
        <color attach="background" args={['#1a1a1a']} />
        
        {/* Luces */}
        <ambientLight intensity={0.5} />
        <directionalLight 
          position={[10, 20, 10]} 
          intensity={1} 
          castShadow 
          shadow-mapSize={[1024, 1024]}
        />
        <pointLight position={[0, 5, 0]} intensity={0.8} color="#fff" />

        {/* Entorno base */}
        <Suspense fallback={null}>
          <Environment preset="city" />
          <Grid 
            infiniteGrid 
            fadeDistance={50} 
            sectionColor="#4a4a4a" 
            cellColor="#2b2b2b" 
            position={[0, -0.01, 0]} 
          />
          
          {/* El Túnel */}
          <TunnelGeometry />

          {/* Zona Restringida (Mock 1) */}
          <RestrictedZone position={[5, 0, -5]} size={[10, 4, 10]} name="Zona Carguío" />

          {/* Trabajador (Mock ID 1) */}
          <WorkerAvatar position={[0, 0, 0]} riskLevel={workerRisk} label="W-001 (Juan)" />
          
          {/* Trabajador (Mock ID 2 - Seguro) */}
          <WorkerAvatar position={[-5, 0, 8]} riskLevel="BAJO" label="W-002 (Ana)" />

          {/* Maquinaria (Mock ID 1) */}
          <MachineModel position={[4, 0, 0]} riskLevel={machineRisk} label="M-001 (LHD)" />

        </Suspense>

        {/* Controles de cámara */}
        <OrbitControls 
          makeDefault
          maxPolarAngle={Math.PI / 2 - 0.05} // No bajar más allá del piso
          minDistance={2}
          maxDistance={40}
        />
        
        {/* Métricas de rendimiento (Solo desarrollo) */}
        <Stats />
      </Canvas>
      <InfoPanel3D activeAlert={activeAlert} />
    </>
  );
}
