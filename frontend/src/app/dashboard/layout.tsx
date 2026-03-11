import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-muted/20 overflow-hidden font-sans">
        <Sidebar />
        <SidebarInset className="flex-1 flex flex-col overflow-hidden relative bg-transparent border-0 shadow-none m-0 ml-0 mr-0 peer-data-[variant=inset]:ml-0 peer-data-[variant=inset]:mr-0 peer-data-[variant=inset]:rounded-none">
          <Header />
          {children}
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
