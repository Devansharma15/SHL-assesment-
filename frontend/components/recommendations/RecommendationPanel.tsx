import { ScrollArea } from "@/components/ui/scroll-area";
import { RecommendationCard } from "./RecommendationCard"; // fix cache
import { FileSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AssessmentDetailModal } from "../modals/AssessmentDetailModal";
import { ComparisonModal } from "../modals/ComparisonModal";
import { useState } from "react";

export function RecommendationPanel({ chat }: { chat: any }) {
  const { 
    recommendations, 
    comparedAssessments, 
    selectedAssessment,
    isModalOpen,
    toggleCompare,
    clearComparison,
    openModal,
    closeModal,
    messages
  } = chat;

  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);

  const hasRecommendations = recommendations && recommendations.length > 0;
  const isAssistantLast = messages.length > 0 && messages[messages.length - 1].role === "assistant";

  return (
    <div className="flex flex-col h-full bg-slate-50/50">
      <div className="h-14 border-b border-slate-200 bg-white px-6 flex items-center justify-between shrink-0">
        <h2 className="text-sm font-semibold text-slate-700">Assessment Recommendations</h2>
        {comparedAssessments.length > 0 && (
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-medium text-slate-500">
              {comparedAssessments.length} selected
            </span>
            <Button 
              size="sm" 
              variant="default" 
              className="h-8 text-xs bg-blue-900 hover:bg-blue-800 text-white shadow-none"
              onClick={() => setIsCompareModalOpen(true)} 
              disabled={comparedAssessments.length < 2}
            >
              Compare Matrix
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 text-xs text-slate-500 hover:bg-slate-100"
              onClick={clearComparison}
            >
              Clear
            </Button>
          </div>
        )}
      </div>

      <ScrollArea className="flex-1 min-h-0 p-6">
        {(!hasRecommendations || !isAssistantLast) ? (
          <div className="h-full flex flex-col items-center justify-center text-center py-32">
            <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center mb-4">
              <FileSearch className="h-5 w-5 text-slate-400" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900">No Recommendations Yet</h3>
            <p className="text-xs text-slate-500 max-w-xs mt-2 leading-relaxed">
              Provide details about the role in the chat pane to receive tailored assessment recommendations from the catalog.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {recommendations.map((rec: any) => (
              <RecommendationCard 
                key={rec.name}
                recommendation={rec}
                isCompared={comparedAssessments.some((a: any) => a.name === rec.name)}
                onViewDetails={() => openModal(rec)}
                onToggleCompare={() => toggleCompare(rec)}
              />
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Modals */}
      {selectedAssessment && (
        <AssessmentDetailModal 
          assessment={selectedAssessment}
          isOpen={isModalOpen}
          onClose={closeModal}
          onCompare={() => toggleCompare(selectedAssessment)}
          isCompared={comparedAssessments.some((a: any) => a.name === selectedAssessment.name)}
        />
      )}

      <ComparisonModal 
        assessments={comparedAssessments}
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        onClear={() => {
          clearComparison();
          setIsCompareModalOpen(false);
        }}
      />
    </div>
  );
}
