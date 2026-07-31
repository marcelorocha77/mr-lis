"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard, Users, Stethoscope, ClipboardList, TestTube2,
  FileText, Activity, ShieldAlert, ListChecks, Radio, LogOut,
  CalendarClock, HandCoins, Cpu, MessageSquare,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { clearTokens } from "@/lib/api";

type NavItem = { href: string; label: string; icon: React.ComponentType<{ className?: string }> };
type NavGroup = { title: string; items: NavItem[] };

const groups: NavGroup[] = [
  {
    title: "Operação",
    items: [
      { href: "/dashboard", label: "Painel geral", icon: LayoutDashboard },
      { href: "/mrlab/pacientes", label: "Pacientes", icon: Users },
      { href: "/mrlab/requisicoes", label: "Requisições", icon: ClipboardList },
      { href: "/mrlab/coleta", label: "Coleta", icon: TestTube2 },
      { href: "/mrlab/agenda", label: "Agenda", icon: CalendarClock },
    ],
  },
  {
    title: "Análises",
    items: [
      { href: "/mrpooling", label: "Worklist (setor)", icon: ListChecks },
      { href: "/mrlablaudo", label: "Laudos", icon: FileText },
    ],
  },
  {
    title: "Controle de qualidade",
    items: [
      { href: "/mrquality", label: "Painel QC", icon: Activity },
      { href: "/mrquality/dosagens", label: "Lançar dosagem", icon: ClipboardList },
      { href: "/mrquality/levey-jennings", label: "Levey-Jennings", icon: Activity },
      { href: "/mrquality/sigma", label: "Sigma-Westgard", icon: Activity },
      { href: "/mrquality/violacoes", label: "Violações", icon: ShieldAlert },
      { href: "/mrquality/analitos", label: "QC-Analitos", icon: TestTube2 },
      { href: "/mrquality/lotes", label: "Lotes QC", icon: TestTube2 },
    ],
  },
  {
    title: "Integração",
    items: [
      { href: "/mrinterface/equipamentos", label: "Equipamentos", icon: Cpu },
      { href: "/mrinterface/mensagens", label: "Mensagens", icon: MessageSquare },
      { href: "/mrinterface", label: "Endpoints", icon: Radio },
      { href: "/mrguardian", label: "Monitoramento", icon: ShieldAlert },
    ],
  },
  {
    title: "Cadastros",
    items: [
      { href: "/mrlab/medicos", label: "Médicos solicitantes", icon: Stethoscope },
      { href: "/mrlab/convenios", label: "Convênios", icon: HandCoins },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearTokens();
    router.push("/login");
  }

  return (
    <aside className="w-64 shrink-0 bg-slate-900 text-slate-200 flex flex-col">
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="text-2xl font-black tracking-tight text-white">MR LIS</div>
        <div className="text-xs text-slate-400 mt-0.5">Sistema unificado de laboratório</div>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 space-y-6">
        {groups.map((group) => (
          <div key={group.title}>
            <div className="px-5 mb-2 text-xs uppercase tracking-wider text-slate-500 font-semibold">
              {group.title}
            </div>
            <ul>
              {group.items.map((item) => {
                const active = pathname === item.href || pathname.startsWith(item.href + "/");
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-5 py-2 text-sm hover:bg-slate-800 transition-colors",
                        active && "bg-brand-600 text-white hover:bg-brand-600"
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-slate-800">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded"
        >
          <LogOut className="w-4 h-4" />
          Sair
        </button>
      </div>
    </aside>
  );
}
