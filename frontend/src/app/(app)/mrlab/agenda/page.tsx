"use client";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { CalendarClock } from "lucide-react";

export default function AgendaPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
        <CalendarClock className="w-6 h-6 text-brand-600" /> Agenda
      </h1>
      <Card>
        <CardHeader><CardTitle>Agendamento de coleta</CardTitle></CardHeader>
        <CardBody className="text-sm text-slate-500">
          Em breve — grade de agendamentos por posto/dia/horário para procedimentos que exigem agendamento (Curva Glicêmica, Teste de Tolerância, Holter, etc.).
        </CardBody>
      </Card>
    </div>
  );
}
