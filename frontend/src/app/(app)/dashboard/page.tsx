"use client";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Users, ClipboardList, FileText, Activity } from "lucide-react";

type Stat = { label: string; value: string | number; icon: React.ComponentType<{ className?: string }>; hint?: string };

function StatCard({ s }: { s: Stat }) {
  const Icon = s.icon;
  return (
    <Card>
      <CardBody className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-lg bg-brand-100 text-brand-700 flex items-center justify-center">
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">{s.label}</div>
          <div className="text-2xl font-semibold text-slate-800">{s.value}</div>
          {s.hint && <div className="text-xs text-slate-500">{s.hint}</div>}
        </div>
      </CardBody>
    </Card>
  );
}

export default function DashboardPage() {
  const patients = useQuery({
    queryKey: ["patients-count"],
    queryFn: () => api<Page<unknown>>("/mrlab/pacientes?page=1&page_size=1"),
  });
  const requests = useQuery({
    queryKey: ["requests-count"],
    queryFn: () => api<Page<unknown>>("/mrlab/requisicoes?page=1&page_size=1"),
  });
  const laudos = useQuery({
    queryKey: ["laudos-pendentes"],
    queryFn: () => api<unknown[]>("/mrlablaudo/pendentes"),
  });

  const stats: Stat[] = [
    { label: "Pacientes", value: patients.data?.total ?? "—", icon: Users, hint: "cadastrados" },
    { label: "Requisições", value: requests.data?.total ?? "—", icon: ClipboardList, hint: "total no sistema" },
    { label: "Laudos pendentes", value: (laudos.data?.length ?? "—") as number, icon: FileText, hint: "para liberar" },
    { label: "Equipamentos", value: "3", icon: Activity, hint: "conectados" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500">Visão geral do laboratório</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => <StatCard key={s.label} s={s} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Requisições recentes</CardTitle></CardHeader>
          <CardBody className="text-sm text-slate-500">
            Em breve — lista das últimas requisições recebidas.
          </CardBody>
        </Card>
        <Card>
          <CardHeader><CardTitle>Prazo (turnaround)</CardTitle></CardHeader>
          <CardBody className="text-sm text-slate-500">
            Em breve — % de exames dentro do TAT por setor.
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
