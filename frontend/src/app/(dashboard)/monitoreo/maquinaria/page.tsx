'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface Machine {
  id: number;
  machine_code: string;
  type: string;
  model: string;
  status: string;
}

export default function MaquinariaPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMachines = async () => {
      try {
        const res = await api.get('/machines/');
        setMachines(res.data);
      } catch (err) {
        console.error('Error fetching machines', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMachines();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPERATING':
        return <Badge className="bg-emerald-600">Operando</Badge>;
      case 'IDLE':
        return <Badge variant="secondary">Detenida</Badge>;
      case 'MAINTENANCE':
        return <Badge variant="destructive">Mantenimiento</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Maquinaria</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>Listado de Equipos Pesados</CardTitle>
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
                  <TableHead>Tipo</TableHead>
                  <TableHead>Modelo</TableHead>
                  <TableHead>Estado Actual</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {machines.map((machine) => (
                  <TableRow key={machine.id}>
                    <TableCell>{machine.id}</TableCell>
                    <TableCell className="font-medium">{machine.machine_code}</TableCell>
                    <TableCell>{machine.type}</TableCell>
                    <TableCell>{machine.model}</TableCell>
                    <TableCell>{getStatusBadge(machine.status)}</TableCell>
                  </TableRow>
                ))}
                {machines.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-4">No hay maquinaria registrada.</TableCell>
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
