"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Radio } from "lucide-react";

type Endpoint = {
  name: string;
  protocol: string;
  direction: string;
  host: string | null;
  port: number | null;
  status: string;
};

const statusColor: Record<string, string> = {
  active: "bg-emerald-100 text-emerald-700",
  paused: "bg-amber-100 text-amber-700",
  error: "bg-red-100 text-red-700",
};

export default function MRInterfacePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["mrinterface-endpoints"],
    queryFn: () => api<Endpoint[]>("/mrinterface/endpoints"),
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Radio className="w-6 h-6 text-brand-600" /> MRInterface
        </h1>
        <p className="text-sm text-slate-500">Integrações com equipamentos e sistemas externos</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Endpoints configurados</CardTitle></CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Nome</th>
                <th className="text-left px-4 py-2">Protocolo</th>
                <th className="text-left px-4 py-2">Direção</th>
                <th className="text-left px-4 py-2">Endereço</th>
                <th className="text-left px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
              {data?.map((e) => (
                <tr key={e.name} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium">{e.name}</td>
                  <td className="px-4 py-2 font-mono">{e.protocol}</td>
                  <td className="px-4 py-2 text-slate-600">{e.direction}</td>
                  <td className="px-4 py-2 text-slate-600">{e.host ? `${e.host}:${e.port}` : "—"}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-1 rounded ${statusColor[e.status]}`}>{e.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>HL7 v2</CardTitle></CardHeader>
          <CardBody className="text-sm text-slate-500">
            Integração bidirecional com analisadores clínicos (Cobas, Sysmex, Architect, DxH). Mensagens ORM/ORU sobre MLLP.
          </CardBody>
        </Card>
        <Card>
          <CardHeader><CardTitle>TISS 4.x</CardTitle></CardHeader>
          <CardBody className="text-sm text-slate-500">
            Envio de guias SP-SADT e lote de faturamento no padrão XML da ANS. Em breve.
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
