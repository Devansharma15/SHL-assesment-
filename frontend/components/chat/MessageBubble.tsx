"use client";

import type { Message } from "@/types";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`h-7 w-7 rounded-sm flex items-center justify-center text-[10px] font-bold shrink-0 ${
          isUser
            ? "bg-slate-200 text-slate-600 border border-slate-300"
            : "bg-blue-900 text-white border border-blue-950"
        }`}
      >
        {isUser ? "HR" : "SHL"}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[85%] px-4 py-3 text-[13px] leading-relaxed break-words overflow-x-auto ${
          isUser
            ? "bg-slate-100 text-slate-800 rounded-md border border-slate-200/60"
            : "bg-white border border-slate-200 text-slate-800 rounded-md shadow-sm"
        }`}
      >
        {/* Render message with line breaks */}
        {message.content.split("\n").map((line, i) => (
          <span key={i}>
            {line}
            {i < message.content.split("\n").length - 1 && <br />}
          </span>
        ))}
      </div>
    </div>
  );
}
