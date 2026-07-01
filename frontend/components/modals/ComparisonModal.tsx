"use client";

import type { Recommendation } from "@/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface ComparisonModalProps {
  assessments: Recommendation[];
  isOpen: boolean;
  onClose: () => void;
  onClear: () => void;
}

export function ComparisonModal({ assessments, isOpen, onClose, onClear }: ComparisonModalProps) {
  // Collect all unique skills across all compared assessments
  const allSkills = Array.from(
    new Set(assessments.flatMap((a) => a.skills_measured || []))
  ).sort();

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-[90vw] lg:max-w-6xl w-full max-h-[90vh] bg-white border border-slate-200 rounded-xl p-0 shadow-2xl overflow-hidden gap-0 flex flex-col">
        <DialogHeader className="px-6 py-4 border-b border-slate-200 bg-slate-50/50">
          <div className="flex items-center justify-between pr-4">
            <DialogTitle className="text-lg font-semibold text-slate-900 leading-tight">
              Assessment Comparison Matrix
            </DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClear}
              className="text-xs text-slate-500 hover:text-slate-800 h-8 px-2 shadow-none"
            >
              Clear Selection
            </Button>
          </div>
        </DialogHeader>

        <div className="overflow-x-auto overflow-y-auto flex-1 p-6">
          <table className="w-full text-left border-collapse text-[13px]">
            <thead>
              <tr className="border-b-2 border-slate-200">
                <th className="py-3 pr-4 font-semibold text-[11px] text-slate-400 uppercase tracking-wider min-w-[160px] whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Feature / Spec
                </th>
                {assessments.map((a) => (
                  <th
                    key={a.name}
                    className="py-3 px-6 font-bold text-slate-900 min-w-[300px] align-bottom"
                  >
                    {a.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {/* Test Type */}
              <tr>
                <td className="py-4 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Assessment Type
                </td>
                {assessments.map((a) => (
                  <td key={a.name} className="py-4 px-6 text-slate-800 font-medium text-[13px]">
                    {a.test_type}
                  </td>
                ))}
              </tr>

              {/* Description */}
              <tr>
                <td className="py-4 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider align-top whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Overview
                </td>
                {assessments.map((a) => (
                  <td
                    key={a.name}
                    className="py-4 px-6 text-slate-600 leading-relaxed text-[13px] align-top"
                  >
                    {a.description || "N/A"}
                  </td>
                ))}
              </tr>

              {/* Duration */}
              <tr>
                <td className="py-4 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider align-top whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Duration
                </td>
                {assessments.map((a) => (
                  <td key={a.name} className="py-4 px-6 text-slate-700 text-[13px]">
                    {a.duration || "Varies"}
                  </td>
                ))}
              </tr>

              {/* Remote Testing */}
              <tr>
                <td className="py-4 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider align-top whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Remote Testing
                </td>
                {assessments.map((a) => (
                  <td key={a.name} className="py-4 px-6 text-slate-700 text-[13px]">
                    {a.remote_testing ? "Supported" : "No"}
                  </td>
                ))}
              </tr>

              {/* Seniority Levels */}
              <tr>
                <td className="py-4 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider align-top whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Seniority Levels
                </td>
                {assessments.map((a) => (
                  <td key={a.name} className="py-4 px-6 text-slate-700 text-[13px]">
                    {a.seniority_levels?.join(", ") || "N/A"}
                  </td>
                ))}
              </tr>

              {/* Job Families */}
              <tr>
                <td className="py-4 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider align-top whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Job Families
                </td>
                {assessments.map((a) => (
                  <td key={a.name} className="py-4 px-6 text-slate-700 text-[13px]">
                    {a.job_families?.join(", ") || "N/A"}
                  </td>
                ))}
              </tr>

              {/* Skills Checklist Matrix header */}
              <tr>
                <td colSpan={assessments.length + 1} className="py-4 bg-slate-50/50">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2">
                    Skills & Competencies Coverage
                  </div>
                </td>
              </tr>

              {/* Skills Checklist Matrix */}
              {allSkills.map((skill) => (
                <tr key={skill} className="hover:bg-slate-50/30">
                  <td className="py-3 pr-4 text-[12px] text-slate-700 font-medium bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9] max-w-[200px] break-words">
                    {skill}
                  </td>
                  {assessments.map((a) => {
                    const hasSkill = a.skills_measured && a.skills_measured.includes(skill);
                    return (
                      <td key={a.name} className="py-3 px-6">
                        {hasSkill ? (
                          <div className="flex items-center gap-1.5 text-blue-700 font-medium">
                            <svg className="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            Covered
                          </div>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}

              {/* External URL */}
              <tr>
                <td className="py-6 pr-4 font-medium text-[11px] text-slate-500 uppercase tracking-wider whitespace-nowrap bg-white sticky left-0 z-10 shadow-[1px_0_0_0_#f1f5f9]">
                  Action
                </td>
                {assessments.map((a) => (
                  <td key={a.name} className="py-6 px-6">
                    <a
                      href={a.url || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-700 hover:text-blue-900 font-medium text-[12px] underline underline-offset-2"
                    >
                      View in SHL Catalog
                    </a>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>

        <div className="px-6 py-3 bg-slate-50/50 border-t border-slate-200 flex items-center justify-end">
          <Button
            variant="outline"
            onClick={onClose}
            className="text-xs h-8 shadow-none border-slate-200 bg-white"
          >
            Close Matrix
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
