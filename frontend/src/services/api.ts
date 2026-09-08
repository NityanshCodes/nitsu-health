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
  nutrition_today: {
    entries: number;
    calories: number;
    protein_g: number;
    carbs_g: number;
    fats_g: number;
    water_ml: number;
  };
  activity_today: {
    entries: number;
    total_steps: number;
    total_active_minutes: number;
  };
  sleep: { last_entry?: { duration_minutes?: number | null; start_time?: string | null } | null };
  active_goals: {
    id: number;
    title: string;
    target_value: number;
    progress_value: number;
    unit: string;
    progress_pct: number;
  }[];
  recent_reports: { id: number; title: string; report_type: string; created_at: string }[];
  unread_notifications: number;
  latest_metrics: {
    metric_type: string;
    value: number;
    unit: string;
    recorded_at: string;
  }[];
}

export interface NutritionTodayResponse {
  user_id: number;
  date: string;
  entries: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  fiber_g: number;
  water_ml: number;
  recommendation: string;
}

export interface WearableStatusResponse {
  configured: boolean;
  config_note?: string | null;
  connections: { provider: string; status: string; last_synced_at?: string | null }[];
}

export interface LatestReportResponse {
  user_id: number;
  title: string;
  report_type?: string;
  status: string;
  summary: string;
  report_data?: Record<string, unknown> | null;
  generated_at?: string | null;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  limit?: number;
  offset?: number;
}

export interface PaginatedParams {
  limit?: number;
  offset?: number;
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

export interface HealthMetricResponse {
  id: number;
  user_id: number;
  metric_type: string;
  value: number;
  unit: string;
  source: string;
  recorded_at: string;
  notes?: string | null;
}

export interface HealthMetricCreatePayload {
  metric_type: string;
  value: number;
  unit: string;
  recorded_at?: string;
  notes?: string | null;
}

export interface ActivityResponse {
  id: number;
  user_id: number;
  activity_type: string;
  steps?: number | null;
  active_minutes?: number | null;
  distance_km?: number | null;
  calories_burned?: number | null;
  source: string;
  recorded_at: string;
  notes?: string | null;
}

export interface ActivityCreatePayload {
  activity_type: string;
  steps?: number | null;
  active_minutes?: number | null;
  distance_km?: number | null;
  calories_burned?: number | null;
  notes?: string | null;
  recorded_at?: string;
}

export interface SleepResponse {
  id: number;
  user_id: number;
  start_time: string;
  end_time: string;
  duration_minutes?: number | null;
  sleep_stages?: Record<string, unknown> | null;
  source: string;
  notes?: string | null;
}

export interface SleepCreatePayload {
  start_time: string;
  end_time: string;
  duration_minutes?: number | null;
  notes?: string | null;
}

export interface GoalResponse {
  id: number;
  user_id: number;
  goal_type: string;
  title: string;
  target_value: number;
  unit: string;
  start_date: string;
  target_date: string;
  progress_value: number;
  status: string;
  completed_at?: string | null;
  notes?: string | null;
}

export interface GoalCreatePayload {
  goal_type: string;
  title: string;
  target_value: number;
  unit: string;
  start_date: string;
  target_date: string;
  progress_value?: number;
  notes?: string | null;
}

export interface MedicalRecordResponse {
  id: number;
  user_id: number;
  category: string;
  title: string;
  description?: string | null;
  file_path?: string | null;
  mime_type?: string | null;
  recorded_at?: string | null;
  notes?: string | null;
}

export interface MedicalRecordCreatePayload {
  category: string;
  title: string;
  description?: string | null;
  notes?: string | null;
}

export interface NotificationResponse {
  id: number;
  user_id: number;
  type: string;
  title: string;
  body?: string | null;
  is_read: boolean;
  created_at: string;
}

export interface ReportListItem {
  id: number;
  title: string;
  report_type: string;
  summary: string;
  status: string;
  generated_at?: string | null;
  created_at: string;
}

export interface InsightResponse {
  id: number;
  type: string;
  title: string;
  body: string;
  confidence?: number | null;
  next_step?: string | null;
  is_read: boolean;
  generated_at: string;
  source_data?: Record<string, unknown> | null;
}

export interface ConversationSummary {
  id: number;
  title?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: { role: string; content: string; created_at: string }[];
}

export interface SubscriptionStatus {
  plan: string;
  status: string;
  provider?: string | null;
  started_at?: string | null;
  expires_at?: string | null;
}

export interface PaymentOrderResponse {
  order_id: string;
  amount: number;
  currency: string;
  provider: string;
  payment_id: number;
  note?: string | null;
}

export interface PaymentRecord {
  id: number;
  amount: number;
  currency: string;
  status: string;
  provider?: string | null;
  provider_order_id?: string | null;
  created_at: string;
}

export interface SearchResult {
  type: string;
  id: number;
  title: string;
  detail?: string | null;
  date?: string | null;
}

export interface HealthProfileResponse {
  id: number;
  height_cm?: number | null;
  weight_kg?: number | null;
  blood_type?: string | null;
  medical_conditions?: string | null;
  allergies?: string | null;
  medications?: string | null;
  lifestyle?: string | null;
  health_notes?: string | null;
}

export interface UpdateHealthProfilePayload {
  height_cm?: number | null;
  weight_kg?: number | null;
  blood_type?: string | null;
  medical_conditions?: string | null;
  allergies?: string | null;
  medications?: string | null;
  lifestyle?: string | null;
  health_notes?: string | null;
}

export interface FamilyHistoryItem {
  id: number;
  category: string;
  relation: string;
  notes?: string | null;
}

export interface FamilyHistoryCreatePayload {
  category: string;
  relation: string;
  notes?: string | null;
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

  async getWearableConnectUrl(): Promise<{ auth_url: string }> {
    const response = await this.client.get<{ auth_url: string }>(
      "/wearables/fitbit/connect",
    );
    return response.data;
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
      await this.client.get<DashboardSummaryResponse>("/dashboard");
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

  // ── Health metrics ────────────────────────────────────────────────

  async getHealthMetrics(
    params: {
      metric_type?: string;
      from?: string;
      to?: string;
    } & PaginatedParams = {},
  ): Promise<ListResponse<HealthMetricResponse>> {
    const response = await this.client.get<ListResponse<HealthMetricResponse>>(
      "/health/metrics",
      { params },
    );
    return response.data;
  }

  async createHealthMetric(
    data: HealthMetricCreatePayload,
  ): Promise<HealthMetricResponse> {
    const response = await this.client.post<HealthMetricResponse>(
      "/health/metrics",
      data,
    );
    return response.data;
  }

  async updateHealthMetric(
    id: number,
    data: Partial<HealthMetricCreatePayload>,
  ): Promise<HealthMetricResponse> {
    const response = await this.client.put<HealthMetricResponse>(
      `/health/metrics/${id}`,
      data,
    );
    return response.data;
  }

  async deleteHealthMetric(id: number): Promise<void> {
    await this.client.delete(`/health/metrics/${id}`);
  }

  // ── Activity ──────────────────────────────────────────────────────

  async getActivity(params: { day?: string } & PaginatedParams = {}): Promise<
    ListResponse<ActivityResponse>
  > {
    const response = await this.client.get<ListResponse<ActivityResponse>>(
      "/activity",
      { params },
    );
    return response.data;
  }

  async getActivityToday(): Promise<Record<string, unknown>> {
    const response = await this.client.get("/activity/today");
    return response.data;
  }

  async createActivityEntry(data: ActivityCreatePayload): Promise<ActivityResponse> {
    const response = await this.client.post<ActivityResponse>("/activity", data);
    return response.data;
  }

  async deleteActivityEntry(id: number): Promise<void> {
    await this.client.delete(`/activity/${id}`);
  }

  // ── Sleep ─────────────────────────────────────────────────────────

  async getSleep(params: { day?: string } & PaginatedParams = {}): Promise<
    ListResponse<SleepResponse>
  > {
    const response = await this.client.get<ListResponse<SleepResponse>>("/sleep", {
      params,
    });
    return response.data;
  }

  async createSleepEntry(data: SleepCreatePayload): Promise<SleepResponse> {
    const response = await this.client.post<SleepResponse>("/sleep", data);
    return response.data;
  }

  async deleteSleepEntry(id: number): Promise<void> {
    await this.client.delete(`/sleep/${id}`);
  }

  // ── Goals ─────────────────────────────────────────────────────────

  async getGoals(
    params: { status?: string } & PaginatedParams = {},
  ): Promise<ListResponse<GoalResponse>> {
    const response = await this.client.get<ListResponse<GoalResponse>>("/goals", {
      params,
    });
    return response.data;
  }

  async createGoal(data: GoalCreatePayload): Promise<GoalResponse> {
    const response = await this.client.post<GoalResponse>("/goals", data);
    return response.data;
  }

  async updateGoalProgress(id: number, progress_value: number): Promise<GoalResponse> {
    const response = await this.client.post<GoalResponse>(`/goals/${id}/progress`, {
      progress_value,
    });
    return response.data;
  }

  async deleteGoal(id: number): Promise<void> {
    await this.client.delete(`/goals/${id}`);
  }

  // ── Medical records ───────────────────────────────────────────────

  async getMedicalRecords(
    params: { category?: string } & PaginatedParams = {},
  ): Promise<ListResponse<MedicalRecordResponse>> {
    const response = await this.client.get<ListResponse<MedicalRecordResponse>>(
      "/medical-records",
      { params },
    );
    return response.data;
  }

  async createMedicalRecord(
    data: MedicalRecordCreatePayload,
  ): Promise<MedicalRecordResponse> {
    const response = await this.client.post<MedicalRecordResponse>(
      "/medical-records",
      data,
    );
    return response.data;
  }

  async deleteMedicalRecord(id: number): Promise<void> {
    await this.client.delete(`/medical-records/${id}`);
  }

  // ── Notifications ─────────────────────────────────────────────────

  async getNotifications(
    params: { unread_only?: boolean } & PaginatedParams = {},
  ): Promise<ListResponse<NotificationResponse>> {
    const response = await this.client.get<ListResponse<NotificationResponse>>(
      "/notifications",
      { params },
    );
    return response.data;
  }

  async markNotificationRead(id: number): Promise<NotificationResponse> {
    const response = await this.client.post<NotificationResponse>(
      `/notifications/${id}/read`,
    );
    return response.data;
  }

  async markAllNotificationsRead(): Promise<{ marked_read: number }> {
    const response = await this.client.post("/notifications/read-all");
    return response.data;
  }

  // ── Reports ───────────────────────────────────────────────────────

  async getReports(params: PaginatedParams = {}): Promise<
    ListResponse<ReportListItem>
  > {
    const response = await this.client.get<ListResponse<ReportListItem>>("/reports", {
      params,
    });
    return response.data;
  }

  async generateReport(): Promise<Record<string, unknown>> {
    const response = await this.client.post("/reports/generate");
    return response.data;
  }

  // ── AI insights / conversations ───────────────────────────────────

  async generateInsights(): Promise<{ generated: number }> {
    const response = await this.client.post("/ai/insights/generate");
    return response.data;
  }

  async getInsights(
    params: { unread_only?: boolean } & PaginatedParams = {},
  ): Promise<ListResponse<InsightResponse>> {
    const response = await this.client.get<ListResponse<InsightResponse>>(
      "/ai/insights",
      { params },
    );
    return response.data;
  }

  async getConversations(params: PaginatedParams = {}): Promise<
    ListResponse<ConversationSummary>
  > {
    const response = await this.client.get<ListResponse<ConversationSummary>>(
      "/ai/conversations",
      { params },
    );
    return response.data;
  }

  async getConversation(id: number): Promise<ConversationDetail> {
    const response = await this.client.get<ConversationDetail>(
      `/ai/conversations/${id}`,
    );
    return response.data;
  }

  // ── Subscription / payments ──────────────────────────────────────

  async getSubscriptionStatus(): Promise<SubscriptionStatus> {
    const response = await this.client.get<SubscriptionStatus>("/subscription/status");
    return response.data;
  }

  async createPaymentOrder(amount: number): Promise<PaymentOrderResponse> {
    const response = await this.client.post<PaymentOrderResponse>(
      "/payments/create-order",
      { amount, currency: "INR" },
    );
    return response.data;
  }

  async getPaymentHistory(): Promise<{ payments: PaymentRecord[] }> {
    const response = await this.client.get("/payments/history");
    return response.data;
  }

  // ── Search ────────────────────────────────────────────────────────

  async search(q: string): Promise<{ query: string; results: SearchResult[]; total: number }> {
    const response = await this.client.get("/search", { params: { q } });
    return response.data;
  }

  async verifyDemoPayment(
    orderId: string,
    signature: string,
  ): Promise<{ status: string; subscription: string }> {
    const response = await this.client.post("/payments/verify", {
      razorpay_order_id: orderId,
      razorpay_payment_id: "demo_payment",
      signature,
    });
    return response.data;
  }

  // ── Profile / health profile ──────────────────────────────────────

  async getProfile(): Promise<HealthProfileResponse> {
    const response = await this.client.get<HealthProfileResponse>("/profile");
    return response.data;
  }

  async updateProfileHealth(data: UpdateHealthProfilePayload): Promise<HealthProfileResponse> {
    const response = await this.client.put<HealthProfileResponse>("/profile", data);
    return response.data;
  }

  async getFamilyHistory(): Promise<FamilyHistoryItem[]> {
    const response = await this.client.get("/profile/family-history");
    return response.data;
  }

  async createFamilyHistory(data: FamilyHistoryCreatePayload): Promise<FamilyHistoryItem> {
    const response = await this.client.post<FamilyHistoryItem>("/profile/family-history", data);
    return response.data;
  }
}

export const apiClient = new APIClient();
