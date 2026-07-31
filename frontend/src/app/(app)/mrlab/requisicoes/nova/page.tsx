"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Trash2 } from "lucide-react";

type Patient = { id: number; full_name: string; cpf: string | null };
type Doctor = { id: number; full_name: string; crm: string; crm_uf: string };
type Insurance = { id: number; code: string; name: string };
type Exam = { id: number; code: string; name: string; section: string | null; price: string };

export default function NovaRequisicaoPage() {
  const router = useRouter();
  const [patientId, setPatientId] = useState<number | null>(null);
  const [doctorId, setDoctorId] = useState<number | null>(null);
  const [insuranceId, setInsuranceId] = useState<number | null>(null);
  const [items, setItems] = useState<Exam[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const pacientes = useQuery({ queryKey: ["pac-select"], queryFn: () => api<Page<Patient>>("/mrlab/pacientes?page_size=200") });
  const medicos = useQuery({ queryKey: ["med-select"], queryFn: () => api<Page<Doctor>>("/mrlab/medicos?page_size=200") });
  const convenios = useQuery({ queryKey: ["conv-select"], queryFn: () => api<Page<Insurance>>("/mrlab/convenios?page_size=200") });
  const exames = useQuery({ queryKey: ["ex-select"], queryFn: () => api<Page<Exam>>("/mrlab/exames?page_size=500") });

  function addExam(e: Exam) {
    if (items.find((i) => i.id === e.id)) return;
    setItems([...items, e]);
  }

  async function submit() {
    if (!patientId) { setError("Selecione um paciente"); return; }
    if (items.length === 0) { setError("Adicione ao menos um exame"); return; }
    setSaving(true);
    setError(null);
    try {
      await api("/mrlab/requisicoes", {
        method: "POST",
        json: {
          patient_id: patientId,
          doctor_id: doctorId,
          insurance_id: insuranceId,
          items: items.map((e) => ({ exam_id: e.id })),
        },
      });
      router.push("/mrlab/requisicoes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar");
    } finally {
      setSaving(false);
    }
  }

  const total = items.reduce((sum, e) => sum + parseFloat(e.price || "0"), 0);

  return (
    <div className="max-w-5xl space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Nova requisição</h1>

      <Card>
        <CardHeader><CardTitle>Paciente e solicitante</CardTitle></CardHeader>
        <CardBody className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label>Paciente *</Label>
            <select className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm" value={patientId ?? ""} onChange={(e) => setPatientId(Number(e.target.value) || null)}>
              <option value="">Selecione...</option>
              {pacientes.data?.items.map((p) => (
                <option key={p.id} value={p.id}>{p.full_name} {p.cpf ? `(${p.cpf})` : ""}</option>
              ))}
            </select>
          </div>
          <div>
            <Label>Médico</Label>
            <select className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm" value={doctorId ?? ""} onChange={(e) => setDoctorId(Number(e.target.value) || null)}>
              <option value="">—</option>
              {medicos.data?.items.map((d) => (
                <option key={d.id} value={d.id}>{d.full_name} — CRM {d.crm_uf} {d.crm}</option>
              ))}
            </select>
          </div>
          <div>
            <Label>Convênio</Label>
            <select className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm" value={insuranceId ?? ""} onChange={(e) => setInsuranceId(Number(e.target.value) || null)}>
              <option value="">—</option>
              {convenios.data?.items.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader><CardTitle>Exames solicitados</CardTitle></CardHeader>
        <CardBody className="space-y-3">
          <div>
            <Label>Adicionar exame</Label>
            <select
              className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
              onChange={(e) => {
                const ex = exames.data?.items.find((x) => x.id === Number(e.target.value));
                if (ex) addExam(ex);
                e.currentTarget.value = "";
              }}
            >
              <option value="">Selecione um exame...</option>
              {exames.data?.items.map((e) => (
                <option key={e.id} value={e.id}>{e.code} — {e.name}</option>
              ))}
            </select>
          </div>

          {items.length > 0 && (
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-3 py-2">Código</th>
                  <th className="text-left px-3 py-2">Exame</th>
                  <th className="text-left px-3 py-2">Setor</th>
                  <th className="text-right px-3 py-2">Preço</th>
                  <th className="w-10" />
                </tr>
              </thead>
              <tbody>
                {items.map((e) => (
                  <tr key={e.id} className="border-t border-slate-100">
                    <td className="px-3 py-2 font-mono">{e.code}</td>
                    <td className="px-3 py-2">{e.name}</td>
                    <td className="px-3 py-2 text-slate-600">{e.section ?? "—"}</td>
                    <td className="px-3 py-2 text-right">R$ {parseFloat(e.price).toFixed(2)}</td>
                    <td className="px-3 py-2 text-right">
                      <button onClick={() => setItems(items.filter((i) => i.id !== e.id))}>
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </td>
                  </tr>
                ))}
                <tr className="border-t-2 border-slate-200 font-semibold">
                  <td colSpan={3} className="px-3 py-2 text-right">Total:</td>
                  <td className="px-3 py-2 text-right">R$ {total.toFixed(2)}</td>
                  <td />
                </tr>
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>

      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={() => router.back()}>Cancelar</Button>
        <Button onClick={submit} disabled={saving}>{saving ? "Salvando..." : "Criar requisição"}</Button>
      </div>
    </div>
  );
}
