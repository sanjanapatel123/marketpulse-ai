import type { CreateAnalysisInput, CreateAnalysisResponse } from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function createAnalysis(
  input: CreateAnalysisInput,
): Promise<CreateAnalysisResponse> {
  const response = await fetch(`${API_URL}/api/analyses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);

    const detail =
      typeof body?.detail === "string" ? body.detail : body?.detail?.message;

    throw new Error(detail ?? "Unable to start analysis");
  }

  return response.json();
}
