"use client";

import type { Recommendation } from "@/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface AssessmentDetailModalProps {
  assessment: Recommendation;
  isOpen: boolean;
  onClose: () => void;
  onCompare: () => void;
  isCompared: boolean;
}

export function AssessmentDetailModal({
  assessment,
  isOpen,
  onClose,
  onCompare,
  isCompared,
}: AssessmentDetailModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl bg-white border border-slate-200 rounded-md p-0 shadow-lg overflow-hidden gap-0">
        <DialogHeader className="px-6 py-4 border-b border-slate-200 bg-slate-50/50">
          <div className="flex items-start justify-between pr-4">
            <div>
              <DialogTitle className="text-lg font-semibold text-slate-900 leading-tight mb-1.5">
                {assessment.name}
              </DialogTitle>
              <Badge variant="outline" className="text-[10px] font-medium bg-white text-slate-600 rounded-sm">
                {assessment.test_type}
              </Badge>
            </div>
          </div>
        </DialogHeader>

        <div className="p-6 overflow-y-auto max-h-[60vh]">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2 space-y-6">
              {/* Description */}
              <div>
                <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Assessment Overview
                </h4>
                <p className="text-[13px] text-slate-700 leading-relaxed">
                  {assessment.description || "No description provided."}
                </p>
              </div>

              {/* Skills Measured */}
              <div>
                <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Skills & Attributes Measured
                </h4>
                {assessment.skills_measured && assessment.skills_measured.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {assessment.skills_measured.map((skill) => (
                      <span
                        key={skill}
                        className="text-[11px] px-2.5 py-1 rounded-sm bg-slate-100 border border-slate-200 text-slate-700 font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 italic">No specific skills listed.</p>
                )}
              </div>
            </div>

            <div className="space-y-6">
              {/* Why Recommended */}
              {assessment.why_recommended && (
                <div className="p-4 bg-blue-50/50 border border-blue-100 rounded-md">
                  <h4 className="text-[10px] font-semibold text-blue-800 uppercase tracking-wider mb-2">
                    AI Recommendation Rationale
                  </h4>
                  <p className="text-[12px] text-slate-700 leading-relaxed">
                    {assessment.why_recommended}
                  </p>
                </div>
              )}

              {/* Metadata */}
              <div>
                <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Metadata
                </h4>
                <dl className="space-y-2 text-[12px]">
                  <div className="flex flex-col gap-1 border-b border-slate-100 pb-2">
                    <dt className="text-slate-500">Category</dt>
                    <dd className="font-medium text-slate-900">{assessment.category || "N/A"}</dd>
                  </div>
                  <div className="flex flex-col gap-1 border-b border-slate-100 pb-2">
                    <dt className="text-slate-500">Duration</dt>
                    <dd className="font-medium text-slate-900">{assessment.duration || "Varies"}</dd>
                  </div>
                  <div className="flex flex-col gap-1 border-b border-slate-100 pb-2">
                    <dt className="text-slate-500">Remote Testing</dt>
                    <dd className="font-medium text-slate-900">{assessment.remote_testing ? "Supported" : "No"}</dd>
                  </div>
                  <div className="flex flex-col gap-1 border-b border-slate-100 pb-2">
                    <dt className="text-slate-500">Seniority Levels</dt>
                    <dd className="font-medium text-slate-900">{assessment.seniority_levels?.join(", ") || "N/A"}</dd>
                  </div>
                  <div className="flex flex-col gap-1 border-b border-slate-100 pb-2">
                    <dt className="text-slate-500">Job Families</dt>
                    <dd className="font-medium text-slate-900">{assessment.job_families?.join(", ") || "N/A"}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-slate-50/50 border-t border-slate-200 flex items-center justify-end gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            className="text-xs h-8 shadow-none border-slate-200"
          >
            Close
          </Button>
          <Button
            variant={isCompared ? "secondary" : "outline"}
            onClick={() => {
              onCompare();
            }}
            className={`text-xs h-8 shadow-none ${
              isCompared
                ? "bg-blue-100 text-blue-800 border-transparent hover:bg-blue-200"
                : "border-slate-200"
            }`}
          >
            {isCompared ? "Selected for Comparison" : "Select for Comparison"}
          </Button>
          <a
            href={assessment.url || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-blue-900 text-white shadow-none hover:bg-blue-800 h-8 px-4"
          >
            View in Catalog
          </a>
        </div>
      </DialogContent>
    </Dialog>
  );
}
