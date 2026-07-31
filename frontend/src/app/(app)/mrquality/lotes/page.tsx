"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Plus, X } from "lucide-react";

type Lot = { id: number; product_name: string; lot_number: string; level: string; expiry_date: string | null; is_active: boolean };
type Manufacturer = { id: number; name: string };

export default function LotesPage() {
  const qc = useQueryClient();
  const [show, setShow] = useState(false);
  const lots = useQuery({ queryKey: ["qc-lots"], queryFn: () => api<Lot[]>("/mrquality/lotes") });
  const fabs = useQuery({ queryKey: ["qc-fabs"], queryFn: () => api<Manufacturer[]>("/mrquality/fabricantes") });
  const create = useMutation({
    mutationFn: (body: Partial<Lot> & { manufacturer_id?: number | null }) => api("/mrquality/lotes", { method: "POST", json: body }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["qc-lots"] }); setShow(false); },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Lotes de controle</h1>
          <p className="text-sm text-slate-500">Materiais de controle interno cadastrados</p>
        </div>
        <Button onClick={() => setShow(true)}><Plus className="w-4 h-4" />Novo lote</Button>
      </div>

      {show && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Novo lote</CardTitle>
            <button onClick={() => setShow(false)}><X className="w-4 h-4 text-slate-500" /></button>
          </CardHeader>
          <CardBody>
            <form className="grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              create.mutate({
                product_name: fd.get("product_name") as string,
                lot_number: fd.get("lot_number") as string,
                level: fd.get("level") as string,
                expiry_date: (fd.get("expiry_date") as string) || null,
                manufacturer_id: Number(fd.get("manufacturer_id")) || null,
              });
            }}>
              <div className="md:col-span-2"><Label>Produto *</Label><Input name="product_name" required placeholder="Ex: Bio-Rad Multiqual" /></div>
              <div><Label>Lote *</Label><Input name="lot_number" required /></div>
              <div>
                <Label>Nível *</Label>
                <select name="level" required className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option value="QC1">QC1 (baixo)</option>
                  <option value="QC2">QC2 (normal)</option>
                  <option value="QC3">QC3 (alto)</option>
                </select>
              </div>
              <div>
                <Label>Fabricante</Label>
                <select name="manufacturer_id" className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option value="">—</option>
                  {fabs.data?.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
              <div><Label>Validade</Label><Input name="expiry_date" type="date" /></div>
              <div className="md:col-span-4 text-right"><Button type="submit" disabled={create.isPending}>Salvar</Button></div>
            </form>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-2">Produto</th>
                <th className="text-left px-4 py-2">Lote</th>
                <th className="text-left px-4 py-2">Nível</th>
                <th className="text-left px-4 py-2">Validade</th>
                <th className="text-left px-4 py-2">Ativo</th>
              </tr>
            </thead>
            <tbody>
              {lots.data?.length === 0 && <tr><td colSpan={5} className="text-center text-slate-400 py-6">Nenhum lote.</td></tr>}
              {lots.data?.map((l) => (
                <tr key={l.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium">{l.product_name}</td>
                  <td className="px-4 py-2 font-mono">{l.lot_number}</td>
                  <td className="px-4 py-2">{l.level}</td>
                  <td className="px-4 py-2 text-slate-600">{l.expiry_date ?? "—"}</td>
                  <td className="px-4 py-2">{l.is_active ? "✓" : "✗"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
