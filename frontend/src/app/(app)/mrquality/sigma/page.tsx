"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Sigma } from "lucide-react";

type SigmaRow = {
  analyte_id: number; exam_code: string; exam_name: string;
  lot_number: string; level: string;
  mean: string | null; sd: string | null; cv_percent: string | null;
  bias_percent: string | null; tea_percent: string | null;
  sigma: string | null; classification: string;
};

const classColor: Record<string, string> = {
  "world-class": "bg-emerald-100 text-emerald-700",
  aceitavel: "bg-amber-100 text-amber-700",
  ruim: "bg-red-100 text-red-700",
  na: "bg-slate-100 text-slate-500",
};

export default function SigmaPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["sigma"],
    queryFn: () => api<SigmaRow[]>("/mrquality/sigma-westgard"),
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Sigma className="w-6 h-6 text-brand-600" /> Sigma-Westgard
        </h1>
        <p className="text-sm text-slate-500">σ = (TEa − |Bias|) / CV — mundo-classe ≥ 6, aceitável ≥ 4, ruim &lt; 3</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Métrica por QC-analito</CardTitle></CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Exame</th>
                <th className="text-left px-4 py-2">Lote</th>
                <th className="text-right px-4 py-2">CV%</th>
                <th className="text-right px-4 py-2">Bias%</th>
                <th className="text-right px-4 py-2">TEa%</th>
                <th className="text-right px-4 py-2">σ</th>
                <th className="text-left px-4 py-2">Classificação</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && <tr><td colSpan={7} className="text-center text-slate-400 py-6">Calculando...</td></tr>}
              {!isLoading && data?.length === 0 && <tr><td colSpan={7} className="text-center text-slate-400 py-6">Nenhum analito com dados suficientes.</td></tr>}
              {data?.map((r) => (
                <tr key={r.analyte_id} className="border-t border-slate-100">
                  <td className="px-4 py-2">
                    <div className="font-medium">{r.exam_code}</div>
                    <div className="text-xs text-slate-500">{r.exam_name}</div>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{r.lot_number} ({r.level})</td>
                  <td className="px-4 py-2 text-right font-mono">{r.cv_percent ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{r.bias_percent ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-mono">{r.tea_percent ?? "—"}</td>
                  <td className="px-4 py-2 text-right font-semibold text-slate-800">{r.sigma ?? "—"}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-1 rounded ${classColor[r.classification]}`}>{r.classification}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
