"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import { ChatPane } from "@/components/chat/ChatPane";
import { RecommendationPanel } from "@/components/recommendations/RecommendationPanel";
import { SHLLogo } from "@/components/ui/logo";

function WorkspaceContent() {
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get("prompt");
  const initialSessionId = searchParams.get("sessionId");
  const sentInitial = useRef(false);

  const chat = useChat(initialSessionId);

  useEffect(() => {
    if (initialPrompt && !sentInitial.current && chat.messages.length === 0 && !initialSessionId) {
      sentInitial.current = true;
      chat.sendMessage(initialPrompt);
    }
  }, [initialPrompt, chat, initialSessionId]);

  return (
    <div className="h-screen flex flex-col bg-slate-50 font-sans text-slate-900 overflow-hidden">
      <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <SHLLogo className="h-5 w-auto mr-1" />
            <span className="font-semibold text-sm tracking-tight border-l border-slate-300 pl-3 ml-1 text-slate-900">
              Assessment Advisor Workspace
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-4 text-sm font-medium text-slate-600">
            <a href="/" className="hover:text-slate-900 py-4">Dashboard</a>
          </nav>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="text-slate-500 font-medium">
            Turns left: {Math.max(0, 5 - Math.ceil(chat.messages.length / 2))}
          </span>
          <button 
            onClick={chat.resetConversation}
            className="text-blue-700 hover:text-blue-800 font-medium px-3 py-1.5 rounded-md hover:bg-blue-50 transition-colors cursor-pointer"
          >
            New Session
          </button>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        <div className="w-full md:w-[45%] lg:w-[40%] border-r border-slate-200 bg-white flex flex-col shadow-[1px_0_10px_rgba(0,0,0,0.02)] z-10">
          <ChatPane chat={chat} />
        </div>
        <div className="hidden md:flex flex-1 flex-col bg-slate-50 overflow-hidden relative">
          <RecommendationPanel chat={chat} />
        </div>
      </main>
    </div>
  );
}

export default function WorkspacePage() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center text-slate-500 text-sm font-medium">Loading workspace...</div>}>
      <WorkspaceContent />
    </Suspense>
  );
}
