/**
 * Driver Appeals Route
 */
import DriverAppeals from "../appeals";

export const metadata = {
  title: "Appeals & Disputes - TraceData Driver",
  description: "Manage your trip appeals and disputes",
};

export default function Page() {
  return <DriverAppeals />;
}
