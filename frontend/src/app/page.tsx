import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/sections/HeroSection";
import { EcosystemSection } from "@/components/sections/EcosystemSection";
import { DashboardPreview } from "@/components/sections/DashboardPreview";
import { HumanInTheLoop } from "@/components/sections/HumanInTheLoop";
import { BurnoutHeatmap } from "@/components/sections/BurnoutHeatmap";

export default function Home() {
  return (
    <div className="min-h-screen bg-brand-deep-navy font-sans antialiased overflow-x-hidden">
      <Navbar />
      
      <main>
        <HeroSection />
        <EcosystemSection />
        <DashboardPreview />
        <HumanInTheLoop />
        <BurnoutHeatmap />
      </main>
      
      <Footer />
    </div>
  );
}
