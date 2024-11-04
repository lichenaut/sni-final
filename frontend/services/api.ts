export function apiFetch(endpoint: string, options?: any) {
  return $fetch(endpoint, {
    baseURL: "http://localhost:8000",
    ...options,
  });
}
