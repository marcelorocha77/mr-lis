"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { ListChecks } from "lucide-react";

type Row = {
  request_item_id: number;
  request_number: string;
  patient_id: number;
  exam_code: string;
  exam_name: string;
  section: string | null;
  status: string;
};

const SECTIONS = ["bioquimica", "hematologia", "hormonios", "imunologia", "urinalise", "parasitologia"];

export default function MRPoolingPage() {
  const [section, setSection] = useState<string>("");
  const { data, isLoading } = useQuery({
    queryKey: ["worklist", section],
    queryFn: () => api<Row[]>(`/mrpooling/worklist${section ? `?section=${section}` : ""}`),
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <ListChecks className="w-6 h-6 text-brand-600" /> MRPooling
        </h1>
        <p className="text-sm text-slate-500">Mapa de trabalho por setor</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setSection("")}
              className={`text-sm px-3 py-1 rounded ${section === "" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"}`}
            >Todos</button>
            {SECTIONS.map((s) => (
              <button
                key={s}
                onClick={() => setSection(s)}
                className={`text-sm px-3 py-1 rounded ${section === s ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"}`}
              >{s}</button>
            ))}
          </div>
        </CardHeader>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Requisição</th>
                <th className="text-left px-4 py-2">Paciente</th>
                <th className="text-left px-4 py-2">Exame</th>
                <th className="text-left px-4 py-2">Setor</th>
                <th className="text-left px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
              {!isLoading && data?.length === 0 && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Nenhum item na worklist.</td></tr>}
              {data?.map((r) => (
                <tr key={r.request_item_id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono">{r.request_number}</td>
                  <td className="px-4 py-2">#{r.patient_id}</td>
                  <td className="px-4 py-2"><span className="font-mono text-slate-500 mr-2">{r.exam_code}</span>{r.exam_name}</td>
                  <td className="px-4 py-2 text-slate-600">{r.section ?? "—"}</td>
                  <td className="px-4 py-2 text-slate-600">{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
