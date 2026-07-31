"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type Violation = {
  id: number; qc_run_id: number; rule_code: string; severity: string;
  resolved_at: string | null; notes: string | null;
};

const sevColor: Record<string, string> = {
  warning: "bg-amber-100 text-amber-700",
  rejection: "bg-red-100 text-red-700",
};

export default function ViolacoesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["violations"],
    queryFn: () => api<Violation[]>("/mrquality/violacoes?only_open=true"),
    refetchInterval: 15_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-brand-600" /> Violações Westgard
        </h1>
        <p className="text-sm text-slate-500">Regras violadas e pendentes de resolução</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Violações abertas</CardTitle></CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Dosagem</th>
                <th className="text-left px-4 py-2">Regra</th>
                <th className="text-left px-4 py-2">Severidade</th>
                <th className="text-left px-4 py-2">Resolvida</th>
                <th className="text-left px-4 py-2">Notas</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
              {!isLoading && data?.length === 0 && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Nenhuma violação aberta.</td></tr>}
              {data?.map((v) => (
                <tr key={v.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono text-xs">#{v.qc_run_id}</td>
                  <td className="px-4 py-2 font-mono">{v.rule_code}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-1 rounded ${sevColor[v.severity]}`}>{v.severity}</span>
                  </td>
                  <td className="px-4 py-2 text-slate-600">{v.resolved_at ? fmtDate(v.resolved_at) : "—"}</td>
                  <td className="px-4 py-2 text-slate-500">{v.notes ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
