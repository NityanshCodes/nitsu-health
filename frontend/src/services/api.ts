import axios from "axios";
import type { AxiosError, AxiosInstance } from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type ApiErrorShape = {
  detail?: string;
  message?: string;
  error?: string;
};

export class ApiError extends Error {
  status?: number;
  payload?: ApiErrorShape;

  constructor(message: string, status?: number, payload?: ApiErrorShape) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name?: string | null;
  last_name?: string | null;
  phone?: string | null;
  country?: string | null;
  timezone?: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
}

export interface AIChatRequest {
  question: string;
  include_context?: boolean;
}

export interface AIChatResponse {
  answer: string;
  disclaimer: string;
  generated_by: string;
  context_used?: Record<string, unknown> | null;
}

export interface AIHealthResponse {
  status: string;
  provider: string;
  configured: boolean;
}

export interface DashboardSummaryResponse {
  user_id: number;
  status: string;
  summary: string;
  insights: string[];
}

export interface NutritionTodayResponse {
  user_id: number;
  status: string;
  calories: number;
  water_ml: number;
  recommendation: string;
}

export interface WearableStatusResponse {
  user_id: number;
  status: string;
  provider: string;
  message: string;
}

export interface LatestReportResponse {
  user_id: number;
  title: string;
  status: string;
  summary: string;
}

export interface BackendHealthResponse {
  status: string;
  service: string;
}

export interface UpdateProfilePayload {
  first_name?: string | null;
  last_name?: string | null;
  phone?: string | null;
  country?: string | null;
  timezone?: string | null;
}

export interface NutritionCreatePayload {
  meal_type: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  water_ml: number;
  notes?: string | null;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

class APIClient {
  private client: AxiosInstance;
  private readonly tokenKey = "nitsu_auth_token";

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { "Content-Type": "application/json" },
      timeout: 20000,
    });

    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers = config.headers ?? {};
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorShape>) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.dispatchEvent(new CustomEvent("auth:logout"));
        }

        const detail =
          error.response?.data?.detail ??
          error.response?.data?.message ??
          error.message;
        return Promise.reject(
          new ApiError(detail, error.response?.status, error.response?.data),
        );
      },
    );
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  clearToken(): void {
    localStorage.removeItem(this.tokenKey);
  }

  hasToken(): boolean {
    return !!this.getToken();
  }

  async register(data: RegisterPayload): Promise<User> {
    const response = await this.client.post<User>("/auth/register", data);
    return response.data;
  }

  async login(data: LoginPayload): Promise<AuthTokenResponse> {
    const response = await this.client.post<AuthTokenResponse>(
      "/auth/login",
      data,
    );
    return response.data;
  }

  async getMe(): Promise<User> {
    const response = await this.client.get<User>("/users/me");
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post("/auth/logout", {});
    } finally {
      this.clearToken();
    }
  }

  async sendAIQuestion(
    question: string,
    includeContext = true,
  ): Promise<AIChatResponse> {
    const response = await this.client.post<AIChatResponse>("/ai/chat", {
      question,
      include_context: includeContext,
    } satisfies AIChatRequest);
    return response.data;
  }

  async getAIHealth(): Promise<AIHealthResponse> {
    const response = await this.client.get<AIHealthResponse>("/ai/health");
    return response.data;
  }

  async getDashboard(): Promise<DashboardSummaryResponse> {
    const response =
      await this.client.get<DashboardSummaryResponse>("/dashboard/summary");
    return response.data;
  }

  async getNutritionToday(): Promise<NutritionTodayResponse> {
    const response =
      await this.client.get<NutritionTodayResponse>("/nutrition/today");
    return response.data;
  }

  async getWearableStatus(): Promise<WearableStatusResponse> {
    const response =
      await this.client.get<WearableStatusResponse>("/wearables/status");
    return response.data;
  }

  async getLatestReport(): Promise<LatestReportResponse> {
    const response =
      await this.client.get<LatestReportResponse>("/reports/latest");
    return response.data;
  }

  async getBackendHealth(): Promise<BackendHealthResponse> {
    const response = await this.client.get<BackendHealthResponse>("/health");
    return response.data;
  }

  async updateProfile(data: UpdateProfilePayload): Promise<User> {
    const response = await this.client.put<User>("/users/me", data);
    return response.data;
  }

  async createNutritionEntry(
    data: NutritionCreatePayload,
  ): Promise<NutritionCreatePayload> {
    const response = await this.client.post<NutritionCreatePayload>(
      "/nutrition",
      data,
    );
    return response.data;
  }
}

export const apiClient = new APIClient();
