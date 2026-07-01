"use client";

import { useState, useCallback, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { MAX_MESSAGE_LENGTH } from "@/lib/constants";
import { SendHorizontal } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setInput("");
  }, [input, isLoading, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="relative border border-slate-200 rounded-md bg-white focus-within:ring-1 focus-within:ring-blue-800 focus-within:border-blue-800 transition-all shadow-sm">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value.slice(0, MAX_MESSAGE_LENGTH))}
          onKeyDown={handleKeyDown}
          placeholder={
            disabled
              ? "Session completed."
              : "Specify role requirements, seniority, and context..."
          }
          disabled={disabled || isLoading}
          rows={2}
          className="w-full resize-none bg-transparent px-3 py-2.5 text-[13px] text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed min-h-[60px]"
          aria-label="Assessment criteria input"
        />
        <div className="flex items-center justify-between px-3 pb-2 pt-1 border-t border-slate-100 bg-slate-50/50 rounded-b-md">
          <span className="text-[10px] text-slate-400 font-medium">
            {input.length}/{MAX_MESSAGE_LENGTH} characters
          </span>
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || disabled}
            size="sm"
            className="h-7 px-3 bg-blue-900 hover:bg-blue-800 text-white rounded shadow-none text-xs font-medium"
            aria-label="Send criteria"
          >
            Submit Request
            <SendHorizontal className="ml-1.5 h-3 w-3" />
          </Button>
        </div>
      </div>
    </div>
  );
}
