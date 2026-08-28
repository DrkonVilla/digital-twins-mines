'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface Worker {
  id: number;
  worker_code: string;
  full_name: string;
  role_job: string;
  area: string;
  is_active: boolean;
}

export default function WorkersPage() {
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorkers = async () => {
      try {
        const res = await api.get('/workers/');
        setWorkers(res.data);
      } catch (err) {
        console.error('Error fetching workers', err);
      } finally {
        setLoading(false);
      }
    };
    fetchWorkers();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Trabajadores</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>Listado de Personal en Terreno</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Cargando datos...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Código</TableHead>
                  <TableHead>Nombre Completo</TableHead>
                  <TableHead>Rol</TableHead>
                  <TableHead>Área</TableHead>
                  <TableHead>Estado</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {workers.map((worker) => (
                  <TableRow key={worker.id}>
                    <TableCell>{worker.id}</TableCell>
                    <TableCell className="font-medium">{worker.worker_code}</TableCell>
                    <TableCell>{worker.full_name}</TableCell>
                    <TableCell>{worker.role_job}</TableCell>
                    <TableCell>{worker.area}</TableCell>
                    <TableCell>
                      {worker.is_active ? (
                        <Badge variant="default" className="bg-emerald-600">Activo</Badge>
                      ) : (
                        <Badge variant="secondary">Inactivo</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {workers.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-4">No hay trabajadores registrados.</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
