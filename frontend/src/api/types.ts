export interface UseCase {
  id: number;
  title: string;
  description: string;
  stakeholders: { name: string; role?: string }[] | null;
  expected_benefit: string | null;
  status: UseCaseStatus;
  company_id: number;
  transcript_id: number | null;
  created_by_id: number | null;
  created_at: string;
  updated_at: string;
}

export type UseCaseStatus =
  | "new"
  | "in_review"
  | "approved"
  | "in_progress"
  | "completed"
  | "archived";

export interface UseCaseListResponse {
  data: UseCase[];
  total: number;
  page: number;
  per_page: number;
}

export interface Company {
  id: number;
  name: string;
  industry_id: number;
}

export interface Industry {
  id: number;
  name: string;
  description: string | null;
}

export interface ChatResponse {
  reply: string;
  session_id: string;
  tool_calls_made: string[];
}
