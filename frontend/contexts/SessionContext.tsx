"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

import { Message, Recommendation } from "@/types";

export interface ChatSession {
  id: string;
  role: string;
  date: string;
  status: "DRAFT" | "COMPLETED";
  assessmentsCount: number;
  messages: Message[];
  recommendations: Recommendation[];
}

interface SessionContextType {
  sessions: ChatSession[];
  createSession: (role: string) => ChatSession;
  updateSession: (id: string, updates: Partial<ChatSession>) => void;
  deleteSession: (id: string) => void;
  clearSessions: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("shl_sessions");
    if (saved) {
      try {
        setSessions(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse sessions", e);
      }
    }
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem("shl_sessions", JSON.stringify(sessions));
    }
  }, [sessions, isLoaded]);

  const createSession = (role: string) => {
    const newSession: ChatSession = {
      id: `REQ-${Math.floor(1000 + Math.random() * 9000)}`,
      role,
      date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
      status: "DRAFT",
      assessmentsCount: 0,
      messages: [],
      recommendations: [],
    };
    setSessions((prev) => [newSession, ...prev]);
    return newSession;
  };

  const updateSession = (id: string, updates: Partial<ChatSession>) => {
    setSessions((prev) =>
      prev.map((session) => (session.id === id ? { ...session, ...updates } : session))
    );
  };

  const deleteSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
  };

  const clearSessions = () => {
    setSessions([]);
  };

  return (
    <SessionContext.Provider value={{ sessions, createSession, updateSession, deleteSession, clearSessions }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSessions() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSessions must be used within a SessionProvider");
  }
  return context;
}
