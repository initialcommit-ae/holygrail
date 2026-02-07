import Navbar from "../components/marketing/Navbar";
import Hero from "../components/marketing/Hero";
import Problem from "../components/marketing/Problem";
import HowItWorks from "../components/marketing/HowItWorks";
import Features from "../components/marketing/Features";
import UseCases from "../components/marketing/UseCases";
import FinalCTA from "../components/marketing/FinalCTA";
import Footer from "../components/marketing/Footer";
import ThemeRevealProvider from "../components/marketing/ThemeRevealProvider";

export default function Home() {
  return (
    <ThemeRevealProvider>
      <div className="min-h-screen flex flex-col selection:bg-black selection:text-white">
        <Navbar />
        <main className="grow">
          <Hero />
          <Problem />
          <HowItWorks />
          <Features />
          <UseCases />
          <FinalCTA />
        </main>
        <Footer />
      </div>
    </ThemeRevealProvider>
  );
}
