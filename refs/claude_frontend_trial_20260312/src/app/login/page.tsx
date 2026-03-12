"use client";

import { useState } from "react";
import { useAuth, UserRole } from "@/context/AuthContext";
import { Grid2x2, Shield, Truck, Building2, Mail, Lock, ArrowRight, ChevronDown } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
  const [selectedRole, setSelectedRole] = useState<UserRole>("Manager");
  const [tenantId, setTenantId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (tenantId && email && password) {
      // Mock authentication
      login(tenantId, selectedRole);
    } else {
      alert("Please fill in all fields.");
    }
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-slate-50 font-sans text-slate-900">
      {/* Background Patterns */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(circle at 0% 0%, rgba(60, 131, 246, 0.15) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(217, 70, 239, 0.1) 0%, transparent 50%)"
        }}
      />
      <div 
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0l15 30-15 30L15 30z' fill='%233c83f6' fill-rule='evenodd'/%3E%3C/svg%3E\")"
        }}
      />

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-6 lg:px-12">
        <div className="flex items-center gap-3">
          <div className="size-10 bg-gradient-to-br from-blue-500 via-fuchsia-500 to-sky-500 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
            <Grid2x2 className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            TraceData <span className="font-light text-slate-500">Command</span>
          </h2>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <a className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors" href="#">Documentation</a>
          <a className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors" href="#">Support</a>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-[460px] bg-white border border-slate-200 rounded-2xl shadow-xl shadow-slate-200/50 p-8 lg:p-10 relative overflow-hidden">
          {/* Top Gradient Bar */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-fuchsia-500 to-sky-500"></div>
          
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2 text-slate-900">Welcome Back</h1>
            <p className="text-slate-500 text-sm">Access your fleet command dashboard</p>
          </div>

          {/* Role Toggle */}
          <div className="mb-8">
            <div className="flex p-1 bg-slate-100 rounded-xl">
              <button 
                type="button"
                onClick={() => setSelectedRole("Manager")}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold rounded-lg transition-all ${
                  selectedRole === "Manager" 
                    ? "bg-white shadow-sm text-blue-600" 
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                <Shield className="w-4 h-4" />
                Fleet Manager
              </button>
              <button 
                type="button"
                onClick={() => setSelectedRole("Driver")}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold rounded-lg transition-all ${
                  selectedRole === "Driver" 
                    ? "bg-white shadow-sm text-blue-600" 
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                <Truck className="w-4 h-4" />
                Driver
              </button>
            </div>
          </div>

          {/* Login Form */}
          <form className="space-y-5" onSubmit={handleLogin}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 px-1">Select Your Company</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors">
                  <Building2 className="w-5 h-5" />
                </div>
                <select 
                  value={tenantId}
                  onChange={(e) => setTenantId(e.target.value)}
                  className="w-full pl-11 pr-10 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all appearance-none cursor-pointer outline-none"
                  required
                >
                  <option value="" disabled>Search or select company</option>
                  <option value="logistics_pro">Logistics Pro Global</option>
                  <option value="nexus_freight">Nexus Freight Solutions</option>
                  <option value="quantum_move">Quantum Move Systems</option>
                </select>
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-slate-400">
                  <ChevronDown className="w-5 h-5" />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 px-1">Email Address</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors">
                  <Mail className="w-5 h-5" />
                </div>
                <input 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none" 
                  placeholder="name@company.com" 
                  type="email"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center px-1">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <a className="text-xs font-semibold text-blue-600 hover:underline" href="#">Forgot password?</a>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors">
                  <Lock className="w-5 h-5" />
                </div>
                <input 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none" 
                  placeholder="••••••••" 
                  type="password"
                  required
                />
              </div>
            </div>

            <div className="pt-2">
              <button 
                type="submit"
                className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 transition-all flex items-center justify-center gap-2 group"
              >
                Sign In to Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-100 text-center">
            <p className="text-sm text-slate-500">
              Don&apos;t have an account? <a className="text-fuchsia-600 font-semibold hover:underline" href="#">Contact Administrator</a>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 p-6 lg:p-12 flex flex-col md:flex-row justify-between items-center gap-4 text-slate-500 text-xs">
        <p>© 2026 TraceData Command. All rights reserved.</p>
        <div className="flex gap-6">
          <a className="hover:text-slate-900 transition-colors" href="#">Privacy Policy</a>
          <a className="hover:text-slate-900 transition-colors" href="#">Terms of Service</a>
          <a className="hover:text-slate-900 transition-colors" href="#">System Status</a>
        </div>
      </footer>

      {/* Ambient background glows */}
      <div className="fixed top-1/4 -right-20 w-64 h-64 bg-fuchsia-500/10 blur-[100px] rounded-full pointer-events-none z-0"></div>
      <div className="fixed bottom-1/4 -left-20 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full pointer-events-none z-0"></div>
    </div>
  );
}
