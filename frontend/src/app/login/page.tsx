"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { BrandMark } from "@/components/shared/BrandMark";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function LoginPage() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<string>("");

  const handleNavigate = () => {
    if (selectedRole === "fleet-manager") {
      router.push("/fleet-manager");
    } else if (selectedRole === "driver") {
      router.push("/driver");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--gray-50)] to-[var(--gray-100)] flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <BrandMark size={64} priority />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            TraceData Fleet Console
          </h1>
          <p className="text-lg text-muted-foreground">
            Intelligent fleet operations, safety, and driver management
            platform.
          </p>
        </div>

        <Card className="glass rounded-xl p-8 space-y-6">
          <div className="space-y-3">
            <label className="text-sm font-semibold text-foreground">
              Select Your Role
            </label>
            <Select
              value={selectedRole || null}
              onValueChange={(value) => setSelectedRole(value ?? "")}
            >
              <SelectTrigger className="bg-white/50 border-[var(--info)]/30 text-foreground">
                <SelectValue placeholder="Choose role to continue..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fleet-manager">
                  Fleet Manager - View dashboards, routes, drivers, and issues
                </SelectItem>
                <SelectItem value="driver">
                  Driver - View your trips, fatigue level, and safety alerts
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={handleNavigate}
            disabled={!selectedRole}
            className="w-full bg-[var(--info)] text-white hover:bg-[hsl(210_100%_45%)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue to Portal
          </Button>
        </Card>
      </div>
    </div>
  );
}
