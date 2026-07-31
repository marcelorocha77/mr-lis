"use client";
import { useQuery } from "@tanstack/react-query";
import { api, Page } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

type Insurance = { id: number; code: string; name: string; ans_code: string | null; price_table: string | null; is_active: boolean };

export default function ConveniosPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["convenios"],
    queryFn: () => api<Page<Insurance>>("/mrlab/convenios?page_size=100"),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Convênios / Operadoras</h1>
      <Card>
        <CardHeader><CardTitle>Convênios cadastrados</CardTitle></CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="text-left px-4 py-2">Código</th>
                  <th className="text-left px-4 py-2">Nome</th>
                  <th className="text-left px-4 py-2">Registro ANS</th>
                  <th className="text-left px-4 py-2">Tabela</th>
                  <th className="text-left px-4 py-2">Ativo</th>
                </tr>
              </thead>
              <tbody>
                {isLoading && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Carregando...</td></tr>}
                {data?.items.map((c) => (
                  <tr key={c.id} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-mono">{c.code}</td>
                    <td className="px-4 py-2 font-medium">{c.name}</td>
                    <td className="px-4 py-2 text-slate-600">{c.ans_code ?? "—"}</td>
                    <td className="px-4 py-2 text-slate-600">{c.price_table ?? "—"}</td>
                    <td className="px-4 py-2">{c.is_active ? "✓" : "✗"}</td>
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
