"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";

type Patient = {
  id: number;
  full_name: string;
  cpf: string | null;
  social_name: string | null;
  birth_date: string | null;
  sex: string | null;
  phone: string | null;
  email: string | null;
  mother_name: string | null;
  address_street: string | null;
  address_number: string | null;
  address_complement: string | null;
  address_district: string | null;
  address_city: string | null;
  address_state: string | null;
  address_zip: string | null;
};

export default function EditarPacientePage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const [form, setForm] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Patient>(`/mrlab/pacientes/${id}`)
      .then((p) => setForm(p))
      .catch((e) => setError(e instanceof Error ? e.message : "Erro"))
      .finally(() => setLoading(false));
  }, [id]);

  function set<K extends keyof Patient>(k: K, v: Patient[K]) {
    setForm((s) => (s ? { ...s, [k]: v } : s));
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!form) return;
    setSaving(true); setError(null);
    try {
      const body: Record<string, unknown> = { ...form };
      delete body.id;
      for (const k of Object.keys(body)) if (body[k] === "") body[k] = null;
      await api(`/mrlab/pacientes/${id}`, { method: "PATCH", json: body });
      router.push("/mrlab/pacientes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally { setSaving(false); }
  }

  async function remove() {
    if (!confirm("Excluir este paciente?")) return;
    setSaving(true); setError(null);
    try {
      await api(`/mrlab/pacientes/${id}`, { method: "DELETE" });
      router.push("/mrlab/pacientes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally { setSaving(false); }
  }

  if (loading) return <div className="text-slate-500">Carregando...</div>;
  if (!form) return <div className="text-red-600">{error || "Paciente não encontrado"}</div>;

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold text-slate-800 mb-4">Editar paciente #{form.id}</h1>
      <form onSubmit={save} className="space-y-4">
        <Card>
          <CardHeader><CardTitle>Dados pessoais</CardTitle></CardHeader>
          <CardBody className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <Label>Nome completo *</Label>
              <Input required value={form.full_name ?? ""} onChange={(e) => set("full_name", e.target.value)} />
            </div>
            <div><Label>CPF</Label><Input value={form.cpf ?? ""} onChange={(e) => set("cpf", e.target.value)} /></div>
            <div><Label>Nascimento</Label><Input type="date" value={form.birth_date ?? ""} onChange={(e) => set("birth_date", e.target.value)} /></div>
            <div>
              <Label>Sexo</Label>
              <select className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm" value={form.sex ?? ""} onChange={(e) => set("sex", e.target.value)}>
                <option value="">—</option><option value="F">F</option><option value="M">M</option><option value="I">I</option>
              </select>
            </div>
            <div><Label>Telefone</Label><Input value={form.phone ?? ""} onChange={(e) => set("phone", e.target.value)} /></div>
            <div><Label>E-mail</Label><Input type="email" value={form.email ?? ""} onChange={(e) => set("email", e.target.value)} /></div>
            <div className="md:col-span-2"><Label>Nome da mãe</Label><Input value={form.mother_name ?? ""} onChange={(e) => set("mother_name", e.target.value)} /></div>
          </CardBody>
        </Card>
        <Card>
          <CardHeader><CardTitle>Endereço</CardTitle></CardHeader>
          <CardBody className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div className="md:col-span-4"><Label>Rua</Label><Input value={form.address_street ?? ""} onChange={(e) => set("address_street", e.target.value)} /></div>
            <div><Label>Número</Label><Input value={form.address_number ?? ""} onChange={(e) => set("address_number", e.target.value)} /></div>
            <div><Label>CEP</Label><Input value={form.address_zip ?? ""} onChange={(e) => set("address_zip", e.target.value)} /></div>
            <div className="md:col-span-3"><Label>Bairro</Label><Input value={form.address_district ?? ""} onChange={(e) => set("address_district", e.target.value)} /></div>
            <div className="md:col-span-2"><Label>Cidade</Label><Input value={form.address_city ?? ""} onChange={(e) => set("address_city", e.target.value)} /></div>
            <div><Label>UF</Label><Input maxLength={2} value={form.address_state ?? ""} onChange={(e) => set("address_state", e.target.value.toUpperCase())} /></div>
          </CardBody>
        </Card>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex items-center justify-between">
          <Button type="button" variant="danger" onClick={remove} disabled={saving}>Excluir</Button>
          <div className="flex items-center gap-2">
            <Button type="button" variant="secondary" onClick={() => router.back()}>Cancelar</Button>
            <Button type="submit" disabled={saving}>{saving ? "Salvando..." : "Salvar"}</Button>
          </div>
        </div>
      </form>
    </div>
  );
}
