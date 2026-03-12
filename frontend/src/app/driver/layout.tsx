import { AppShell } from "@/components/layout/AppShell";

export default function DriverLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AppShell>
      {children}
    </AppShell>
  );
}
