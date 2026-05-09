"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { fetchApi } from "@/lib/api";

const STUDENT_EMAIL_DOMAIN = "@aluno.ifsp.edu.br";

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!form.email.toLowerCase().endsWith(STUDENT_EMAIL_DOMAIN)) {
      setError(`Use um email terminado em ${STUDENT_EMAIL_DOMAIN}.`);
      return;
    }

    setIsLoading(true);
    try {
      await fetchApi("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          role: "Student",
          college_id: 1,
        }),
        skipAuth: true,
      });
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel cadastrar.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="w-full max-w-md rounded-lg border border-stone-200 bg-white p-6 shadow-sm">
        <div className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
            BlaBlaIF
          </p>
          <h1 className="mt-2 text-2xl font-bold text-stone-950">Criar cadastro</h1>
          <p className="mt-1 text-sm text-stone-600">IFSP Campus Votuporanga</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <label className="block">
            <span className="text-sm font-medium text-stone-700">Nome completo</span>
            <input
              className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700"
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-stone-700">Email institucional</span>
            <input
              className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700"
              type="email"
              value={form.email}
              onChange={(event) => updateField("email", event.target.value)}
              placeholder={`seu.nome${STUDENT_EMAIL_DOMAIN}`}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-stone-700">Telefone</span>
            <input
              className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700"
              value={form.phone}
              onChange={(event) => updateField("phone", event.target.value)}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-stone-700">Senha</span>
            <input
              className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700"
              type="password"
              value={form.password}
              onChange={(event) => updateField("password", event.target.value)}
              required
            />
          </label>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-emerald-800 px-4 py-2 font-semibold text-white transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Cadastrando..." : "Criar cadastro"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-stone-600">
          Ja tem conta?{" "}
          <Link href="/login" className="font-semibold text-emerald-800">
            Entrar
          </Link>
        </p>
      </section>
    </main>
  );
}
