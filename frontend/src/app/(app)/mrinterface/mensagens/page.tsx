"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type Msg = {
  id: number;
  at: string;
  equipment_id: number | null;
  direction: string;
  protocol: string;
  message_type: string | null;
  status: string;
  request_number: string | null;
  error: string | null;
  raw?: string;
};

const statusColor: Record<string, string> = {
  ok: "bg-emerald-100 text-emerald-700",
  parse_error: "bg-red-100 text-red-700",
  ack_error: "bg-amber-100 text-amber-700",
  duplicated: "bg-slate-200 text-slate-600",
};

export default function MensagensPage() {
  const [selected, setSelected] = useState<number | null>(null);
  const list = useQuery({
    queryKey: ["messages"],
    queryFn: () => api<Msg[]>("/mrinterface/mensagens?limit=200"),
    refetchInterval: 5_000,
  });
  const detail = useQuery({
    queryKey: ["message", selected],
    queryFn: () => api<Msg>(`/mrinterface/mensagens/${selected}`),
    enabled: selected !== null,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-brand-600" /> Mensagens de integração
        </h1>
        <p className="text-sm text-slate-500">Log de mensagens HL7/ASTM trocadas com os equipamentos</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Últimas mensagens</CardTitle></CardHeader>
          <CardBody className="p-0 max-h-[70vh] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 sticky top-0">
                <tr>
                  <th className="text-left px-3 py-2">Quando</th>
                  <th className="text-left px-3 py-2">Dir</th>
                  <th className="text-left px-3 py-2">Tipo</th>
                  <th className="text-left px-3 py-2">Requisição</th>
                  <th className="text-left px-3 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {list.isLoading && <tr><td colSpan={5} className="text-center py-6 text-slate-400">Carregando...</td></tr>}
                {!list.isLoading && list.data?.length === 0 && (
                  <tr><td colSpan={5} className="text-center py-6 text-slate-400">Nenhuma mensagem.</td></tr>
                )}
                {list.data?.map((m) => (
                  <tr
                    key={m.id}
                    className={`border-t border-slate-100 cursor-pointer hover:bg-slate-50 ${selected === m.id ? "bg-brand-50" : ""}`}
                    onClick={() => setSelected(m.id)}
                  >
                    <td className="px-3 py-2 text-slate-600 text-xs">{fmtDate(m.at)}</td>
                    <td className="px-3 py-2 font-mono text-xs">{m.direction}</td>
                    <td className="px-3 py-2 font-mono text-xs">{m.message_type ?? m.protocol}</td>
                    <td className="px-3 py-2 font-mono text-xs">{m.request_number ?? "—"}</td>
                    <td className="px-3 py-2">
                      <span className={`text-xs px-2 py-1 rounded ${statusColor[m.status] ?? "bg-slate-100"}`}>{m.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Detalhe</CardTitle></CardHeader>
          <CardBody>
            {selected === null && <div className="text-sm text-slate-400">Selecione uma mensagem para ver o conteúdo bruto.</div>}
            {detail.data && (
              <div className="space-y-3 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <div><span className="text-slate-500">Data:</span> {fmtDate(detail.data.at)}</div>
                  <div><span className="text-slate-500">Direção:</span> {detail.data.direction}</div>
                  <div><span className="text-slate-500">Protocolo:</span> {detail.data.protocol}</div>
                  <div><span className="text-slate-500">Tipo:</span> {detail.data.message_type ?? "—"}</div>
                  <div><span className="text-slate-500">Requisição:</span> {detail.data.request_number ?? "—"}</div>
                  <div><span className="text-slate-500">Status:</span> {detail.data.status}</div>
                </div>
                {detail.data.error && (
                  <div className="text-red-600 text-xs bg-red-50 border border-red-200 p-2 rounded">{detail.data.error}</div>
                )}
                <pre className="text-xs bg-slate-900 text-slate-100 p-3 rounded overflow-x-auto whitespace-pre-wrap max-h-[50vh]">
                  {detail.data.raw ?? "(vazio)"}
                </pre>
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
