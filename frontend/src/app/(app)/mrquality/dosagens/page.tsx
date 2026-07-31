"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { ClipboardEdit } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type Analyte = { id: number; qc_lot_id: number; exam_id: number };
type Run = { id: number; qc_analyte_id: number; run_at: string; value: string; z_score: string | null; equipment_batch: string | null; notes: string | null };

export default function DosagensPage() {
  const qc = useQueryClient();
  const [analyteId, setAnalyteId] = useState<number | null>(null);
  const analytes = useQuery({ queryKey: ["analytes-all"], queryFn: () => api<Analyte[]>("/mrquality/analitos") });
  const runs = useQuery({
    queryKey: ["runs", analyteId],
    queryFn: () => analyteId ? api<Run[]>(`/mrquality/dosagens/${analyteId}?limit=50`) : Promise.resolve([]),
    enabled: analyteId !== null,
  });

  const submit = useMutation({
    mutationFn: (body: { qc_analyte_id: number; value: string; equipment_batch?: string; notes?: string }) =>
      api("/mrquality/dosagens", { method: "POST", json: body }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["runs"] }); qc.invalidateQueries({ queryKey: ["mrquality-painel"] }); },
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <ClipboardEdit className="w-6 h-6 text-brand-600" /> Lançar dosagem QC
        </h1>
        <p className="text-sm text-slate-500">Registrar leitura de material de controle — regras Westgard são aplicadas automaticamente</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Nova dosagem</CardTitle></CardHeader>
        <CardBody>
          <form className="grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            const id = Number(fd.get("qc_analyte_id"));
            setAnalyteId(id);
            submit.mutate({
              qc_analyte_id: id,
              value: fd.get("value") as string,
              equipment_batch: (fd.get("equipment_batch") as string) || undefined,
              notes: (fd.get("notes") as string) || undefined,
            });
          }}>
            <div className="md:col-span-2">
              <Label>QC-Analito *</Label>
              <select
                name="qc_analyte_id"
                required
                className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
                value={analyteId ?? ""}
                onChange={(e) => setAnalyteId(Number(e.target.value) || null)}
              >
                <option value="">Selecione...</option>
                {analytes.data?.map((a) => (
                  <option key={a.id} value={a.id}>QC-analito #{a.id}</option>
                ))}
              </select>
            </div>
            <div><Label>Valor *</Label><Input name="value" type="number" step="0.0001" required /></div>
            <div><Label>Lote reagente</Label><Input name="equipment_batch" /></div>
            <div className="md:col-span-3"><Label>Observações</Label><Input name="notes" /></div>
            <div className="md:col-span-4 text-right">
              <Button type="submit" disabled={submit.isPending}>{submit.isPending ? "Registrando..." : "Registrar"}</Button>
            </div>
          </form>
        </CardBody>
      </Card>

      {analyteId && (
        <Card>
          <CardHeader><CardTitle>Últimas dosagens (analito #{analyteId})</CardTitle></CardHeader>
          <CardBody className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="text-left px-4 py-2">Quando</th>
                  <th className="text-right px-4 py-2">Valor</th>
                  <th className="text-right px-4 py-2">Z-score</th>
                  <th className="text-left px-4 py-2">Reagente</th>
                  <th className="text-left px-4 py-2">Obs</th>
                </tr>
              </thead>
              <tbody>
                {runs.data?.length === 0 && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Nenhuma dosagem.</td></tr>}
                {runs.data?.map((r) => (
                  <tr key={r.id} className="border-t border-slate-100">
                    <td className="px-4 py-2 text-slate-600 text-xs">{fmtDate(r.run_at)}</td>
                    <td className="px-4 py-2 text-right font-mono">{r.value}</td>
                    <td className="px-4 py-2 text-right font-mono">{r.z_score ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{r.equipment_batch ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-500">{r.notes ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
