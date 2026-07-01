"use client";

import type { Recommendation } from "@/types";
import { Button } from "@/components/ui/button";
import { TEST_TYPE_ICONS } from "@/lib/constants";

interface ComparisonTableProps {
  assessments: Recommendation[];
  onClear: () => void;
}

export function ComparisonTable({ assessments, onClear }: ComparisonTableProps) {
  // Collect all unique skills across all compared assessments
  const allSkills = Array.from(
    new Set(assessments.flatMap((a) => a.skills_measured || []))
  ).sort();

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/60 rounded-2xl p-5 shadow-sm space-y-4 overflow-hidden">
      <div className="flex items-center justify-between gap-4">
        <h3 className="font-semibold text-sm text-slate-950 dark:text-white flex items-center gap-2">
          📊 Side-by-Side Comparison
        </h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          className="text-xs text-slate-500 hover:text-slate-850 h-8 cursor-pointer"
        >
          Clear Comparison
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-100 dark:border-slate-800">
              <th className="py-2.5 pr-4 font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider w-[120px]">
                Feature
              </th>
              {assessments.map((a) => (
                <th
                  key={a.name}
                  className="py-2.5 px-4 font-semibold text-slate-900 dark:text-white min-w-[160px]"
                >
                  <div className="flex items-center gap-1.5">
                    <span className="shrink-0">
                      {TEST_TYPE_ICONS[a.test_type] || "📋"}
                    </span>
                    <span className="truncate">{a.name}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {/* Test Type */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400">
                Test Type
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4 text-slate-700 dark:text-slate-300">
                  {a.test_type}
                </td>
              ))}
            </tr>

            {/* Description */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400 align-top">
                Description
              </td>
              {assessments.map((a) => (
                <td
                  key={a.name}
                  className="py-3 px-4 text-slate-600 dark:text-slate-400 leading-relaxed max-w-[200px]"
                >
                  {a.description || "—"}
                </td>
              ))}
            </tr>

            {/* Duration */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400">
                Duration
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4 text-slate-700 dark:text-slate-300">
                  {a.duration || "Varies"}
                </td>
              ))}
            </tr>

            {/* Remote Testing */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400">
                Remote Testing
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4 text-slate-700 dark:text-slate-300">
                  {a.remote_testing ? "Supported" : "No"}
                </td>
              ))}
            </tr>

            {/* Seniority Levels */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400 align-top">
                Seniority Levels
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4 text-slate-700 dark:text-slate-300">
                  {a.seniority_levels?.join(", ") || "N/A"}
                </td>
              ))}
            </tr>

            {/* Job Families */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400 align-top">
                Job Families
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4 text-slate-700 dark:text-slate-300">
                  {a.job_families?.join(", ") || "N/A"}
                </td>
              ))}
            </tr>

            {/* Skills Comparison */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400 align-top">
                Skills Covered
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4 align-top">
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(a.skills_measured || []).map((skill) => (
                      <span
                        key={skill}
                        className="px-1.5 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-800 text-[10px] text-slate-600 dark:text-slate-400 font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </td>
              ))}
            </tr>

            {/* Skills Checklist Matrix */}
            {allSkills.map((skill) => (
              <tr key={skill}>
                <td className="py-2 pr-4 text-[10px] text-slate-400 dark:text-slate-500 font-mono truncate">
                  • {skill}
                </td>
                {assessments.map((a) => {
                  const hasSkill = a.skills_measured && a.skills_measured.includes(skill);
                  return (
                    <td key={a.name} className="py-2 px-4">
                      {hasSkill ? (
                        <span className="text-emerald-500 dark:text-emerald-400 font-bold">
                          ✓ Yes
                        </span>
                      ) : (
                        <span className="text-slate-300 dark:text-slate-700">
                          — No
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}

            {/* External URL */}
            <tr>
              <td className="py-3 pr-4 font-medium text-slate-500 dark:text-slate-400">
                Official Catalog
              </td>
              {assessments.map((a) => (
                <td key={a.name} className="py-3 px-4">
                  <a
                    href={a.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1"
                  >
                    SHL Page ↗
                  </a>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
