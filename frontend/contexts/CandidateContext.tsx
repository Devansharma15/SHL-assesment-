"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface Candidate {
  id: string;
  name: string;
  role: string;
  skills: string[];
  parsedAt: string;
  sourceFile: string;
}

interface CandidateContextType {
  candidates: Candidate[];
  addCandidate: (candidate: Omit<Candidate, "id" | "parsedAt">) => Candidate;
  removeCandidate: (id: string) => void;
}

const CandidateContext = createContext<CandidateContextType | undefined>(undefined);

export function CandidateProvider({ children }: { children: ReactNode }) {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("shl_candidates");
    if (saved) {
      try {
        setCandidates(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse candidates from local storage", e);
      }
    }
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem("shl_candidates", JSON.stringify(candidates));
    }
  }, [candidates, isLoaded]);

  const addCandidate = (candidateData: Omit<Candidate, "id" | "parsedAt">) => {
    const newCandidate: Candidate = {
      ...candidateData,
      id: `C-${Math.floor(10000 + Math.random() * 90000)}`,
      parsedAt: new Date().toISOString(),
    };
    setCandidates((prev) => [newCandidate, ...prev]);
    return newCandidate;
  };

  const removeCandidate = (id: string) => {
    setCandidates((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <CandidateContext.Provider value={{ candidates, addCandidate, removeCandidate }}>
      {children}
    </CandidateContext.Provider>
  );
}

export function useCandidates() {
  const context = useContext(CandidateContext);
  if (context === undefined) {
    throw new Error("useCandidates must be used within a CandidateProvider");
  }
  return context;
}
