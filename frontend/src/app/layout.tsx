import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Sidebar } from "@/components/layout/Sidebar";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Management System",
  description: "Internal fleet management and telemetry dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} antialiased font-sans`}
      >
        <TooltipProvider>
          <AuthProvider>
            <SidebarProvider>
              <Sidebar />
              <SidebarInset className="bg-white">
                <main className="flex-1 overflow-y-auto p-8">{children}</main>
              </SidebarInset>
            </SidebarProvider>
          </AuthProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
