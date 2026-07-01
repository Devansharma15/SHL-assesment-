"use client";

import { useEffect, useState } from "react";
import { SHLLogo } from "@/components/ui/logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, ArrowLeft } from "lucide-react";
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

interface Assessment {
  entity_id: string;
  name: string;
  link: string;
  job_levels: string[];
  description: string;
  keys: string[];
}

export default function CatalogPage() {
  const router = useRouter();
  const [catalog, setCatalog] = useState<Assessment[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadCatalog() {
      try {
        const res = await fetch("/api/catalog");
        if (res.ok) {
          const data = await res.json();
          setCatalog(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    loadCatalog();
  }, []);

  const filteredCatalog = catalog.filter(
    (item) =>
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.description?.toLowerCase().includes(search.toLowerCase()) ||
      item.keys?.some((k) => k.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shrink-0">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => router.push("/")}>
            <SHLLogo className="h-5 w-auto mr-1" />
            <span className="font-semibold text-sm tracking-tight text-slate-900 border-l border-slate-300 pl-3 ml-1">
              Assessment Catalog
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
            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Full Assessment Catalog</h1>
            <p className="text-sm text-slate-500 mt-1">Browse and search the complete SHL assessment library.</p>
          </div>
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search by name, category, or description..."
              className="pl-9 h-10 border-slate-200 shadow-sm text-sm focus-visible:ring-blue-700"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="bg-white rounded-md border border-slate-200 shadow-sm overflow-hidden flex-1">
          {isLoading ? (
            <div className="flex items-center justify-center h-64 text-sm font-medium text-slate-500">
              Loading catalog...
            </div>
          ) : (
            <div className="overflow-x-auto max-h-[calc(100vh-240px)]">
              <Table>
                <TableHeader className="sticky top-0 bg-slate-50/90 backdrop-blur-sm shadow-[0_1px_0_rgba(226,232,240,1)] z-10">
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[250px]">Assessment Name</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[350px]">Description</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[200px]">Categories</TableHead>
                    <TableHead className="h-10 text-[11px] font-semibold text-slate-500 uppercase tracking-wider w-[150px]">Job Levels</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCatalog.slice(0, 100).map((item) => (
                    <TableRow key={item.entity_id} className="border-slate-100 hover:bg-slate-50/50">
                      <TableCell className="align-top py-4">
                        <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-blue-700 hover:underline">
                          {item.name}
                        </a>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <p className="text-xs text-slate-600 line-clamp-3" title={item.description}>
                          {item.description || "No description available."}
                        </p>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <div className="flex flex-wrap gap-1.5">
                          {item.keys?.slice(0, 3).map((key, i) => (
                            <Badge key={i} variant="secondary" className="text-[10px] bg-slate-100 text-slate-700 font-medium px-1.5 py-0.5 rounded-sm whitespace-nowrap">
                              {key}
                            </Badge>
                          ))}
                          {(item.keys?.length ?? 0) > 3 && (
                            <Badge variant="secondary" className="text-[10px] bg-slate-100 text-slate-500 font-medium px-1.5 py-0.5 rounded-sm">
                              +{item.keys.length - 3}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="align-top py-4">
                        <div className="text-xs text-slate-500">
                          {item.job_levels?.slice(0, 2).join(", ")}
                          {(item.job_levels?.length ?? 0) > 2 && "..."}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {filteredCatalog.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-12 text-slate-500 text-sm">
                        No assessments found matching "{search}"
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          )}
          {!isLoading && filteredCatalog.length > 100 && (
            <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-xs font-medium text-slate-500 text-center">
              Showing first 100 of {filteredCatalog.length} matching assessments. Please refine your search to see more.
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
