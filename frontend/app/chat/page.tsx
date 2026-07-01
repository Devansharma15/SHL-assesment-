"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { APP_NAME, WELCOME_MESSAGE, EXAMPLE_PROMPTS, MAX_TURNS } from "@/lib/constants";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { AssessmentCard } from "@/components/assessment/AssessmentCard";
import { AssessmentModal } from "@/components/assessment/AssessmentModal";
import { ComparisonTable } from "@/components/assessment/ComparisonTable";
import Link from "next/link";

function ChatContent() {
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get("prompt");
  const sentInitial = useRef(false);

  const {
    messages,
    recommendations,
    comparedAssessments,
    isComparing,
    isLoading,
    error,
    endOfConversation,
    selectedAssessment,
    isModalOpen,
    sendMessage,
    resetConversation,
    toggleCompare,
    clearComparison,
    openModal,
    closeModal,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Auto-send initial prompt from URL
  useEffect(() => {
    if (initialPrompt && !sentInitial.current && messages.length === 0) {
      sentInitial.current = true;
      sendMessage(initialPrompt);
    }
  }, [initialPrompt, messages.length, sendMessage]);

  const turnCount = Math.ceil(messages.length / 2);
  const turnsRemaining = MAX_TURNS - turnCount;

  return (
    <div className="flex flex-col h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="border-b border-slate-200/60 dark:border-slate-800/60 bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm z-10 shrink-0">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
              ← Back
            </Link>
            <div className="h-5 w-px bg-slate-200 dark:bg-slate-700" />
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-md bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
                S
              </div>
              <span className="font-semibold text-sm text-slate-900 dark:text-white">
                {APP_NAME}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {turnsRemaining <= 3 && turnsRemaining > 0 && (
              <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">
                {turnsRemaining} turns left
              </span>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={resetConversation}
              className="text-xs h-8 cursor-pointer"
            >
              New Chat
            </Button>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Welcome message when empty */}
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg mb-6">
                S
              </div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                {APP_NAME}
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md text-center mb-8 leading-relaxed">
                {WELCOME_MESSAGE}
              </p>

              {/* Suggestion chips */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                {EXAMPLE_PROMPTS.slice(0, 4).map((example) => (
                  <button
                    key={example.title}
                    onClick={() => sendMessage(example.prompt)}
                    className="text-left p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-blue-700 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all text-sm group cursor-pointer"
                  >
                    <span className="mr-2">{example.icon}</span>
                    <span className="text-slate-600 dark:text-slate-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {example.title}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message list */}
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}

            {/* Assessment cards */}
            {recommendations.length > 0 &&
              messages.length > 0 &&
              messages[messages.length - 1].role === "assistant" && (
                <div className="pl-10">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                    {recommendations.map((rec) => (
                      <AssessmentCard
                        key={rec.name}
                        recommendation={rec}
                        isCompared={comparedAssessments.some(
                          (a) => a.name === rec.name
                        )}
                        onViewDetails={() => openModal(rec)}
                        onToggleCompare={() => toggleCompare(rec)}
                      />
                    ))}
                  </div>
                </div>
              )}

            {/* Comparison table */}
            {isComparing && comparedAssessments.length >= 2 && (
              <div className="pl-10 mt-4">
                <ComparisonTable
                  assessments={comparedAssessments}
                  onClear={clearComparison}
                />
              </div>
            )}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-sm">
                  S
                </div>
                <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/60 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" />
                  </div>
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mx-10 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-700 dark:text-red-300">
                  ⚠️ {error}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const lastUserMsg = [...messages]
                      .reverse()
                      .find((m) => m.role === "user");
                    if (lastUserMsg) sendMessage(lastUserMsg.content);
                  }}
                  className="mt-2 text-xs h-7 cursor-pointer"
                >
                  Retry
                </Button>
              </div>
            )}

            {/* End of conversation */}
            {endOfConversation && (
              <div className="text-center py-6">
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
                  ✅ Conversation complete. Happy hiring!
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetConversation}
                  className="cursor-pointer"
                >
                  Start New Conversation
                </Button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="shrink-0 border-t border-slate-200/60 dark:border-slate-800/60 bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <ChatInput
            onSend={sendMessage}
            isLoading={isLoading}
            disabled={endOfConversation || turnCount >= MAX_TURNS}
          />
        </div>
      </div>

      {/* Assessment Detail Modal */}
      {selectedAssessment && (
        <AssessmentModal
          assessment={selectedAssessment}
          isOpen={isModalOpen}
          onClose={closeModal}
          onCompare={() => toggleCompare(selectedAssessment)}
          isCompared={comparedAssessments.some(
            (a) => a.name === selectedAssessment.name
          )}
        />
      )}
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-screen bg-slate-50 dark:bg-slate-950">
          <div className="animate-pulse text-slate-400">Loading...</div>
        </div>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
