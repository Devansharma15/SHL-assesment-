"use client";

import type { Recommendation } from "@/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { TEST_TYPE_COLORS, TEST_TYPE_ICONS } from "@/lib/constants";

interface AssessmentModalProps {
  assessment: Recommendation;
  isOpen: boolean;
  onClose: () => void;
  onCompare: () => void;
  isCompared: boolean;
}

export function AssessmentModal({
  assessment,
  isOpen,
  onClose,
  onCompare,
  isCompared,
}: AssessmentModalProps) {
  const colorClass =
    TEST_TYPE_COLORS[assessment.test_type] ||
    "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300";
  const icon = TEST_TYPE_ICONS[assessment.test_type] || "📋";

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md md:max-w-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xl">
        <DialogHeader className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{icon}</span>
            <DialogTitle className="text-xl font-bold text-slate-900 dark:text-white leading-tight">
              {assessment.name}
            </DialogTitle>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary" className={`text-xs font-semibold ${colorClass}`}>
              {assessment.test_type}
            </Badge>
          </div>
        </DialogHeader>

        <Separator className="my-4 bg-slate-100 dark:bg-slate-800" />

        <div className="space-y-4 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
          {/* Description */}
          {assessment.description && (
            <div>
              <h4 className="font-semibold text-slate-900 dark:text-white mb-1.5">
                Description
              </h4>
              <p className="text-slate-600 dark:text-slate-300">
                {assessment.description}
              </p>
            </div>
          )}

          {/* Skills Measured */}
          {assessment.skills_measured && assessment.skills_measured.length > 0 && (
            <div>
              <h4 className="font-semibold text-slate-900 dark:text-white mb-1.5">
                Skills Measured
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {assessment.skills_measured.map((skill) => (
                  <span
                    key={skill}
                    className="text-xs px-2.5 py-1 rounded-full bg-slate-50 dark:bg-slate-800/60 border border-slate-200/50 dark:border-slate-800 text-slate-700 dark:text-slate-300 font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Why Recommended */}
          {assessment.why_recommended && (
            <div className="p-3.5 bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30 rounded-xl">
              <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-1.5 flex items-center gap-1.5">
                <span>💡</span> Why Recommended
              </h4>
              <p className="text-xs text-blue-800 dark:text-blue-300 italic leading-relaxed">
                {assessment.why_recommended}
              </p>
            </div>
          )}
        </div>

        <Separator className="my-4 bg-slate-100 dark:bg-slate-800" />

        <div className="flex items-center gap-3">
          <Button
            variant={isCompared ? "default" : "outline"}
            onClick={() => {
              onCompare();
              onClose();
            }}
            className={`flex-1 cursor-pointer ${
              isCompared
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : ""
            }`}
          >
            {isCompared ? "Remove from Comparison" : "Add to Comparison"}
          </Button>
          <a
            href={assessment.url}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              buttonVariants({ variant: "default" }),
              "flex-1 bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 cursor-pointer flex items-center justify-center gap-1.5"
            )}
          >
            View on SHL Website ↗
          </a>
        </div>
      </DialogContent>
    </Dialog>
  );
}
