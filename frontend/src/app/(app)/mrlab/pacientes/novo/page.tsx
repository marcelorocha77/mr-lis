"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";

export default function NovoPacientePage() {
  const router = useRouter();
  const [form, setForm] = useState({
    full_name: "", cpf: "", birth_date: "", sex: "", phone: "", email: "", mother_name: "",
    address_street: "", address_number: "", address_district: "",
    address_city: "", address_state: "", address_zip: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set<K extends keyof typeof form>(k: K, v: string) {
    setForm((s) => ({ ...s, [k]: v }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const body: Record<string, unknown> = { ...form };
      for (const k of Object.keys(body)) if (body[k] === "") body[k] = null;
      await api("/mrlab/pacientes", { method: "POST", json: body });
      router.push("/mrlab/pacientes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold text-slate-800 mb-4">Novo paciente</h1>
      <form onSubmit={submit} className="space-y-4">
        <Card>
          <CardHeader><CardTitle>Dados pessoais</CardTitle></CardHeader>
          <CardBody className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="full_name">Nome completo *</Label>
              <Input id="full_name" required value={form.full_name} onChange={(e) => set("full_name", e.target.value)} />
            </div>
            <div><Label>CPF</Label><Input value={form.cpf} onChange={(e) => set("cpf", e.target.value)} /></div>
            <div><Label>Data de nascimento</Label><Input type="date" value={form.birth_date} onChange={(e) => set("birth_date", e.target.value)} /></div>
            <div>
              <Label>Sexo</Label>
              <select className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm" value={form.sex} onChange={(e) => set("sex", e.target.value)}>
                <option value="">—</option><option value="F">Feminino</option><option value="M">Masculino</option><option value="I">Indefinido</option>
              </select>
            </div>
            <div><Label>Telefone</Label><Input value={form.phone} onChange={(e) => set("phone", e.target.value)} /></div>
            <div><Label>E-mail</Label><Input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} /></div>
            <div className="md:col-span-2"><Label>Nome da mãe</Label><Input value={form.mother_name} onChange={(e) => set("mother_name", e.target.value)} /></div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Endereço</CardTitle></CardHeader>
          <CardBody className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div className="md:col-span-4"><Label>Rua</Label><Input value={form.address_street} onChange={(e) => set("address_street", e.target.value)} /></div>
            <div className="md:col-span-1"><Label>Número</Label><Input value={form.address_number} onChange={(e) => set("address_number", e.target.value)} /></div>
            <div className="md:col-span-1"><Label>CEP</Label><Input value={form.address_zip} onChange={(e) => set("address_zip", e.target.value)} /></div>
            <div className="md:col-span-3"><Label>Bairro</Label><Input value={form.address_district} onChange={(e) => set("address_district", e.target.value)} /></div>
            <div className="md:col-span-2"><Label>Cidade</Label><Input value={form.address_city} onChange={(e) => set("address_city", e.target.value)} /></div>
            <div className="md:col-span-1"><Label>UF</Label><Input maxLength={2} value={form.address_state} onChange={(e) => set("address_state", e.target.value.toUpperCase())} /></div>
          </CardBody>
        </Card>

        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex items-center gap-2 justify-end">
          <Button type="button" variant="secondary" onClick={() => router.back()}>Cancelar</Button>
          <Button type="submit" disabled={saving}>{saving ? "Salvando..." : "Salvar"}</Button>
        </div>
      </form>
    </div>
  );
}
