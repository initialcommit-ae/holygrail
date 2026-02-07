const steps = [
  {
    number: "01",
    title: "Define Your Intent",
    body: "Don't worry about phrasing. Tell us your goal and who you need to hear from. Our AI translates business objectives into professional parameters.",
    tag: "STRATEGY",
  },
  {
    number: "02",
    title: "Refine Your Draft",
    body: "Review a custom-built survey generated instantly. Add, remove, or tweak questions with a click. Total control, zero writer's block.",
    tag: "CREATION",
  },
  {
    number: "03",
    title: "Launch and Learn",
    body: "Hit 'Launch' and let us do the legwork. We tap into verified external pools. Come back to insights, not just rows of data.",
    tag: "RESULTS",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      data-theme="dark"
      className="py-32 bg-black text-white theme-transition"
    >
      <div className="max-w-[1400px] mx-auto px-8">
        <div className="flex flex-col md:flex-row justify-between items-end mb-24 reveal">
          <div className="max-w-xl">
            <div className="text-[11px] tracking-[0.2em] uppercase text-slate-500 mb-6">
              Execution Path
            </div>
            <h2 className="text-5xl md:text-6xl light-heading leading-tight">
              From idea to data <br /> in three smooth beats.
            </h2>
          </div>
          <p className="text-slate-400 text-lg max-w-sm mb-2 opacity-80">
            No PhD in statistics required. We built MeshAi for teams who need
            quality results without the legacy complexity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="group relative reveal"
              style={{ transitionDelay: `${idx * 0.15}s` }}
            >
              <div className="mb-12">
                <div className="text-[10px] tracking-widest text-slate-500 mb-4 font-mono">
                  {step.tag}
                </div>
                <div className="text-6xl font-light mb-8 text-slate-800 group-hover:text-white transition-colors duration-500">
                  {step.number}
                </div>
                <h3 className="text-2xl mb-4 light-heading">{step.title}</h3>
                <p className="text-slate-500 text-[15px] leading-relaxed group-hover:text-slate-300 transition-colors duration-500">
                  {step.body}
                </p>
              </div>
              <div className="h-[1px] w-full bg-slate-900 group-hover:bg-slate-700 transition-all duration-700" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
