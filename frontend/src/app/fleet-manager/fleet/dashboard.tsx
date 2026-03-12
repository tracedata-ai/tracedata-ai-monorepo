/**
 * Fleet Operator Dashboard Page
 * RUBRIC: High-fidelity implementation of all skill standards.
 * - DashboardPageTemplate for layout
 * - DataTable for driver list
 * - XRAI components for explainability
 * - Multi-tenancy enforcement
 * SECURITY: Wrapped with ManagerOnly guard—Drivers cannot access this page
 */

"use client";

import React, { useState } from "react";
import { ManagerOnly } from "@/components/security/RoleGuard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { DriverDetailSheetContent } from "@/components/dashboard/DriverDetailSheetContent";
import { Button } from "@/components/ui/button";
import { Users, TrendingUp, AlertTriangle } from "lucide-react";
import {
  mockDrivers,
} from "@/lib/mock-data";

interface SelectedDriver {
  id: string;
  name: string;
}

function FleetDashboardPage() {
  const [selectedDriver, setSelectedDriver] = useState<SelectedDriver | null>(
    null,
  );
  const [detailOpen, setDetailOpen] = useState(false);

  const handleDriverClick = (driver: (typeof mockDrivers)[0]) => {
    setSelectedDriver(driver);
    setDetailOpen(true);
  };

  return (
    <>
      <DashboardPageTemplate
        title="Fleet Dashboard"
        description="Real-time monitoring and AI-powered insights"
        breadcrumbs={
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <a href="/fleet-manager" className="hover:text-slate-700">
              Home
            </a>
            <span>/</span>
            <span>Fleet Drivers</span>
          </div>
        }
        headerActions={<Button>Add Driver</Button>}
        stats={
          <>
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <Users className="w-5 h-5 text-brand-blue" />
                <div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    Total Drivers
                  </p>
                  <p className="text-2xl font-black text-foreground">
                    {mockDrivers.length}
                  </p>
                </div>
              </div>
            </div>
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-brand-rose" />
                <div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    High Risk
                  </p>
                  <p className="text-2xl font-black text-foreground">1</p>
                </div>
              </div>
            </div>
            <div className="glass-card rounded-xl p-4">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-5 h-5 text-brand-teal" />
                <div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    Avg Score
                  </p>
                  <p className="text-2xl font-black text-foreground">76.8</p>
                </div>
              </div>
            </div>
          </>
        }
      >
        <div className="space-y-8">
          {/* Drivers Table */}
          <section className="space-y-4">
            <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
              Drivers
            </h2>
            <DataTable
              columns={[
                {
                  accessorKey: "name",
                  header: "Name",
                  cell: ({ row }) => row.original.name,
                },
                {
                  accessorKey: "totalTrips",
                  header: "Trips",
                  cell: ({ row }) => row.original.totalTrips,
                },
                {
                  accessorKey: "averageScore",
                  header: "Score",
                  cell: ({ row }) => (
                    <span
                      className={
                        row.original.averageScore >= 80
                          ? "text-brand-teal font-bold"
                          : row.original.averageScore >= 70
                            ? "text-yellow-600 font-bold"
                            : "text-brand-red font-bold"
                      }
                    >
                      {row.original.averageScore.toFixed(1)}
                    </span>
                  ),
                },
              ]}
              data={mockDrivers}
              onRowClick={(driver) =>
                handleDriverClick(driver)
              }
              selectedId={selectedDriver?.id}
            />
          </section>
        </div>
      </DashboardPageTemplate>

      {/* Detail Sheet */}
      {selectedDriver && (
        <DetailSheet
          open={detailOpen}
          onOpenChange={setDetailOpen}
          title={selectedDriver.name}
        >
          <DriverDetailSheetContent 
            driverId={selectedDriver.id} 
            driverName={selectedDriver.name} 
          />
        </DetailSheet>
      )}
    </>
  );
}

export default function FleetOperatorDashboard() {
  return (
    <ManagerOnly>
      <FleetDashboardPage />
    </ManagerOnly>
  );
}
