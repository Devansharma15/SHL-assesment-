"use client";

import { useCandidates } from "@/contexts/CandidateContext";
import { SHLLogo } from "@/components/ui/logo";
import { Button } from "@/components/ui/button";
import { ArrowLeft, User, FileText, Trash2, Clock } from "lucide-react";
import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function CandidatesPage() {
  const router = useRouter();
  const { candidates, removeCandidate } = useCandidates();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shrink-0">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => router.push("/")}>
            <SHLLogo className="h-5 w-auto mr-1" />
            <span className="font-semibold text-sm tracking-tight text-slate-900 border-l border-slate-300 pl-3 ml-1">
              Candidates
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-4 text-sm font-medium text-slate-600">
            <a href="/" className="hover:text-slate-900 py-4">Dashboard</a>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push("/")} className="text-xs font-medium text-slate-600 hover:text-slate-900">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Scanned Candidates</h1>
            <p className="text-sm text-slate-500 mt-1">Manage parsed candidate resumes from the AI Advisor.</p>
          </div>
        </div>

        <div className="bg-white rounded-md border border-slate-200 shadow-sm overflow-hidden flex-1">
          {candidates.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500">
              <User className="h-10 w-10 text-slate-300 mb-4" />
              <p className="text-sm font-medium text-slate-600">No candidates found.</p>
              <p className="text-xs text-slate-400 mt-1">Drag and drop resumes into the chat workspace to scan them.</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-6"
                onClick={() => router.push("/workspace")}
              >
                Go to Workspace
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-slate-50/90">
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[120px] pl-5">Candidate ID</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[250px]">Name</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[250px]">Role / Source File</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[250px]">Extracted Skills</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[180px]">Scanned On</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[80px] text-right pr-5">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {candidates.map((candidate) => (
                    <TableRow key={candidate.id} className="border-slate-100 hover:bg-slate-50/50">
                      <TableCell className="align-top py-4 pl-5">
                        <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-1 rounded">
                          {candidate.id}
                        </span>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <div className="font-semibold text-sm text-slate-800">{candidate.name}</div>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <div className="text-sm font-medium text-slate-700">{candidate.role}</div>
                        <div className="flex items-center text-xs text-slate-500 mt-1">
                          <FileText className="h-3 w-3 mr-1" />
                          {candidate.sourceFile}
                        </div>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <div className="flex flex-wrap gap-1.5">
                          {candidate.skills.map((skill, i) => (
                            <Badge key={i} variant="secondary" className="text-[10px] bg-indigo-50 text-indigo-700 font-medium px-1.5 py-0.5 rounded-sm whitespace-nowrap">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <div className="flex items-center text-xs text-slate-500">
                          <Clock className="h-3 w-3 mr-1.5" />
                          {new Date(candidate.parsedAt).toLocaleString()}
                        </div>
                      </TableCell>
                      <TableCell className="align-top py-4 text-right pr-5">
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => removeCandidate(candidate.id)}
                          className="h-8 w-8 text-slate-400 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
