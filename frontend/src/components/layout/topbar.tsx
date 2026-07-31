"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Me = { full_name: string; email: string; role: string; tenant_name: string };

export function Topbar() {
  const [me, setMe] = useState<Me | null>(null);
  useEffect(() => {
    api<Me>("/auth/me").then(setMe).catch(() => setMe(null));
  }, []);
  return (
    <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6">
      <div className="text-sm text-slate-500">{me?.tenant_name}</div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-sm font-medium text-slate-800">{me?.full_name}</div>
          <div className="text-xs text-slate-500 capitalize">{me?.role}</div>
        </div>
        <div className="w-9 h-9 rounded-full bg-brand-600 text-white flex items-center justify-center text-sm font-semibold">
          {me?.full_name?.[0] ?? "?"}
        </div>
      </div>
    </header>
  );
}
