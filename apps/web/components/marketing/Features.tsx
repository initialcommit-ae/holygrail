export default function Features() {
  return (
    <section
      data-theme="dark"
      className="bg-black py-24 px-8 theme-transition"
    >
      <div className="max-w-[1400px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Olive Card */}
          <div className="bg-[#717a41] rounded-[2.5rem] p-10 min-h-[440px] flex flex-col justify-between reveal">
            <div>
              <div className="text-[10px] tracking-widest text-white/50 mb-8 uppercase font-mono">
                Real-time Analysis
              </div>
              <h3 className="text-white text-[32px] leading-tight light-heading">
                Automated <br /> Insights
              </h3>
            </div>
            <div className="flex justify-end">
              <button className="w-14 h-14 bg-[#9ba75e] rounded-full flex items-center justify-center text-white hover:scale-110 transition-all">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M17 8l4 4m0 0l-4 4m4-4H3"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* Image Card */}
          <div
            className="relative rounded-[2.5rem] p-10 min-h-[440px] flex flex-col justify-between overflow-hidden reveal"
            style={{ transitionDelay: "0.1s" }}
          >
            <div className="absolute inset-0 bg-slate-900 opacity-80" />
            <div
              className="absolute inset-0 bg-cover bg-center mix-blend-overlay grayscale"
              style={{
                backgroundImage: `url('https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=2070&auto=format&fit=crop')`,
              }}
            />

            <div className="relative z-10 bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-600/20 rounded flex items-center justify-center text-blue-400 text-[10px] font-mono border border-blue-500/30">
                    AI
                  </div>
                  <span className="text-white text-[13px] light-heading">
                    Sentiment scan
                  </span>
                </div>
                <span className="text-white/30 text-[11px] font-mono tracking-tighter">
                  LIVE FEED
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                  <div className="w-3/4 h-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.5)]" />
                </div>
              </div>
            </div>

            <div className="relative z-10">
              <h3 className="text-white text-[18px] mb-3 light-heading">
                Adaptive research management
              </h3>
              <p className="text-white/50 text-[13px] leading-relaxed">
                MeshAi eliminates manual click work and automates the synthesis
                for you.
              </p>
            </div>
          </div>

          {/* Blurred Image Card 2 */}
          <div
            className="relative rounded-[2.5rem] p-10 min-h-[440px] flex flex-col justify-end overflow-hidden reveal"
            style={{ transitionDelay: "0.2s" }}
          >
            <div
              className="absolute inset-0 bg-cover bg-center"
              style={{
                backgroundImage: `url('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=2070&auto=format&fit=crop')`,
              }}
            />
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
            <div className="relative z-10 flex flex-col justify-between h-full">
              <div className="text-[10px] tracking-widest text-white/50 uppercase font-mono">
                Global Reach
              </div>
              <div className="flex justify-end">
                <button className="w-14 h-14 bg-white/10 backdrop-blur-md rounded-full flex items-center justify-center text-white hover:bg-white hover:text-black transition-all">
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M17 8l4 4m0 0l-4 4m4-4H3"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Tan Card */}
          <div
            className="bg-[#b3a382] rounded-[2.5rem] p-10 min-h-[440px] flex flex-col justify-between reveal"
            style={{ transitionDelay: "0.3s" }}
          >
            <div>
              <div className="text-[10px] tracking-widest text-black/40 mb-8 uppercase font-mono">
                Targeting
              </div>
              <h3 className="text-slate-900 text-[32px] leading-tight light-heading">
                Audience <br /> Targeting
              </h3>
            </div>
            <div className="flex justify-end">
              <button className="w-14 h-14 bg-black/5 rounded-full flex items-center justify-center text-slate-900 hover:bg-black hover:text-white transition-all">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M17 8l4 4m0 0l-4 4m4-4H3"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
