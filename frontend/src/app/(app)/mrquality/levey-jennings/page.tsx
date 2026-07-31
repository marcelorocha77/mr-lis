"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart } from "lucide-react";

type Analyte = { id: number };
type Point = { run_id: number; at: string; value: string; z_score: string | null; violations: string[] };
type LJ = {
  analyte_id: number; exam_code: string; lot_number: string; level: string;
  mean: string | null; sd: string | null;
  upper_1s: string | null; lower_1s: string | null;
  upper_2s: string | null; lower_2s: string | null;
  upper_3s: string | null; lower_3s: string | null;
  points: Point[];
  stats: { n: number; mean: number; sd: number; cv: number; min: number; max: number };
};

function LeveyJenningsChart({ data }: { data: LJ }) {
  if (!data.mean || !data.sd || data.points.length === 0) {
    return <div className="text-sm text-slate-400 py-12 text-center">Sem dados suficientes para o gráfico.</div>;
  }
  const mean = parseFloat(data.mean);
  const sd = parseFloat(data.sd);
  const yMin = mean - 4 * sd;
  const yMax = mean + 4 * sd;
  const W = 900;
  const H = 380;
  const padL = 60, padR = 20, padT = 20, padB = 40;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const n = data.points.length;
  const xStep = chartW / Math.max(1, n - 1);

  const yFor = (v: number) => padT + (yMax - v) / (yMax - yMin) * chartH;
  const xFor = (i: number) => padL + i * xStep;

  const line = (v: number) => yFor(v);

  const path = data.points
    .map((p, i) => `${i === 0 ? "M" : "L"}${xFor(i)},${yFor(parseFloat(p.value))}`)
    .join(" ");

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
      {/* faixas SD */}
      <rect x={padL} y={line(mean + sd)} width={chartW} height={line(mean - sd) - line(mean + sd)} fill="#dcfce7" opacity="0.6" />
      <rect x={padL} y={line(mean + 2*sd)} width={chartW} height={line(mean + sd) - line(mean + 2*sd)} fill="#fef9c3" opacity="0.6" />
      <rect x={padL} y={line(mean - sd)} width={chartW} height={line(mean - 2*sd) - line(mean - sd)} fill="#fef9c3" opacity="0.6" />
      <rect x={padL} y={line(mean + 3*sd)} width={chartW} height={line(mean + 2*sd) - line(mean + 3*sd)} fill="#fee2e2" opacity="0.6" />
      <rect x={padL} y={line(mean - 2*sd)} width={chartW} height={line(mean - 3*sd) - line(mean - 2*sd)} fill="#fee2e2" opacity="0.6" />

      {/* linhas de referência */}
      {[3, 2, 1, 0, -1, -2, -3].map((k) => (
        <g key={k}>
          <line x1={padL} y1={line(mean + k * sd)} x2={W - padR} y2={line(mean + k * sd)}
                stroke={k === 0 ? "#059669" : Math.abs(k) === 3 ? "#dc2626" : "#94a3b8"}
                strokeWidth={k === 0 ? 2 : 1}
                strokeDasharray={k === 0 ? "" : "4 4"} />
          <text x={padL - 6} y={line(mean + k * sd) + 3} fontSize={11} textAnchor="end" fill="#475569">
            {k === 0 ? "μ" : (k > 0 ? "+" : "") + k + "SD"}
          </text>
        </g>
      ))}

      {/* série */}
      <path d={path} stroke="#1d6cf5" strokeWidth={1.5} fill="none" />

      {/* pontos */}
      {data.points.map((p, i) => {
        const has3s = p.violations.includes("1_3s") || p.violations.includes("2_2s") || p.violations.includes("R_4s");
        const has2s = p.violations.includes("1_2s");
        const c = has3s ? "#dc2626" : has2s ? "#d97706" : "#1d6cf5";
        return (
          <circle key={p.run_id} cx={xFor(i)} cy={yFor(parseFloat(p.value))} r={4} fill={c} stroke="#fff" strokeWidth={1}>
            <title>{`${p.at}\nvalor: ${p.value}${p.violations.length ? `\nregras: ${p.violations.join(", ")}` : ""}`}</title>
          </circle>
        );
      })}

      {/* eixo x */}
      <line x1={padL} y1={H - padB} x2={W - padR} y2={H - padB} stroke="#cbd5e1" />
      <text x={padL} y={H - 10} fontSize={11} fill="#475569">n={n}</text>
    </svg>
  );
}

export default function LeveyJenningsPage() {
  const analytes = useQuery({ queryKey: ["lj-analytes"], queryFn: () => api<Analyte[]>("/mrquality/analitos") });
  const [id, setId] = useState<number | null>(null);
  const lj = useQuery({
    queryKey: ["lj", id],
    queryFn: () => id ? api<LJ>(`/mrquality/levey-jennings/${id}?limit=60`) : Promise.resolve(null),
    enabled: id !== null,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <LineChart className="w-6 h-6 text-brand-600" /> Gráfico Levey-Jennings
        </h1>
        <p className="text-sm text-slate-500">Série histórica de controles com faixas ±1, ±2, ±3 SD</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-600">QC-Analito:</label>
            <select
              value={id ?? ""}
              onChange={(e) => setId(Number(e.target.value) || null)}
              className="h-9 rounded-md border border-slate-300 px-3 text-sm min-w-64"
            >
              <option value="">Selecione...</option>
              {analytes.data?.map((a) => (<option key={a.id} value={a.id}>QC-analito #{a.id}</option>))}
            </select>
          </div>
        </CardHeader>
        <CardBody>
          {!id && <div className="text-sm text-slate-400 py-12 text-center">Selecione um QC-analito.</div>}
          {lj.data && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-4 text-sm">
                <div><div className="text-xs text-slate-500">Exame</div><div className="font-medium">{lj.data.exam_code}</div></div>
                <div><div className="text-xs text-slate-500">Lote</div><div className="font-mono text-xs">{lj.data.lot_number} ({lj.data.level})</div></div>
                <div><div className="text-xs text-slate-500">Média</div><div className="font-mono">{lj.data.stats.mean.toFixed(4)}</div></div>
                <div><div className="text-xs text-slate-500">SD</div><div className="font-mono">{lj.data.stats.sd.toFixed(4)}</div></div>
                <div><div className="text-xs text-slate-500">CV%</div><div className="font-mono">{lj.data.stats.cv.toFixed(2)}</div></div>
                <div><div className="text-xs text-slate-500">n</div><div className="font-mono">{lj.data.stats.n}</div></div>
              </div>
              <LeveyJenningsChart data={lj.data} />
            </>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
