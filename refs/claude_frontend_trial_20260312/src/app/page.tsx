import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/sections/HeroSection";
import { LogoMarquee } from "@/components/sections/LogoMarquee";
import { SolutionGrid } from "@/components/sections/SolutionGrid";
import { AgentArchitectureSection } from "@/components/sections/AgentArchitectureSection";
import { DashboardPreview } from "@/components/sections/DashboardPreview";
import { ResultsSection } from "@/components/sections/ResultsSection";
import { Testimonials } from "@/components/sections/Testimonials";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground font-sans antialiased overflow-x-hidden">
      <Navbar />

      <main>
        <HeroSection />
        <LogoMarquee />
        <SolutionGrid />
        <AgentArchitectureSection />
        <DashboardPreview />
        <ResultsSection />
        <Testimonials />
      </main>

      <Footer />
    </div>
  );
}
