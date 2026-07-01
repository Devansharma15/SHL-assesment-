import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { TooltipProvider } from "@/components/ui/tooltip";
import { CandidateProvider } from "@/contexts/CandidateContext";
import { SessionProvider } from "@/contexts/SessionContext";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SHL Assessment Advisor — AI-Powered Assessment Recommendations",
  description:
    "Find the right SHL assessments for your hiring needs. Our AI advisor helps HR professionals and recruiters discover the best talent evaluation tools.",
  keywords: ["SHL", "assessments", "hiring", "HR", "talent evaluation", "AI", "recommendations"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">
        <SessionProvider>
          <CandidateProvider>
            <TooltipProvider>{children}</TooltipProvider>
          </CandidateProvider>
        </SessionProvider>
      </body>
    </html>
  );
}
