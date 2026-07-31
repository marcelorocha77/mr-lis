"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Activity, AlertTriangle, Beaker, ClipboardEdit, FlaskConical, LineChart,
  ListChecks, ShieldCheck, Sigma, Wrench,
} from "lucide-react";

type Painel = {
  active_analytes: number;
  active_lots: number;
  open_rejections: number;
  open_warnings: number;
};

const shortcuts = [
  { href: "/mrquality/dosagens", label: "Lançar dosagem", icon: ClipboardEdit, desc: "Registrar leitura de controle" },
  { href: "/mrquality/levey-jennings", label: "Levey-Jennings", icon: LineChart, desc: "Gráfico de controle" },
  { href: "/mrquality/sigma", label: "Sigma-Westgard", icon: Sigma, desc: "Métrica σ por analito" },
  { href: "/mrquality/violacoes", label: "Violações", icon: AlertTriangle, desc: "Regras Westgard violadas" },
  { href: "/mrquality/analitos", label: "QC-Analitos", icon: Beaker, desc: "Cadastro por exame×lote" },
  { href: "/mrquality/lotes", label: "Lotes de controle", icon: FlaskConical, desc: "Cadastro de lotes QC" },
];

function KPI({ label, value, icon: Icon, color = "brand" }: { label: string; value: number | string; icon: React.ComponentType<{ className?: string }>; color?: "brand" | "red" | "amber" | "emerald" }) {
  const bg = { brand: "bg-brand-100 text-brand-700", red: "bg-red-100 text-red-700", amber: "bg-amber-100 text-amber-700", emerald: "bg-emerald-100 text-emerald-700" }[color];
  return (
    <Card>
      <CardBody className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${bg}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
          <div className="text-2xl font-semibold text-slate-800">{value}</div>
        </div>
      </CardBody>
    </Card>
  );
}

export default function MRQualityPainel() {
  const painel = useQuery({
    queryKey: ["mrquality-painel"],
    queryFn: () => api<Painel>("/mrquality/painel"),
    refetchInterval: 30_000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Activity className="w-6 h-6 text-brand-600" /> MRQuality
        </h1>
        <p className="text-sm text-slate-500">Controle interno de qualidade analítica</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI label="Analitos ativos" value={painel.data?.active_analytes ?? "—"} icon={Beaker} />
        <KPI label="Lotes ativos" value={painel.data?.active_lots ?? "—"} icon={FlaskConical} />
        <KPI label="Rejeições abertas" value={painel.data?.open_rejections ?? "—"} icon={AlertTriangle} color="red" />
        <KPI label="Avisos abertos" value={painel.data?.open_warnings ?? "—"} icon={ShieldCheck} color="amber" />
      </div>

      <div>
        <div className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-2">Ações rápidas</div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {shortcuts.map((s) => (
            <Link key={s.href} href={s.href}>
              <Card className="hover:border-brand-500 hover:shadow transition">
                <CardBody className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center">
                    <s.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-800">{s.label}</div>
                    <div className="text-xs text-slate-500">{s.desc}</div>
                  </div>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
