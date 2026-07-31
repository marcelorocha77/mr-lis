"use client";
import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Search } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type Patient = {
  id: number;
  full_name: string;
  cpf: string | null;
  birth_date: string | null;
  sex: string | null;
  phone: string | null;
  created_at: string;
};

export default function PacientesPage() {
  const [q, setQ] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["pacientes", q],
    queryFn: () => api<Page<Patient>>(`/mrlab/pacientes?q=${encodeURIComponent(q)}&page_size=50`),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Pacientes</h1>
          <p className="text-sm text-slate-500">Cadastro de pacientes</p>
        </div>
        <Link href="/mrlab/pacientes/novo"><Button><Plus className="w-4 h-4" />Novo paciente</Button></Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-400" />
            <Input placeholder="Buscar por nome ou CPF..." value={q} onChange={(e) => setQ(e.target.value)} className="max-w-md" />
          </div>
        </CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="text-left px-4 py-2">Nome</th>
                  <th className="text-left px-4 py-2">CPF</th>
                  <th className="text-left px-4 py-2">Nascimento</th>
                  <th className="text-left px-4 py-2">Sexo</th>
                  <th className="text-left px-4 py-2">Telefone</th>
                  <th className="text-left px-4 py-2">Cadastrado em</th>
                  <th className="w-10" />
                </tr>
              </thead>
              <tbody>
                {isLoading && (
                  <tr><td colSpan={7} className="px-4 py-6 text-center text-slate-400">Carregando...</td></tr>
                )}
                {!isLoading && data?.items.length === 0 && (
                  <tr><td colSpan={7} className="px-4 py-6 text-center text-slate-400">Nenhum paciente encontrado.</td></tr>
                )}
                {data?.items.map((p) => (
                  <tr key={p.id} className="border-t border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-2 font-medium text-slate-800">{p.full_name}</td>
                    <td className="px-4 py-2 text-slate-600">{p.cpf ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{p.birth_date ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{p.sex ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{p.phone ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-500">{fmtDate(p.created_at)}</td>
                    <td className="px-4 py-2 text-right">
                      <Link href={`/mrlab/pacientes/${p.id}`} className="text-brand-600 hover:underline">Editar</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data && (
            <div className="px-4 py-2 text-xs text-slate-500 border-t border-slate-100">
              {data.total} paciente(s)
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
