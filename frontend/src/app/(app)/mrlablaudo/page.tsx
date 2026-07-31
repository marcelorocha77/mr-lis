"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, CheckCircle2 } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type LaudoSummary = {
  request_id: number;
  number: string;
  patient_id: number;
  status: string;
  received_datetime: string;
  ready_count: number;
  total_count: number;
};

export default function MRLABLaudoPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["laudos-pendentes-page"],
    queryFn: () => api<LaudoSummary[]>("/mrlablaudo/pendentes"),
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <FileText className="w-6 h-6 text-brand-600" /> MRLABLaudo
        </h1>
        <p className="text-sm text-slate-500">Emissão e liberação de laudos</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Requisições aguardando liberação</CardTitle></CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Requisição</th>
                <th className="text-left px-4 py-2">Paciente</th>
                <th className="text-left px-4 py-2">Recebida</th>
                <th className="text-left px-4 py-2">Progresso</th>
                <th className="text-left px-4 py-2">Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {isLoading && <tr><td colSpan={6} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
              {!isLoading && data?.length === 0 && <tr><td colSpan={6} className="text-center text-slate-400 py-6">Nenhum laudo pendente.</td></tr>}
              {data?.map((l) => (
                <tr key={l.request_id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono">{l.number}</td>
                  <td className="px-4 py-2">#{l.patient_id}</td>
                  <td className="px-4 py-2 text-slate-600">{fmtDate(l.received_datetime)}</td>
                  <td className="px-4 py-2">{l.ready_count}/{l.total_count}</td>
                  <td className="px-4 py-2">{l.status}</td>
                  <td className="px-4 py-2 text-right">
                    <Button size="sm"><CheckCircle2 className="w-4 h-4" />Liberar</Button>
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
