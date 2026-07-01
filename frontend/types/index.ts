/* TypeScript types for the SHL Assessment Recommender frontend. */

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface Recommendation {
  name: string;
  url: string;
  test_type: string;
  description?: string;
  skills_measured: string[];
  why_recommended?: string;
  category?: string;
  duration?: string;
  seniority_levels?: string[];
  job_families?: string[];
  remote_testing?: boolean;
}

export interface ChatRequest {
  messages: Message[];
}

export interface ChatResponse {
  reply: string;
  recommendations: Recommendation[];
  end_of_conversation: boolean;
}

export interface HealthResponse {
  status: string;
}

export interface AppState {
  messages: Message[];
  recommendations: Recommendation[];
  comparedAssessments: Recommendation[];
  isComparing: boolean;
  isLoading: boolean;
  error: string | null;
  endOfConversation: boolean;
  selectedAssessment: Recommendation | null;
  isModalOpen: boolean;
}

export type AppAction =
  | { type: "ADD_USER_MESSAGE"; payload: string }
  | { type: "ADD_ASSISTANT_RESPONSE"; payload: ChatResponse }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "TOGGLE_COMPARE"; payload: Recommendation }
  | { type: "CLEAR_COMPARISON" }
  | { type: "OPEN_MODAL"; payload: Recommendation }
  | { type: "CLOSE_MODAL" }
  | { type: "RESET_CONVERSATION" }
  | { type: "LOAD_SESSION"; payload: { messages: Message[], recommendations: Recommendation[] } };
