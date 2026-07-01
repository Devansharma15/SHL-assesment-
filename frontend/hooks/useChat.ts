/* Chat state management hook using useReducer. */
"use client";

import { useReducer, useCallback, useState, useEffect } from "react";
import type { AppState, AppAction, Message, ChatResponse, Recommendation } from "@/types";
import { sendChatMessage } from "@/lib/api";
import { useSessions } from "@/contexts/SessionContext";

const initialState: AppState = {
  messages: [],
  recommendations: [],
  comparedAssessments: [],
  isComparing: false,
  isLoading: false,
  error: null,
  endOfConversation: false,
  selectedAssessment: null,
  isModalOpen: false,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "ADD_USER_MESSAGE":
      return {
        ...state,
        messages: [
          ...state.messages,
          { role: "user" as const, content: action.payload },
        ],
        error: null,
      };

    case "ADD_ASSISTANT_RESPONSE":
      return {
        ...state,
        messages: [
          ...state.messages,
          { role: "assistant" as const, content: action.payload.reply },
        ],
        recommendations:
          action.payload.recommendations.length > 0
            ? action.payload.recommendations
            : state.recommendations,
        endOfConversation: action.payload.end_of_conversation,
        isLoading: false,
      };

    case "SET_LOADING":
      return { ...state, isLoading: action.payload };

    case "SET_ERROR":
      return { ...state, error: action.payload, isLoading: false };

    case "TOGGLE_COMPARE": {
      const exists = state.comparedAssessments.some(
        (a) => a.name === action.payload.name
      );
      const updated = exists
        ? state.comparedAssessments.filter(
          (a) => a.name !== action.payload.name
        )
        : [...state.comparedAssessments, action.payload];
      return {
        ...state,
        comparedAssessments: updated,
        isComparing: updated.length >= 2,
      };
    }

    case "CLEAR_COMPARISON":
      return { ...state, comparedAssessments: [], isComparing: false };

    case "OPEN_MODAL":
      return {
        ...state,
        selectedAssessment: action.payload,
        isModalOpen: true,
      };

    case "CLOSE_MODAL":
      return { ...state, selectedAssessment: null, isModalOpen: false };

    case "RESET_CONVERSATION":
      return { ...initialState };

    case "LOAD_SESSION":
      return {
        ...initialState,
        messages: action.payload.messages,
        recommendations: action.payload.recommendations,
      };

    default:
      return state;
  }
}

export function useChat(initialSessionId?: string | null) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
  const { sessions, createSession, updateSession } = useSessions();
  const [hasLoaded, setHasLoaded] = useState(false);

  // Load session data if provided
  useEffect(() => {
    if (initialSessionId && sessions.length > 0 && !hasLoaded) {
      const session = sessions.find((s) => s.id === initialSessionId);
      if (session) {
        dispatch({
          type: "LOAD_SESSION",
          payload: {
            messages: session.messages || [],
            recommendations: session.recommendations || [],
          },
        });
        setSessionId(session.id);
        setHasLoaded(true);
      }
    }
  }, [initialSessionId, sessions, hasLoaded]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || state.isLoading) return;

      let currentSessionId = sessionId;
      if (!currentSessionId && !content.startsWith("(System:")) {
        // Extract a short role description for the session title
        const role = content.substring(0, 35) + (content.length > 35 ? "..." : "");
        const newSession = createSession(role);
        setSessionId(newSession.id);
        currentSessionId = newSession.id;
      }

      dispatch({ type: "ADD_USER_MESSAGE", payload: content });
      dispatch({ type: "SET_LOADING", payload: true });

      const messages: Message[] = [
        ...state.messages,
        { role: "user" as const, content },
      ];

      // Sync user message immediately
      if (currentSessionId) {
        updateSession(currentSessionId, { messages });
      }

      try {
        const response = await sendChatMessage({ messages });
        dispatch({ type: "ADD_ASSISTANT_RESPONSE", payload: response });

        if (currentSessionId) {
          updateSession(currentSessionId, {
            status: response.recommendations.length > 0 ? "COMPLETED" : "DRAFT",
            assessmentsCount: response.recommendations.length,
            messages: [
              ...messages,
              { role: "assistant" as const, content: response.reply },
            ],
            recommendations: response.recommendations.length > 0 ? response.recommendations : state.recommendations,
          });
        }
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "Something went wrong. Please try again.";
        dispatch({ type: "SET_ERROR", payload: message });
      }
    },
    [state.messages, state.isLoading, state.recommendations, sessionId, createSession, updateSession]
  );

  const resetConversation = useCallback(() => {
    dispatch({ type: "RESET_CONVERSATION" });
    setSessionId(null);
    setHasLoaded(false);
  }, []);

  const toggleCompare = useCallback((assessment: Recommendation) => {
    dispatch({ type: "TOGGLE_COMPARE", payload: assessment });
  }, []);

  const clearComparison = useCallback(() => {
    dispatch({ type: "CLEAR_COMPARISON" });
  }, []);

  const openModal = useCallback((assessment: Recommendation) => {
    dispatch({ type: "OPEN_MODAL", payload: assessment });
  }, []);

  const closeModal = useCallback(() => {
    dispatch({ type: "CLOSE_MODAL" });
  }, []);

  return {
    ...state,
    sendMessage,
    resetConversation,
    toggleCompare,
    clearComparison,
    openModal,
    closeModal,
  };
}
