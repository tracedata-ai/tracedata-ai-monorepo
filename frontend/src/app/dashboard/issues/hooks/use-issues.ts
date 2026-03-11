import { useState } from "react";
import { dashboardConfig } from "@/config/dashboard";

export function useIssues() {
  const [activeTab, setActiveTab] = useState("Open");
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  // Derive the selected issue
  const selectedIssue = dashboardConfig.issues.find(
    (issue) => issue.id === selectedIssueId
  ) || null;

  return {
    issues: dashboardConfig.issues,
    activeTab,
    setActiveTab,
    selectedIssueId,
    setSelectedIssueId,
    selectedIssue,
  };
}
