"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Plus, Search, X } from "lucide-react";

type Doctor = { id: number; full_name: string; crm: string; crm_uf: string; specialty: string | null; phone: string | null };

export default function MedicosPage() {
  const [q, setQ] = useState("");
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["medicos", q],
    queryFn: () => api<Page<Doctor>>(`/mrlab/medicos?q=${encodeURIComponent(q)}&page_size=50`),
  });

  const create = useMutation({
    mutationFn: (body: Omit<Doctor, "id">) => api("/mrlab/medicos", { method: "POST", json: body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["medicos"] });
      setShowForm(false);
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Médicos solicitantes</h1>
          <p className="text-sm text-slate-500">Cadastro de médicos</p>
        </div>
        <Button onClick={() => setShowForm(true)}><Plus className="w-4 h-4" />Novo médico</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Novo médico</CardTitle>
            <button onClick={() => setShowForm(false)}><X className="w-4 h-4 text-slate-500" /></button>
          </CardHeader>
          <CardBody>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                create.mutate({
                  full_name: fd.get("full_name") as string,
                  crm: fd.get("crm") as string,
                  crm_uf: (fd.get("crm_uf") as string).toUpperCase(),
                  specialty: (fd.get("specialty") as string) || null,
                  phone: (fd.get("phone") as string) || null,
                });
              }}
              className="grid grid-cols-1 md:grid-cols-6 gap-3"
            >
              <div className="md:col-span-3"><Label>Nome *</Label><Input name="full_name" required /></div>
              <div><Label>CRM *</Label><Input name="crm" required /></div>
              <div><Label>UF *</Label><Input name="crm_uf" required maxLength={2} /></div>
              <div><Label>Telefone</Label><Input name="phone" /></div>
              <div className="md:col-span-6"><Label>Especialidade</Label><Input name="specialty" /></div>
              <div className="md:col-span-6 text-right">
                <Button type="submit" disabled={create.isPending}>{create.isPending ? "Salvando..." : "Salvar"}</Button>
              </div>
            </form>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-400" />
            <Input placeholder="Buscar por nome ou CRM..." value={q} onChange={(e) => setQ(e.target.value)} className="max-w-md" />
          </div>
        </CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="text-left px-4 py-2">Nome</th>
                  <th className="text-left px-4 py-2">CRM</th>
                  <th className="text-left px-4 py-2">UF</th>
                  <th className="text-left px-4 py-2">Especialidade</th>
                  <th className="text-left px-4 py-2">Telefone</th>
                </tr>
              </thead>
              <tbody>
                {isLoading && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
                {!isLoading && data?.items.length === 0 && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Nenhum médico.</td></tr>}
                {data?.items.map((d) => (
                  <tr key={d.id} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-medium">{d.full_name}</td>
                    <td className="px-4 py-2">{d.crm}</td>
                    <td className="px-4 py-2">{d.crm_uf}</td>
                    <td className="px-4 py-2 text-slate-600">{d.specialty ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{d.phone ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
