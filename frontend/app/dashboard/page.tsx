import React from "react";

export default function DashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Fleet Manager Dashboard</h1>
      <p className="mb-4">Welcome to TraceData.ai Fleet Operations.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Placeholder cards */}
        <div className="bg-white shadow rounded p-6">
          <h2 className="text-xl font-semibold mb-2">Fleet Status</h2>
          <p>Active Vehicles: 24</p>
          <p>Maintenance Due: 3</p>
        </div>

        <div className="bg-white shadow rounded p-6">
          <h2 className="text-xl font-semibold mb-2">Recent Alerts</h2>
          <ul className="list-disc list-inside">
            <li>Vehicle V-102: Low Tire Pressure</li>
            <li>Driver D-05: Harsh Braking</li>
          </ul>
        </div>

        <div className="bg-white shadow rounded p-6">
          <h2 className="text-xl font-semibold mb-2">Route Optimization</h2>
          <p>3 active routes optimized today.</p>
        </div>
      </div>
    </div>
  );
}
