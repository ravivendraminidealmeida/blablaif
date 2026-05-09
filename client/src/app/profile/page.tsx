"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { fetchApi, User, UserUpdateInput } from "@/lib/api";

const STUDENT_EMAIL_DOMAIN = "@aluno.ifsp.edu.br";

export default function Profile() {
  const router = useRouter();
  const [form, setForm] = useState<UserUpdateInput>({
    name: "",
    email: "",
    phone: "",
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetchApi<User>("/auth/me")
      .then((user) => {
        setForm({
          name: user.name,
          email: user.email,
          phone: user.phone,
        });
      })
      .catch(() => {
        localStorage.removeItem("token");
        router.push("/login");
      })
      .finally(() => setIsLoading(false));
  }, [router]);

  function updateField(field: keyof UserUpdateInput, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!form.email.toLowerCase().endsWith(STUDENT_EMAIL_DOMAIN)) {
      setError(`Use um email terminado em ${STUDENT_EMAIL_DOMAIN}.`);
      return;
    }

    setIsSaving(true);
    try {
      const user = await fetchApi<User>("/auth/me", {
        method: "PATCH",
        body: JSON.stringify(form),
      });
      setForm({
        name: user.name,
        email: user.email,
        phone: user.phone,
      });
      setSuccess("Perfil atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel atualizar o perfil.");
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm font-medium text-stone-600">Carregando...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-4 py-10">
      <section className="mx-auto w-full max-w-xl rounded-lg border border-stone-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
              BlaBlaIF
            </p>
            <h1 className="mt-2 text-2xl font-bold text-stone-950">Meu perfil</h1>
            <p className="mt-1 text-sm text-stone-600">Atualize seus dados de contato.</p>
          </div>
          <Link
            href="/"
            className="rounded-md border border-stone-300 px-4 py-2 text-center text-sm font-semibold text-stone-700 hover:bg-stone-100"
          >
            Voltar
          </Link>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
          {success && (
            <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
              {success}
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

          <button
            type="submit"
            disabled={isSaving}
            className="w-full rounded-md bg-emerald-800 px-4 py-2 font-semibold text-white transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSaving ? "Salvando..." : "Salvar perfil"}
          </button>
        </form>
      </section>
    </main>
  );
}
