"use client";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { TestTube2, Barcode } from "lucide-react";
import { Input, Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function ColetaPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
        <TestTube2 className="w-6 h-6 text-brand-600" /> Coleta de amostras
      </h1>

      <Card>
        <CardHeader><CardTitle>Ler código de barras</CardTitle></CardHeader>
        <CardBody className="space-y-3">
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <Label>Código da amostra</Label>
              <div className="relative">
                <Barcode className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <Input className="pl-9" placeholder="Escanear ou digitar..." autoFocus />
              </div>
            </div>
            <Button>Registrar coleta</Button>
          </div>
          <p className="text-xs text-slate-500">
            Registre a coleta lendo o código de barras do tubo. O sistema atualiza o status da amostra e da requisição vinculada.
          </p>
        </CardBody>
      </Card>

      <Card>
        <CardHeader><CardTitle>Amostras pendentes</CardTitle></CardHeader>
        <CardBody className="text-sm text-slate-500">Em breve — fila de amostras aguardando coleta.</CardBody>
      </Card>
    </div>
  );
}
