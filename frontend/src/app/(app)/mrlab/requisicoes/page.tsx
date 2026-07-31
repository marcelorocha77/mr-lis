"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type Req = {
  id: number;
  number: string;
  patient_id: number;
  status: string;
  received_datetime: string;
  items: { id: number; exam_id: number; status: string }[];
};

const statusColor: Record<string, string> = {
  aberta: "bg-slate-100 text-slate-700",
  coletada: "bg-blue-100 text-blue-700",
  em_processo: "bg-amber-100 text-amber-700",
  liberada: "bg-emerald-100 text-emerald-700",
  cancelada: "bg-red-100 text-red-700",
  entregue: "bg-purple-100 text-purple-700",
};

export default function RequisicoesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["requisicoes"],
    queryFn: () => api<Page<Req>>("/mrlab/requisicoes?page_size=50"),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Requisições</h1>
          <p className="text-sm text-slate-500">Pedidos de exames</p>
        </div>
        <Link href="/mrlab/requisicoes/nova"><Button><Plus className="w-4 h-4" />Nova requisição</Button></Link>
      </div>

      <Card>
        <CardHeader><CardTitle>Últimas requisições</CardTitle></CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="text-left px-4 py-2">Número</th>
                  <th className="text-left px-4 py-2">Paciente</th>
                  <th className="text-left px-4 py-2">Recebida</th>
                  <th className="text-left px-4 py-2">Exames</th>
                  <th className="text-left px-4 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {isLoading && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
                {!isLoading && data?.items.length === 0 && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Nenhuma requisição.</td></tr>}
                {data?.items.map((r) => (
                  <tr key={r.id} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-mono">{r.number}</td>
                    <td className="px-4 py-2">#{r.patient_id}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtDate(r.received_datetime)}</td>
                    <td className="px-4 py-2 text-slate-600">{r.items.length}</td>
                    <td className="px-4 py-2">
                      <span className={`text-xs px-2 py-1 rounded ${statusColor[r.status] ?? "bg-slate-100 text-slate-700"}`}>
                        {r.status}
                      </span>
                    </td>
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
