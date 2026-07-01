"use client";

import type { Recommendation } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TEST_TYPE_COLORS, TEST_TYPE_ICONS } from "@/lib/constants";

interface AssessmentCardProps {
  recommendation: Recommendation;
  isCompared: boolean;
  onViewDetails: () => void;
  onToggleCompare: () => void;
}

export function AssessmentCard({
  recommendation,
  isCompared,
  onViewDetails,
  onToggleCompare,
}: AssessmentCardProps) {
  const colorClass =
    TEST_TYPE_COLORS[recommendation.test_type] ||
    "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300";
  const icon = TEST_TYPE_ICONS[recommendation.test_type] || "📋";

  return (
    <Card className="group border-slate-200/60 dark:border-slate-800/60 hover:border-blue-300 dark:hover:border-blue-700 transition-all duration-200 hover:shadow-md bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm overflow-hidden">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-lg shrink-0">{icon}</span>
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white truncate">
              {recommendation.name}
            </h3>
          </div>
        </div>

        {/* Test Type Badge */}
        <Badge
          variant="secondary"
          className={`text-[10px] font-medium mb-2 ${colorClass}`}
        >
          {recommendation.test_type}
        </Badge>

        {/* Description */}
        {recommendation.description && (
          <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mb-2 leading-relaxed">
            {recommendation.description}
          </p>
        )}

        {/* Skills */}
        {recommendation.skills_measured && recommendation.skills_measured.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {recommendation.skills_measured.slice(0, 3).map((skill) => (
              <span
                key={skill}
                className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
              >
                {skill}
              </span>
            ))}
            {recommendation.skills_measured.length > 3 && (
              <span className="text-[10px] text-slate-400">
                +{recommendation.skills_measured.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Why recommended */}
        {recommendation.why_recommended && (
          <p className="text-[11px] text-blue-600 dark:text-blue-400 mb-3 italic line-clamp-2">
            💡 {recommendation.why_recommended}
          </p>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onViewDetails}
            className="text-xs h-7 flex-1 cursor-pointer"
          >
            View Details
          </Button>
          <Button
            variant={isCompared ? "default" : "outline"}
            size="sm"
            onClick={onToggleCompare}
            className={`text-xs h-7 cursor-pointer ${
              isCompared
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : ""
            }`}
          >
            {isCompared ? "✓ Compared" : "Compare"}
          </Button>
          <a
            href={recommendation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline shrink-0"
          >
            SHL ↗
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
