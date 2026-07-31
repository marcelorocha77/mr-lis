"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Plus, X } from "lucide-react";

type Analyte = {
  id: number; qc_lot_id: number; exam_id: number; equipment_id: number | null;
  package_insert_mean: string | null; package_insert_sd: string | null;
  internal_mean: string | null; internal_sd: string | null; internal_cv: string | null;
  tea_percent: string | null; active_rules: Record<string, unknown>; is_active: boolean;
};
type Lot = { id: number; product_name: string; lot_number: string; level: string };
type Exam = { id: number; code: string; name: string };
type Equipment = { id: number; code: string; name: string };
type Rule = { code: string; description: string; kind: string };

const DEFAULT_RULES = ["1_2s", "1_3s", "2_2s", "R_4s", "4_1s", "10x"];

export default function AnalitosPage() {
  const qc = useQueryClient();
  const [show, setShow] = useState(false);
  const [rules, setRules] = useState<string[]>(DEFAULT_RULES);
  const list = useQuery({ queryKey: ["qc-analytes"], queryFn: () => api<Analyte[]>("/mrquality/analitos") });
  const lots = useQuery({ queryKey: ["qc-lots"], queryFn: () => api<Lot[]>("/mrquality/lotes") });
  const exams = useQuery({ queryKey: ["exams-all"], queryFn: () => api<Page<Exam>>("/mrlab/exames?page_size=500") });
  const equipments = useQuery({ queryKey: ["equipments-all"], queryFn: () => api<Equipment[]>("/mrinterface/equipamentos") });
  const rulesList = useQuery({ queryKey: ["westgard-rules"], queryFn: () => api<Rule[]>("/mrquality/regras") });

  const create = useMutation({
    mutationFn: (body: Record<string, unknown>) => api("/mrquality/analitos", { method: "POST", json: body }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["qc-analytes"] }); setShow(false); },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">QC-Analitos</h1>
          <p className="text-sm text-slate-500">Configuração de controle por exame × lote × equipamento</p>
        </div>
        <Button onClick={() => setShow(true)}><Plus className="w-4 h-4" />Novo QC-Analito</Button>
      </div>

      {show && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Novo QC-Analito</CardTitle>
            <button onClick={() => setShow(false)}><X className="w-4 h-4 text-slate-500" /></button>
          </CardHeader>
          <CardBody>
            <form className="grid grid-cols-1 md:grid-cols-6 gap-3" onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              create.mutate({
                qc_lot_id: Number(fd.get("qc_lot_id")),
                exam_id: Number(fd.get("exam_id")),
                equipment_id: Number(fd.get("equipment_id")) || null,
                package_insert_mean: fd.get("pi_mean") || null,
                package_insert_sd: fd.get("pi_sd") || null,
                internal_mean: fd.get("in_mean") || null,
                internal_sd: fd.get("in_sd") || null,
                internal_cv: fd.get("in_cv") || null,
                tea_percent: fd.get("tea") || null,
                active_rules: { rules },
                is_active: true,
              });
            }}>
              <div className="md:col-span-2">
                <Label>Lote *</Label>
                <select name="qc_lot_id" required className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option value="">Selecione...</option>
                  {lots.data?.map((l) => (
                    <option key={l.id} value={l.id}>{l.product_name} - {l.lot_number} ({l.level})</option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2">
                <Label>Exame *</Label>
                <select name="exam_id" required className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option value="">Selecione...</option>
                  {exams.data?.items.map((e) => (
                    <option key={e.id} value={e.id}>{e.code} — {e.name}</option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2">
                <Label>Equipamento</Label>
                <select name="equipment_id" className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option value="">—</option>
                  {equipments.data?.map((eq) => (
                    <option key={eq.id} value={eq.id}>{eq.code} — {eq.name}</option>
                  ))}
                </select>
              </div>

              <div><Label>Média bula</Label><Input name="pi_mean" type="number" step="0.0001" /></div>
              <div><Label>SD bula</Label><Input name="pi_sd" type="number" step="0.0001" /></div>
              <div><Label>Média interna</Label><Input name="in_mean" type="number" step="0.0001" /></div>
              <div><Label>SD interno</Label><Input name="in_sd" type="number" step="0.0001" /></div>
              <div><Label>CV%</Label><Input name="in_cv" type="number" step="0.01" /></div>
              <div><Label>TEa%</Label><Input name="tea" type="number" step="0.01" /></div>

              <div className="md:col-span-6">
                <Label>Regras Westgard ativas</Label>
                <div className="flex flex-wrap gap-2 pt-1">
                  {rulesList.data?.map((r) => {
                    const on = rules.includes(r.code);
                    return (
                      <button
                        key={r.code}
                        type="button"
                        onClick={() => setRules(on ? rules.filter((x) => x !== r.code) : [...rules, r.code])}
                        className={`text-xs px-3 py-1 rounded ${on ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"}`}
                        title={r.description}
                      >{r.code}</button>
                    );
                  })}
                </div>
              </div>

              <div className="md:col-span-6 text-right"><Button type="submit" disabled={create.isPending}>Salvar</Button></div>
            </form>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">ID</th>
                <th className="text-left px-4 py-2">Lote</th>
                <th className="text-left px-4 py-2">Exame</th>
                <th className="text-right px-4 py-2">Média</th>
                <th className="text-right px-4 py-2">SD</th>
                <th className="text-right px-4 py-2">CV%</th>
                <th className="text-right px-4 py-2">TEa%</th>
              </tr>
            </thead>
            <tbody>
              {list.data?.length === 0 && <tr><td colSpan={7} className="text-center text-slate-400 py-6">Nenhum analito.</td></tr>}
              {list.data?.map((a) => {
                const lot = lots.data?.find((x) => x.id === a.qc_lot_id);
                const ex = exams.data?.items.find((x) => x.id === a.exam_id);
                return (
                  <tr key={a.id} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-mono text-xs">#{a.id}</td>
                    <td className="px-4 py-2">{lot ? `${lot.lot_number} (${lot.level})` : `#${a.qc_lot_id}`}</td>
                    <td className="px-4 py-2">{ex ? `${ex.code} — ${ex.name}` : `#${a.exam_id}`}</td>
                    <td className="px-4 py-2 text-right">{a.internal_mean ?? a.package_insert_mean ?? "—"}</td>
                    <td className="px-4 py-2 text-right">{a.internal_sd ?? a.package_insert_sd ?? "—"}</td>
                    <td className="px-4 py-2 text-right">{a.internal_cv ?? "—"}</td>
                    <td className="px-4 py-2 text-right">{a.tea_percent ?? "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
