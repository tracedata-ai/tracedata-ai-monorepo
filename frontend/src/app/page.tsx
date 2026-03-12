import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  LayoutDashboardIcon, 
  ActivityIcon, 
  TrendingUpIcon, 
  AlertTriangleIcon 
} from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">
          Overview
        </h2>
        <p className="text-slate-500">
          Monitor your fleet activity and statistics here.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">
              Total Paths
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              98
            </div>
          </CardContent>
        </Card>

        <Card className="border shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">
              Trip Confidence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              92.4%
            </div>
          </CardContent>
        </Card>

        <Card className="border shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
              Active Issues
              <AlertTriangleIcon className="w-4 h-4 text-amber-500" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              3
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
