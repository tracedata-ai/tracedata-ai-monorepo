/**
 * Driver Profile Route
 */
import DriverProfile from "../profile";

export const metadata = {
  title: "My Profile - TraceData Driver",
  description: "Your profile and performance summary",
};

export default function Page() {
  return <DriverProfile />;
}
