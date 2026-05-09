"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { login } from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await login(email, password);
      localStorage.setItem("token", response.access_token);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel entrar.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="w-full max-w-sm rounded-lg border border-stone-200 bg-white p-6 shadow-sm">
        <div className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
            BlaBlaIF
          </p>
          <h1 className="mt-2 text-2xl font-bold text-stone-950">Entrar</h1>
          <p className="mt-1 text-sm text-stone-600">IFSP Campus Votuporanga</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <label className="block">
            <span className="text-sm font-medium text-stone-700">Email institucional</span>
            <input
              className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-stone-700">Senha</span>
            <input
              className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-emerald-800 px-4 py-2 font-semibold text-white transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-stone-600">
          Ainda nao tem conta?{" "}
          <Link href="/register" className="font-semibold text-emerald-800">
            Criar cadastro
          </Link>
        </p>
      </section>
    </main>
  );
}
