import { ChatInput } from "./ChatInput";
import { MessageBubble } from "./MessageBubble";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useEffect, useRef, useState, DragEvent } from "react";
import { useCandidates } from "@/contexts/CandidateContext";
import { FileUp, Loader2 } from "lucide-react";

export function ChatPane({ chat }: { chat: any }) {
  const { messages, isLoading, error, sendMessage, endOfConversation } = chat;
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const { addCandidate } = useCandidates();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (!file) return;

    setIsScanning(true);
    
    // Simulate API delay for parsing
    setTimeout(() => {
      const mockRoles = ["Software Engineer", "Sales Executive", "Product Manager", "Data Analyst"];
      const mockSkillsList = [
        ["React", "TypeScript", "Node.js"],
        ["B2B Sales", "Negotiation", "CRM"],
        ["Agile", "User Research", "Roadmapping"],
        ["Python", "SQL", "Tableau"]
      ];
      const randomIndex = Math.floor(Math.random() * mockRoles.length);
      
      const candidate = addCandidate({
        name: file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " "),
        role: mockRoles[randomIndex],
        skills: mockSkillsList[randomIndex],
        sourceFile: file.name
      });
      
      sendMessage(`(System: Resume "${file.name}" scanned successfully and saved as Candidate ${candidate.id}. Based on the resume, the candidate is a fit for ${candidate.role} roles.)`);
      setIsScanning(false);
    }, 2000);
  };

  return (
    <div 
      className="flex flex-col h-full relative"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag & Drop Overlay */}
      {(isDragging || isScanning) && (
        <div className="absolute inset-0 bg-slate-900/10 backdrop-blur-[2px] z-50 flex items-center justify-center rounded-md border-2 border-dashed border-blue-500 m-2">
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center max-w-sm text-center">
            {isScanning ? (
              <>
                <Loader2 className="h-10 w-10 text-blue-600 animate-spin mb-4" />
                <h3 className="text-lg font-semibold text-slate-900">Scanning Resume</h3>
                <p className="text-sm text-slate-500 mt-2">Extracting skills, experience, and role fit...</p>
              </>
            ) : (
              <>
                <FileUp className="h-10 w-10 text-blue-600 mb-4" />
                <h3 className="text-lg font-semibold text-slate-900">Drop Resume to Scan</h3>
                <p className="text-sm text-slate-500 mt-2">PDF, DOCX, or TXT files supported.</p>
              </>
            )}
          </div>
        </div>
      )}

      <ScrollArea className="flex-1 min-h-0 p-6">
        {messages.length === 0 && !isLoading && (
          <div className="py-4">
            <h2 className="text-sm font-semibold text-slate-900 mb-2">Start an Assessment Request</h2>
            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
              Describe the role you&apos;re hiring for. Be sure to include seniority level, key skills, and industry context.
            </p>
          </div>
        )}

        <div className="flex flex-col gap-6 pb-4">
          {messages.map((msg: any, i: number) => (
            <MessageBubble key={i} message={msg} />
          ))}
          
          {isLoading && (
            <div className="flex gap-3">
              <div className="h-7 w-7 rounded-sm bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-ping" />
              </div>
              <div className="text-xs text-slate-500 py-1.5 font-medium">Processing request...</div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-xs text-red-700 font-medium">Error: {error}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="p-4 border-t border-slate-100 bg-white">
        <ChatInput 
          onSend={sendMessage} 
          isLoading={isLoading} 
          disabled={endOfConversation} 
        />
      </div>
    </div>
  );
}
