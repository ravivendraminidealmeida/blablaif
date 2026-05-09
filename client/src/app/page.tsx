"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { fetchApi, Ride, RideCreateInput, RideDirection, RideRequest, User } from "@/lib/api";

const CAMPUS_NAME = "IFSP Campus Votuporanga";

const statusLabels: Record<string, string> = {
  Scheduled: "Agendada",
  Cancelled: "Cancelada",
  Pending: "Pendente",
  Accepted: "Aceita",
  Rejected: "Recusada",
};

const directionLabels: Record<RideDirection, string> = {
  ToCampus: "Indo para o campus",
  FromCampus: "Saindo do campus",
};

type DashboardTab = "available" | "my-rides" | "requests";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatMoney(value: string) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));
}

function whatsappHref(phone: string) {
  const digits = phone.replace(/\D/g, "");
  const normalized = digits.length === 10 || digits.length === 11 ? `55${digits}` : digits;
  return `https://wa.me/${normalized}`;
}

function emptyRideForm(): RideCreateInput {
  return {
    direction: "ToCampus",
    origin: "",
    destination: CAMPUS_NAME,
    departure_time: "",
    available_seats: 3,
    price_per_seat: "0",
    allow_custom_pickup: false,
    fixed_gathering_point: "",
    notes: "",
  };
}

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [availableRides, setAvailableRides] = useState<Ride[]>([]);
  const [myRides, setMyRides] = useState<Ride[]>([]);
  const [myRequests, setMyRequests] = useState<RideRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isRideFormOpen, setIsRideFormOpen] = useState(false);
  const [rideForm, setRideForm] = useState<RideCreateInput>(emptyRideForm);
  const [requestRide, setRequestRide] = useState<Ride | null>(null);
  const [requestForm, setRequestForm] = useState({ pickup_address: "", message: "" });
  const [actionLoading, setActionLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<DashboardTab>("available");

  const scheduledMyRides = useMemo(
    () => myRides.filter((ride) => ride.status === "Scheduled"),
    [myRides],
  );

  const tabs = [
    { id: "available", label: "Caronas disponiveis", count: availableRides.length },
    { id: "my-rides", label: "Minhas caronas", count: scheduledMyRides.length },
    { id: "requests", label: "Minhas solicitacoes", count: myRequests.length },
  ] satisfies { id: DashboardTab; label: string; count: number }[];

  async function loadDashboard() {
    setError("");
    const [me, rides, mine, requests] = await Promise.all([
      fetchApi<User>("/auth/me"),
      fetchApi<Ride[]>("/rides"),
      fetchApi<Ride[]>("/rides/mine"),
      fetchApi<RideRequest[]>("/ride-requests/mine"),
    ]);
    setUser(me);
    setAvailableRides(rides);
    setMyRides(mine);
    setMyRequests(requests);
  }

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    loadDashboard()
      .catch(() => {
        localStorage.removeItem("token");
        router.push("/login");
      })
      .finally(() => setIsLoading(false));
  }, [router]);

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  function updateRideForm(field: keyof RideCreateInput, value: string | number | boolean) {
    setRideForm((current) => {
      const next = { ...current, [field]: value };
      if (field === "direction") {
        const direction = value as RideDirection;
        next.origin = direction === "FromCampus" ? CAMPUS_NAME : "";
        next.destination = direction === "ToCampus" ? CAMPUS_NAME : "";
      }
      return next;
    });
  }

  async function handleCreateRide(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActionLoading(true);
    setError("");

    try {
      await fetchApi<Ride>("/rides", {
        method: "POST",
        body: JSON.stringify({
          ...rideForm,
          departure_time: new Date(rideForm.departure_time).toISOString(),
          fixed_gathering_point: rideForm.allow_custom_pickup ? null : rideForm.fixed_gathering_point,
          notes: rideForm.notes || null,
        }),
      });
      setRideForm(emptyRideForm());
      setIsRideFormOpen(false);
      await loadDashboard();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar a carona.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRequestRide(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!requestRide) return;
    setActionLoading(true);
    setError("");

    try {
      await fetchApi<RideRequest>(`/rides/${requestRide.id}/requests`, {
        method: "POST",
        body: JSON.stringify({
          pickup_address: requestForm.pickup_address,
          message: requestForm.message || null,
        }),
      });
      setRequestRide(null);
      setRequestForm({ pickup_address: "", message: "" });
      await loadDashboard();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel solicitar a vaga.");
    } finally {
      setActionLoading(false);
    }
  }

  async function runAction(action: () => Promise<unknown>) {
    setActionLoading(true);
    setError("");
    try {
      await action();
      await loadDashboard();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel concluir a acao.");
    } finally {
      setActionLoading(false);
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
    <main className="min-h-screen">
      <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
              BlaBlaIF
            </p>
            <h1 className="mt-1 text-2xl font-bold text-stone-950">Painel de caronas</h1>
            <p className="text-sm text-stone-600">{CAMPUS_NAME}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-sm text-stone-600">{user?.name}</span>
            <button
              type="button"
              onClick={() => setIsRideFormOpen(true)}
              className="rounded-md bg-emerald-800 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-900"
            >
              Oferecer carona
            </button>
            <button
              type="button"
              onClick={logout}
              className="rounded-md border border-stone-300 px-4 py-2 text-sm font-semibold text-stone-700 hover:bg-stone-100"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6">
        <nav className="mb-5 flex gap-2 overflow-x-auto border-b border-stone-200" aria-label="Secoes do painel">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex shrink-0 items-center gap-2 border-b-2 px-3 py-3 text-sm font-semibold ${
                  isActive
                    ? "border-emerald-800 text-emerald-900"
                    : "border-transparent text-stone-600 hover:border-stone-300 hover:text-stone-950"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                <span>{tab.label}</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs ${
                    isActive ? "bg-emerald-100 text-emerald-900" : "bg-stone-200 text-stone-700"
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            );
          })}
        </nav>

        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {activeTab === "available" && (
          <section>
            <SectionHeader title="Caronas disponiveis" count={availableRides.length} />
            <div className="grid gap-3">
              {availableRides.length === 0 ? (
                <EmptyState text="Nenhuma carona agendada no momento." />
              ) : (
                availableRides.map((ride) => (
                  <RideCard
                    key={ride.id}
                    ride={ride}
                    currentUserId={user?.id}
                    onRequest={() => {
                      setRequestRide(ride);
                      setRequestForm({
                        pickup_address: ride.allow_custom_pickup ? "" : ride.fixed_gathering_point || "",
                        message: "",
                      });
                    }}
                  />
                ))
              )}
            </div>
          </section>
        )}

        {activeTab === "my-rides" && (
          <section>
            <SectionHeader title="Minhas caronas" count={scheduledMyRides.length} />
            <div className="grid gap-3">
              {myRides.length === 0 ? (
                <EmptyState text="Voce ainda nao ofereceu caronas." />
              ) : (
                myRides.map((ride) => (
                  <MyRideCard
                    key={ride.id}
                    ride={ride}
                    actionLoading={actionLoading}
                    onAccept={(requestId) =>
                      runAction(() => fetchApi(`/ride-requests/${requestId}/accept`, { method: "PATCH" }))
                    }
                    onReject={(requestId) =>
                      runAction(() => fetchApi(`/ride-requests/${requestId}/reject`, { method: "PATCH" }))
                    }
                    onCancel={() =>
                      runAction(() => fetchApi(`/rides/${ride.id}/cancel`, { method: "PATCH" }))
                    }
                  />
                ))
              )}
            </div>
          </section>
        )}

        {activeTab === "requests" && (
          <section>
            <SectionHeader title="Minhas solicitacoes" count={myRequests.length} />
            <div className="grid gap-3">
              {myRequests.length === 0 ? (
                <EmptyState text="Voce ainda nao solicitou vagas." />
              ) : (
                myRequests.map((request) => (
                  <MyRequestCard
                    key={request.id}
                    request={request}
                    actionLoading={actionLoading}
                    onCancel={() =>
                      runAction(() => fetchApi(`/ride-requests/${request.id}/cancel`, { method: "PATCH" }))
                    }
                  />
                ))
              )}
            </div>
          </section>
        )}
      </div>

      {isRideFormOpen && (
        <Modal title="Oferecer carona" onClose={() => setIsRideFormOpen(false)}>
          <form onSubmit={handleCreateRide} className="space-y-4">
            <label className="block">
              <span className="text-sm font-medium text-stone-700">Sentido</span>
              <select
                className="mt-1 w-full rounded-md border border-stone-300 px-3 py-2"
                value={rideForm.direction}
                onChange={(event) => updateRideForm("direction", event.target.value as RideDirection)}
              >
                <option value="ToCampus">Indo para o campus</option>
                <option value="FromCampus">Saindo do campus</option>
              </select>
            </label>

            <TwoColumn>
              <TextField
                label="Origem"
                value={rideForm.origin}
                onChange={(value) => updateRideForm("origin", value)}
                disabled={rideForm.direction === "FromCampus"}
                required
              />
              <TextField
                label="Destino"
                value={rideForm.destination}
                onChange={(value) => updateRideForm("destination", value)}
                disabled={rideForm.direction === "ToCampus"}
                required
              />
            </TwoColumn>

            <TwoColumn>
              <TextField
                label="Data e horario"
                type="datetime-local"
                value={rideForm.departure_time}
                onChange={(value) => updateRideForm("departure_time", value)}
                required
              />
              <TextField
                label="Preco por vaga"
                type="number"
                min="0"
                step="0.01"
                value={rideForm.price_per_seat}
                onChange={(value) => updateRideForm("price_per_seat", value)}
                required
              />
            </TwoColumn>

            <TwoColumn>
              <TextField
                label="Vagas"
                type="number"
                min="1"
                max="8"
                value={String(rideForm.available_seats)}
                onChange={(value) => updateRideForm("available_seats", Number(value))}
                required
              />
              <label className="flex min-h-[66px] items-center gap-3 rounded-md border border-stone-300 px-3 py-2 text-sm text-stone-700">
                <input
                  type="checkbox"
                  checked={rideForm.allow_custom_pickup}
                  onChange={(event) => updateRideForm("allow_custom_pickup", event.target.checked)}
                />
                Aceitar embarque personalizado
              </label>
            </TwoColumn>

            {!rideForm.allow_custom_pickup && (
              <TextField
                label="Ponto de encontro"
                value={rideForm.fixed_gathering_point || ""}
                onChange={(value) => updateRideForm("fixed_gathering_point", value)}
                required
              />
            )}

            <label className="block">
              <span className="text-sm font-medium text-stone-700">Observacoes</span>
              <textarea
                className="mt-1 min-h-20 w-full rounded-md border border-stone-300 px-3 py-2"
                value={rideForm.notes || ""}
                onChange={(event) => updateRideForm("notes", event.target.value)}
              />
            </label>

            <button
              type="submit"
              disabled={actionLoading}
              className="w-full rounded-md bg-emerald-800 px-4 py-2 font-semibold text-white hover:bg-emerald-900 disabled:opacity-60"
            >
              {actionLoading ? "Salvando..." : "Publicar carona"}
            </button>
          </form>
        </Modal>
      )}

      {requestRide && (
        <Modal title="Solicitar vaga" onClose={() => setRequestRide(null)}>
          <form onSubmit={handleRequestRide} className="space-y-4">
            <div className="rounded-md bg-stone-100 px-3 py-2 text-sm text-stone-700">
              {requestRide.origin} {"->"} {requestRide.destination}
            </div>
            <TextField
              label={requestRide.allow_custom_pickup ? "Endereco de embarque" : "Ponto de encontro"}
              value={requestForm.pickup_address}
              onChange={(value) => setRequestForm((current) => ({ ...current, pickup_address: value }))}
              required
            />
            <label className="block">
              <span className="text-sm font-medium text-stone-700">Mensagem</span>
              <textarea
                className="mt-1 min-h-20 w-full rounded-md border border-stone-300 px-3 py-2"
                value={requestForm.message}
                onChange={(event) =>
                  setRequestForm((current) => ({ ...current, message: event.target.value }))
                }
              />
            </label>
            <button
              type="submit"
              disabled={actionLoading}
              className="w-full rounded-md bg-emerald-800 px-4 py-2 font-semibold text-white hover:bg-emerald-900 disabled:opacity-60"
            >
              {actionLoading ? "Enviando..." : "Enviar solicitacao"}
            </button>
          </form>
        </Modal>
      )}
    </main>
  );
}

function SectionHeader({ title, count }: { title: string; count: number }) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-lg font-bold text-stone-950">{title}</h2>
      <span className="rounded-full bg-stone-200 px-2.5 py-1 text-xs font-semibold text-stone-700">
        {count}
      </span>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-dashed border-stone-300 bg-white px-4 py-6 text-sm text-stone-600">
      {text}
    </div>
  );
}

function RideCard({
  ride,
  currentUserId,
  onRequest,
}: {
  ride: Ride;
  currentUserId?: number;
  onRequest: () => void;
}) {
  const seatsLeft = ride.available_seats - ride.accepted_seats;
  const isMine = ride.rider_id === currentUserId;
  const hasActiveRequest = ride.current_user_request_status === "Pending" || ride.current_user_request_status === "Accepted";

  return (
    <article className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
            {directionLabels[ride.direction]}
          </p>
          <h3 className="mt-1 text-lg font-bold text-stone-950">
            {ride.origin} {"->"} {ride.destination}
          </h3>
          <p className="mt-1 text-sm text-stone-600">
            {formatDate(ride.departure_time)} por {ride.rider_name}
          </p>
        </div>
        <div className="text-left md:text-right">
          <p className="font-bold text-stone-950">{formatMoney(ride.price_per_seat)}</p>
          <p className="text-sm text-stone-600">{seatsLeft} vaga(s) livres</p>
        </div>
      </div>

      <div className="mt-3 grid gap-2 text-sm text-stone-700 md:grid-cols-2">
        <p>{ride.allow_custom_pickup ? "Aceita embarque personalizado" : `Ponto: ${ride.fixed_gathering_point}`}</p>
        {ride.notes && <p>{ride.notes}</p>}
        {ride.rider_phone && <PhoneActions label="Motorista" phone={ride.rider_phone} />}
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={onRequest}
          disabled={isMine || seatsLeft <= 0 || hasActiveRequest}
          className="rounded-md bg-emerald-800 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-900 disabled:cursor-not-allowed disabled:bg-stone-300 disabled:text-stone-600"
        >
          {isMine ? "Sua carona" : hasActiveRequest ? statusLabels[ride.current_user_request_status || ""] : "Solicitar vaga"}
        </button>
      </div>
    </article>
  );
}

function MyRideCard({
  ride,
  actionLoading,
  onAccept,
  onReject,
  onCancel,
}: {
  ride: Ride;
  actionLoading: boolean;
  onAccept: (requestId: number) => void;
  onReject: (requestId: number) => void;
  onCancel: () => void;
}) {
  return (
    <article className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-bold text-stone-950">
            {ride.origin} {"->"} {ride.destination}
          </h3>
          <p className="text-sm text-stone-600">{formatDate(ride.departure_time)}</p>
        </div>
        <span className="rounded-full bg-stone-100 px-2.5 py-1 text-xs font-semibold text-stone-700">
          {statusLabels[ride.status]}
        </span>
      </div>

      <div className="mt-3 space-y-2">
        {ride.requests.length === 0 ? (
          <p className="text-sm text-stone-600">Sem solicitacoes ainda.</p>
        ) : (
          ride.requests.map((request) => (
            <div key={request.id} className="rounded-md border border-stone-200 p-3">
              <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                <div className="text-sm text-stone-700">
                  <p className="font-semibold text-stone-950">{request.passenger?.name}</p>
                  <p>Embarque: {request.pickup_address}</p>
                  {request.message && <p>Mensagem: {request.message}</p>}
                  {request.passenger?.phone && <PhoneActions label="Passageiro" phone={request.passenger.phone} />}
                </div>
                <span className="text-xs font-semibold text-stone-600">{statusLabels[request.status]}</span>
              </div>
              {request.status === "Pending" && (
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    disabled={actionLoading}
                    onClick={() => onAccept(request.id)}
                    className="rounded-md bg-emerald-800 px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-60"
                  >
                    Aceitar
                  </button>
                  <button
                    type="button"
                    disabled={actionLoading}
                    onClick={() => onReject(request.id)}
                    className="rounded-md border border-stone-300 px-3 py-1.5 text-sm font-semibold text-stone-700 disabled:opacity-60"
                  >
                    Recusar
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {ride.status === "Scheduled" && (
        <button
          type="button"
          disabled={actionLoading}
          onClick={onCancel}
          className="mt-4 rounded-md border border-red-200 px-3 py-1.5 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:opacity-60"
        >
          Cancelar carona
        </button>
      )}
    </article>
  );
}

function MyRequestCard({
  request,
  actionLoading,
  onCancel,
}: {
  request: RideRequest;
  actionLoading: boolean;
  onCancel: () => void;
}) {
  return (
    <article className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-bold text-stone-950">
            {request.ride?.origin} {"->"} {request.ride?.destination}
          </h3>
          {request.ride && <p className="text-sm text-stone-600">{formatDate(request.ride.departure_time)}</p>}
        </div>
        <span className="rounded-full bg-stone-100 px-2.5 py-1 text-xs font-semibold text-stone-700">
          {statusLabels[request.status]}
        </span>
      </div>
      <p className="mt-2 text-sm text-stone-700">Embarque: {request.pickup_address}</p>
      {request.driver_phone && <PhoneActions label="Motorista" phone={request.driver_phone} />}
      {(request.status === "Pending" || request.status === "Accepted") && (
        <button
          type="button"
          disabled={actionLoading}
          onClick={onCancel}
          className="mt-4 rounded-md border border-red-200 px-3 py-1.5 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:opacity-60"
        >
          Cancelar solicitacao
        </button>
      )}
    </article>
  );
}

function Modal({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950/40 px-4 py-6">
      <section className="max-h-full w-full max-w-2xl overflow-auto rounded-lg bg-white p-5 shadow-xl">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="text-lg font-bold text-stone-950">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-stone-300 px-3 py-1 text-sm font-semibold text-stone-700"
          >
            Fechar
          </button>
        </div>
        {children}
      </section>
    </div>
  );
}

function PhoneActions({ label, phone }: { label: string; phone: string }) {
  const [copyLabel, setCopyLabel] = useState("Copiar");

  async function copyPhone() {
    try {
      await navigator.clipboard.writeText(phone);
      setCopyLabel("Copiado");
      window.setTimeout(() => setCopyLabel("Copiar"), 1800);
    } catch {
      setCopyLabel("Erro");
      window.setTimeout(() => setCopyLabel("Copiar"), 1800);
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2 text-sm text-stone-700">
      <span>
        {label}: <strong className="font-semibold text-stone-950">{phone}</strong>
      </span>
      <button
        type="button"
        onClick={copyPhone}
        className="rounded-md border border-stone-300 px-2.5 py-1 text-xs font-semibold text-stone-700 hover:bg-stone-100"
      >
        {copyLabel}
      </button>
      <a
        href={whatsappHref(phone)}
        target="_blank"
        rel="noreferrer"
        aria-label={`Abrir WhatsApp de ${label}`}
        title={`Abrir WhatsApp de ${label}`}
        className="inline-flex size-8 items-center justify-center rounded-md border border-emerald-200 bg-white hover:bg-emerald-50"
      >
        <Image src="/brands/whatsapp-glyph.svg" alt="" width={20} height={20} />
      </a>
    </div>
  );
}

function TextField({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  disabled = false,
  min,
  max,
  step,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
  disabled?: boolean;
  min?: string;
  max?: string;
  step?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-stone-700">{label}</span>
      <input
        className="mt-1 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-stone-950 outline-none focus:border-emerald-700 disabled:bg-stone-100"
        type={type}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        disabled={disabled}
      />
    </label>
  );
}

function TwoColumn({ children }: { children: ReactNode }) {
  return <div className="grid gap-4 md:grid-cols-2">{children}</div>;
}
