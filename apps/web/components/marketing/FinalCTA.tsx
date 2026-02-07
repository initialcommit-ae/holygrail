import { Link } from '@/i18n/routing';

export default function FinalCTA() {
  return (
    <section
      data-theme="light"
      className="py-48 bg-white theme-transition"
    >
      <div className="max-w-4xl mx-auto px-8 text-center reveal">
        <div className="text-[11px] tracking-[0.2em] uppercase text-slate-400 mb-10">
          Get Started
        </div>
        <h2 className="text-[64px] leading-[1.1] text-slate-900 mb-10 light-heading">
          Ready to meet your <br /> next 200 respondents?
        </h2>
        <p className="text-[18px] text-slate-500 mb-14 max-w-lg mx-auto leading-relaxed">
          Join the platform that makes professional market research as easy as
          sending a Slack message.
        </p>
        <Link href="/dashboard" className="inline-block bg-black text-white px-14 py-5 rounded-full text-lg hover:bg-slate-800 transition-all shadow-2xl shadow-black/5 active:scale-95">
          Launch My Campaign
        </Link>
        <div className="mt-14 flex justify-center gap-10 text-[11px] text-slate-400 uppercase tracking-widest font-mono">
          <span className="flex items-center gap-2">
            <div className="w-1 h-1 bg-emerald-400 rounded-full" /> No credit
            card
          </span>
          <span className="flex items-center gap-2">
            <div className="w-1 h-1 bg-emerald-400 rounded-full" /> Cancel
            anytime
          </span>
        </div>
      </div>
    </section>
  );
}
