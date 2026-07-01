"use client";

import type { Recommendation } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface RecommendationCardProps {
  recommendation: Recommendation;
  isCompared: boolean;
  onViewDetails: () => void;
  onToggleCompare: () => void;
}

export function RecommendationCard({
  recommendation,
  isCompared,
  onViewDetails,
  onToggleCompare,
}: RecommendationCardProps) {
  return (
    <Card className="rounded-md border-slate-200 shadow-sm bg-white overflow-hidden flex flex-col h-full">
      <CardContent className="p-0 flex flex-col h-full">
        <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex-1">
          <div className="flex justify-between items-start gap-4 mb-3">
            <h3 className="font-semibold text-sm text-slate-900 leading-tight">
              {recommendation.name}
            </h3>
            <Badge variant="outline" className="text-[10px] font-medium bg-white text-slate-600 shrink-0 whitespace-nowrap">
              {recommendation.test_type}
            </Badge>
          </div>
          
          {recommendation.skills_measured && recommendation.skills_measured.length > 0 && (
            <div className="mb-3">
              <div className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 mb-1.5">Skills Assessed</div>
              <div className="flex flex-wrap gap-1">
                {recommendation.skills_measured.slice(0, 4).map((skill) => (
                  <span
                    key={skill}
                    className="text-[10px] px-2 py-0.5 rounded-sm bg-slate-100 text-slate-600 border border-slate-200"
                  >
                    {skill}
                  </span>
                ))}
                {recommendation.skills_measured.length > 4 && (
                  <span className="text-[10px] text-slate-500 font-medium px-1 py-0.5">
                    +{recommendation.skills_measured.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}

          {recommendation.why_recommended && (
            <div className="mt-3 bg-blue-50/50 border border-blue-100 rounded p-2.5">
              <div className="text-[10px] uppercase font-semibold tracking-wider text-blue-800 mb-1">Recommendation Rationale</div>
              <p className="text-[11px] text-slate-700 leading-relaxed line-clamp-3">
                {recommendation.why_recommended}
              </p>
            </div>
          )}
        </div>
        
        <div className="p-3 bg-white flex items-center gap-2 shrink-0 border-t border-slate-100">
          <Button
            variant="outline"
            size="sm"
            onClick={onViewDetails}
            className="text-xs h-8 flex-1 border-slate-200 shadow-none text-slate-700"
          >
            View Specs
          </Button>
          <Button
            variant={isCompared ? "secondary" : "outline"}
            size="sm"
            onClick={onToggleCompare}
            className={`text-xs h-8 shadow-none ${
              isCompared
                ? "bg-blue-100 text-blue-800 border-transparent hover:bg-blue-200"
                : "border-slate-200 text-slate-700"
            }`}
          >
            {isCompared ? "Selected" : "Compare"}
          </Button>
          {recommendation.url && (
            <a
              href={recommendation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-700 hover:text-blue-900 font-medium px-2 underline underline-offset-2"
            >
              Catalog
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
