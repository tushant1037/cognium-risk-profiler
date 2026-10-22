import type {
  AssessmentPreview,
  AssessmentRecord,
  NaturalLanguageResponse,
  QuestionnaireSubmission,
  RecordVerification,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(
      "Could not reach the Cognium API. Check that the backend is running and try again.",
    );
  }

  if (!response.ok) {
    let message = `The request failed (${response.status}).`;
    try {
      const body: unknown = await response.json();
      if (
        typeof body === "object" &&
        body !== null &&
        "detail" in body &&
        typeof body.detail === "string"
      ) {
        message = body.detail;
      }
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function previewAssessment(
  submission: QuestionnaireSubmission,
): Promise<AssessmentPreview> {
  return request("/api/v1/assess/preview", {
    method: "POST",
    body: JSON.stringify(submission),
  });
}

export function createAssessment(
  submission: QuestionnaireSubmission,
): Promise<AssessmentRecord> {
  return request("/api/v1/assess", {
    method: "POST",
    body: JSON.stringify(submission),
  });
}

export function listRecords(): Promise<AssessmentRecord[]> {
  return request("/api/v1/records?limit=25");
}

export function getRecord(recordId: string): Promise<RecordVerification> {
  return request(`/api/v1/records/${encodeURIComponent(recordId)}`);
}

export function getNaturalLanguageRecommendation(
  prompt: string,
): Promise<NaturalLanguageResponse> {
  return request("/api/recommend/natural-language", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}
