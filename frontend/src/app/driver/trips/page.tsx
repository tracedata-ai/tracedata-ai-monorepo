/**
 * Driver Trips Route
 */
import DriverTrips from "../trips";

export const metadata = {
  title: "My Trips - TraceData Driver",
  description: "View your trip history and scores",
};

export default function Page() {
  return <DriverTrips />;
}
