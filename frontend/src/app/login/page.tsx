"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, saveTokens } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  const router = useRouter();
  const [tenant, setTenant] = useState("demo");
  const [email, setEmail] = useState("admin@demo.mr");
  const [password, setPassword] = useState("mr123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api<{ access_token: string; refresh_token: string }>("/auth/login", {
        method: "POST",
        json: { email, password, tenant_slug: tenant },
      });
      saveTokens(res.access_token, res.refresh_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro no login");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-brand-50 via-white to-brand-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>MR LIS</CardTitle>
              <p className="text-sm text-slate-500 mt-1">Sistema de laboratório clínico</p>
            </div>
            <div className="text-2xl font-black tracking-tight text-brand-600">MR</div>
          </div>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="tenant">Laboratório</Label>
              <Input id="tenant" value={tenant} onChange={(e) => setTenant(e.target.value)} required />
            </div>
            <div>
              <Label htmlFor="email">E-mail</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Entrando..." : "Entrar"}
            </Button>
          </form>
          <p className="mt-6 text-xs text-slate-500 text-center">
            v0.1.0 · MR Informática · 2026
          </p>
        </CardBody>
      </Card>
    </main>
  );
}
