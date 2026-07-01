"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search, Plus, Clock, FileText, BarChart, Users } from "lucide-react";
import { SHLLogo } from "@/components/ui/logo";
import { useSessions } from "@/contexts/SessionContext";

export default function EnterpriseDashboard() {
  const router = useRouter();
  const { sessions, clearSessions } = useSessions();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Top Navigation */}
      <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <SHLLogo className="h-5 w-auto mr-1" />
            <span className="font-semibold text-sm tracking-tight text-slate-900 border-l border-slate-300 pl-3 ml-1">
              Assessment Advisor
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-4 text-sm font-medium text-slate-600">
            <a href="/" className="text-blue-700 border-b-2 border-blue-700 py-4">Dashboard</a>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative hidden md:block">
            <Search className="absolute left-2.5 top-2 h-4 w-4 text-slate-400" />
            <Input 
              placeholder="Search roles or candidates..." 
              className="h-8 w-64 pl-9 bg-slate-50 border-slate-200 text-xs focus-visible:ring-blue-700 shadow-none"
            />
          </div>
          <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold text-xs border border-blue-200">
            HR
          </div>
        </div>
      </header>

      {/* Main Dashboard Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 flex flex-col gap-8">
        
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Recruiting Workspace</h1>
            <p className="text-sm text-slate-500 mt-1">Manage role profiles and discover recommended assessments.</p>
          </div>
          <Button 
            onClick={() => router.push("/workspace")}
            className="bg-blue-900 hover:bg-blue-800 text-white shadow-none rounded-md h-9 px-4 text-sm font-medium"
          >
            <Plus className="mr-2 h-4 w-4" />
            New Assessment Request
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column: Quick Stats */}
          <div className="md:col-span-1 flex flex-col gap-6">
            <Card className="rounded-md border-slate-200 shadow-sm bg-blue-50/50">
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <div className="bg-blue-100 p-2 rounded text-blue-700">
                    <BarChart className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-blue-900">System Update</h3>
                    <p className="text-xs text-blue-700/80 mt-1 leading-relaxed">
                      The SHL Assessment Catalog has been updated with the latest Graduate Sift modules.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Data Table */}
          <div className="md:col-span-2">
            <Card className="rounded-md border-slate-200 shadow-sm h-full flex flex-col">
              <CardHeader className="pb-0 pt-5 px-5 border-b border-slate-100 mb-2 shrink-0">
                <div className="flex items-center justify-between mb-4">
                  <CardTitle className="text-sm font-medium text-slate-700">Recent Requests</CardTitle>
                  {sessions.length > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm("Are you sure you want to clear your entire request history?")) {
                          clearSessions();
                        }
                      }}
                      className="text-xs h-7 text-slate-500 hover:text-red-600 hover:bg-red-50"
                    >
                      Clear History
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="p-0 flex-1">
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent border-slate-200">
                      <TableHead className="h-9 text-[11px] font-semibold text-slate-500 uppercase tracking-wider pl-5">REQ ID</TableHead>
                      <TableHead className="h-9 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Role</TableHead>
                      <TableHead className="h-9 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Date</TableHead>
                      <TableHead className="h-9 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Status</TableHead>
                      <TableHead className="h-9 text-[11px] font-semibold text-slate-500 uppercase tracking-wider text-right pr-5">Assessments</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sessions.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="py-12 text-center text-sm text-slate-500">
                          No recent requests found. Start a new assessment request to see it here!
                        </TableCell>
                      </TableRow>
                    ) : (
                      sessions.map((session) => (
                        <TableRow 
                          key={session.id} 
                          className="border-slate-100 cursor-pointer hover:bg-slate-50/80 transition-colors"
                          onClick={() => router.push(`/workspace?sessionId=${session.id}`)}
                        >
                          <TableCell className="py-3 pl-5 text-xs font-medium text-blue-700">{session.id}</TableCell>
                          <TableCell className="py-3 text-xs text-slate-700 font-medium">{session.role}</TableCell>
                          <TableCell className="py-3 text-xs text-slate-500">
                            <div className="flex items-center gap-1.5">
                              <Clock className="h-3 w-3" />
                              {session.date}
                            </div>
                          </TableCell>
                          <TableCell className="py-3">
                            <Badge 
                              variant="secondary" 
                              className={`text-[10px] uppercase font-semibold tracking-wider rounded-sm px-1.5 py-0.5 ${
                                session.status === "COMPLETED" 
                                  ? "bg-green-100 text-green-700 hover:bg-green-100" 
                                  : "bg-slate-100 text-slate-600 hover:bg-slate-100"
                              }`}
                            >
                              {session.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="py-3 text-xs text-slate-500 text-right pr-5">{session.assessmentsCount}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
