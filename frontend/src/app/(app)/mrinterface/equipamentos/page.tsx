"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Cpu, Plus, Power, PowerOff, X } from "lucide-react";
import { fmtDate } from "@/lib/utils";

type Equipment = {
  id: number;
  code: string;
  name: string;
  driver: string;
  protocol: string;
  section: string | null;
  connection: Record<string, unknown>;
  direction: string;
  is_enabled: boolean;
  last_seen: string | null;
  last_error: string | null;
};

type DriverInfo = { code: string; vendor: string; model: string; protocol: string; section: string };

export default function EquipamentosPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  const equipments = useQuery({
    queryKey: ["equipments"],
    queryFn: () => api<Equipment[]>("/mrinterface/equipamentos"),
    refetchInterval: 10_000,
  });
  const drivers = useQuery({
    queryKey: ["drivers"],
    queryFn: () => api<DriverInfo[]>("/mrinterface/drivers"),
  });

  const toggle = useMutation({
    mutationFn: (e: Equipment) =>
      api<Equipment>(`/mrinterface/equipamentos/${e.id}`, {
        method: "PATCH",
        json: { is_enabled: !e.is_enabled },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["equipments"] }),
  });

  const create = useMutation({
    mutationFn: (body: Partial<Equipment>) =>
      api("/mrinterface/equipamentos", { method: "POST", json: body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["equipments"] });
      setShowForm(false);
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-brand-600" /> Equipamentos
          </h1>
          <p className="text-sm text-slate-500">
            Analisadores e equipamentos conectados ao sistema — {drivers.data?.length ?? 0} drivers disponíveis
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}><Plus className="w-4 h-4" />Novo equipamento</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Novo equipamento</CardTitle>
            <button onClick={() => setShowForm(false)}><X className="w-4 h-4 text-slate-500" /></button>
          </CardHeader>
          <CardBody>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const fd = new FormData(e.currentTarget);
                const driverInfo = drivers.data?.find((d) => d.code === (fd.get("driver") as string));
                const connection: Record<string, unknown> = {};
                const host = fd.get("host") as string;
                const port = fd.get("port") as string;
                if (host) connection.host = host;
                if (host) connection.bind = "0.0.0.0";
                if (port) connection.port = Number(port);
                create.mutate({
                  code: fd.get("code") as string,
                  name: fd.get("name") as string,
                  driver: fd.get("driver") as string,
                  protocol: driverInfo?.protocol || "hl7_mllp",
                  section: driverInfo?.section || null,
                  connection,
                });
              }}
              className="grid grid-cols-1 md:grid-cols-6 gap-3"
            >
              <div><Label>Código *</Label><Input name="code" required /></div>
              <div className="md:col-span-3"><Label>Nome *</Label><Input name="name" required /></div>
              <div className="md:col-span-2">
                <Label>Driver *</Label>
                <select name="driver" required className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option value="">Selecione...</option>
                  {drivers.data?.map((d) => (
                    <option key={d.code} value={d.code}>
                      {d.vendor} — {d.model} ({d.protocol})
                    </option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-3"><Label>Host / IP</Label><Input name="host" placeholder="10.0.1.50" /></div>
              <div><Label>Porta</Label><Input name="port" type="number" placeholder="5000" /></div>
              <div className="md:col-span-6 text-right">
                <Button type="submit" disabled={create.isPending}>{create.isPending ? "Salvando..." : "Salvar"}</Button>
              </div>
            </form>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Equipamentos cadastrados</CardTitle></CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Código</th>
                <th className="text-left px-4 py-2">Nome</th>
                <th className="text-left px-4 py-2">Driver</th>
                <th className="text-left px-4 py-2">Protocolo</th>
                <th className="text-left px-4 py-2">Setor</th>
                <th className="text-left px-4 py-2">Última comunicação</th>
                <th className="text-left px-4 py-2">Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {equipments.isLoading && <tr><td colSpan={8} className="text-center py-6 text-slate-400">Carregando...</td></tr>}
              {equipments.data?.length === 0 && <tr><td colSpan={8} className="text-center py-6 text-slate-400">Nenhum equipamento.</td></tr>}
              {equipments.data?.map((eq) => (
                <tr key={eq.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono">{eq.code}</td>
                  <td className="px-4 py-2 font-medium">{eq.name}</td>
                  <td className="px-4 py-2 font-mono text-xs text-slate-600">{eq.driver}</td>
                  <td className="px-4 py-2 text-slate-600">{eq.protocol}</td>
                  <td className="px-4 py-2 text-slate-600">{eq.section ?? "—"}</td>
                  <td className="px-4 py-2 text-slate-600">{eq.last_seen ? fmtDate(eq.last_seen) : "nunca"}</td>
                  <td className="px-4 py-2">
                    {eq.last_error ? (
                      <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-700" title={eq.last_error}>erro</span>
                    ) : eq.is_enabled ? (
                      <span className="text-xs px-2 py-1 rounded bg-emerald-100 text-emerald-700">ativo</span>
                    ) : (
                      <span className="text-xs px-2 py-1 rounded bg-slate-200 text-slate-600">desativado</span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => toggle.mutate(eq)} title={eq.is_enabled ? "Desativar" : "Ativar"}>
                      {eq.is_enabled ? <PowerOff className="w-4 h-4 text-red-500" /> : <Power className="w-4 h-4 text-emerald-500" />}
                    </button>
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
