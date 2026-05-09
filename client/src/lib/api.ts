const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export type User = {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: "Student" | "Professor";
  college_id: number;
};

export type UserUpdateInput = {
  name: string;
  email: string;
  phone: string;
};

export type PasswordUpdateInput = {
  current_password: string;
  new_password: string;
};

export type Notification = {
  id: number;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
};

export type RideDirection = "ToCampus" | "FromCampus";
export type RideStatus = "Scheduled" | "InProgress" | "Completed" | "Cancelled";
export type RequestStatus = "Pending" | "Accepted" | "Rejected" | "Cancelled";

export type RideRequest = {
  id: number;
  ride_id: number;
  passenger_id: number;
  pickup_address: string;
  message?: string | null;
  status: RequestStatus;
  passenger?: {
    id: number;
    name: string;
    email: string;
    phone?: string | null;
  } | null;
  ride?: {
    id: number;
    direction: RideDirection;
    origin: string;
    destination: string;
    departure_time: string;
    price_per_seat: string;
    rider_name: string;
  } | null;
  driver_phone?: string | null;
};

export type Ride = {
  id: number;
  rider_id: number;
  direction: RideDirection;
  origin: string;
  destination: string;
  departure_time: string;
  price_per_seat: string;
  available_seats: number;
  accepted_seats: number;
  allow_custom_pickup: boolean;
  fixed_gathering_point?: string | null;
  notes?: string | null;
  status: RideStatus;
  rider_name: string;
  rider_phone?: string | null;
  current_user_request_status?: RequestStatus | null;
  requests: RideRequest[];
};

export type RideCreateInput = {
  direction: RideDirection;
  origin: string;
  destination: string;
  departure_time: string;
  available_seats: number;
  price_per_seat: string;
  allow_custom_pickup: boolean;
  fixed_gathering_point?: string | null;
  notes?: string | null;
};

type ApiOptions = RequestInit & {
  skipAuth?: boolean;
};

export async function fetchApi<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { skipAuth, ...fetchOptions } = options;
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token && !skipAuth) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    let errorMsg = "Nao foi possivel concluir a operacao.";
    try {
      const errorData = await response.json();
      if (Array.isArray(errorData.detail)) {
        errorMsg = errorData.detail[0]?.msg || errorMsg;
      } else {
        errorMsg = errorData.detail || errorMsg;
      }
    } catch {}
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export async function login(email: string, password: string) {
  const params = new URLSearchParams();
  params.append("username", email);
  params.append("password", password);

  return fetchApi<{ access_token: string; token_type: string }>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params,
    skipAuth: true,
  });
}
