"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldAlert } from "lucide-react";

type Equip = { name: string; status: string; last_seen: string | null; pending_results: number };

const statusColor: Record<string, string> = {
  online: "bg-emerald-100 text-emerald-700",
  offline: "bg-red-100 text-red-700",
  warning: "bg-amber-100 text-amber-700",
};

export default function MRGuardianPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["equipamentos"],
    queryFn: () => api<Equip[]>("/mrguardian/equipamentos"),
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-brand-600" /> MRGuardian
        </h1>
        <p className="text-sm text-slate-500">Monitoramento em tempo real</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Equipamentos conectados</CardTitle></CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Equipamento</th>
                <th className="text-left px-4 py-2">Status</th>
                <th className="text-left px-4 py-2">Resultados pendentes</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && <tr><td colSpan={3} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
              {data?.map((e) => (
                <tr key={e.name} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium">{e.name}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-1 rounded ${statusColor[e.status] ?? "bg-slate-100"}`}>{e.status}</span>
                  </td>
                  <td className="px-4 py-2">{e.pending_results}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>

      <Card>
        <CardHeader><CardTitle>Alarmes ativos</CardTitle></CardHeader>
        <CardBody className="text-sm text-slate-500">Nenhum alarme ativo.</CardBody>
      </Card>
    </div>
  );
}
