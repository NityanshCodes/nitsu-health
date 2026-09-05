import { apiClient, type LoginPayload, type RegisterPayload } from "./api";

export async function registerUser(payload: RegisterPayload) {
  return apiClient.register(payload);
}

export async function loginUser(payload: LoginPayload) {
  const result = await apiClient.login(payload);
  apiClient.setToken(result.access_token);
  return result;
}

export async function fetchCurrentUser() {
  return apiClient.getMe();
}

export async function logoutUser() {
  return apiClient.logout();
}
