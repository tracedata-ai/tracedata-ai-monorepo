/**
 * Driver Dashboard Route
 */
import DriverDashboard from "./dashboard";

export const metadata = {
  title: "My Dashboard - TraceData Driver",
  description: "Your driving performance and insights",
};

export default function Page() {
  return <DriverDashboard />;
}
