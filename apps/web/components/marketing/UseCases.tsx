const useCases = [
  {
    title: "Market Research",
    description: "Understand why people choose competitors.",
    items: [
      "Competitor Benchmarking",
      "Brand Perception",
      "Pricing Elasticity",
    ],
  },
  {
    title: "Public Policy",
    description: "Gather citizen feedback on new initiatives.",
    items: [
      "Local Planning",
      "Service Improvement",
      "Community Sentiment",
    ],
  },
  {
    title: "User Behavior",
    description: "Map out the 'why' behind the 'what' for new products.",
    items: [
      "Needs Assessment",
      "Journey Mapping",
      "Concept Validation",
    ],
  },
];

export default function UseCases() {
  return (
    <section
      id="use-cases"
      data-theme="light"
      className="py-32 bg-slate-50 theme-transition"
    >
      <div className="max-w-[1400px] mx-auto px-8">
        <div className="flex justify-between items-end mb-20 reveal">
          <div>
            <div className="text-[11px] tracking-[0.2em] uppercase text-slate-400 mb-6">
              Solutions
            </div>
            <h2 className="text-5xl light-heading text-slate-900">
              Trusted For...
            </h2>
          </div>
          <p className="text-slate-500 max-w-xs text-right text-sm">
            Versatile research frameworks for teams of every size and sector.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {useCases.map((useCase, idx) => (
            <div
              key={idx}
              className="bg-white p-12 rounded-[2.5rem] border border-slate-100 flex flex-col reveal"
              style={{ transitionDelay: `${idx * 0.1}s` }}
            >
              <h3 className="text-2xl mb-4 text-slate-900 light-heading">
                {useCase.title}
              </h3>
              <p className="text-slate-500 mb-12 text-[15px]">
                {useCase.description}
              </p>
              <div className="space-y-3 mt-auto">
                {useCase.items.map((item, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 text-[13px] text-slate-400 bg-slate-50/50 py-3 px-5 rounded-full border border-slate-100"
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
