export default function Hero() {
  return (
    <section
      data-theme="light"
      className="relative pt-40 pb-20 overflow-hidden bg-white theme-transition"
    >
      <div className="max-w-[1400px] mx-auto px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Left Column: Text */}
          <div className="lg:col-span-5 pt-12 reveal">
            <div className="text-[11px] tracking-[0.2em] uppercase text-slate-400 mb-12">
              AI-Powered Market Research Software
            </div>
            <h1 className="text-[64px] leading-[1.1] text-slate-900 mb-10 light-heading">
              With{" "}
              <span className="inline-block w-10 h-10 bg-black rounded-full align-middle mb-2 mx-1" />{" "}
              MeshAi <br />
              your research <br />
              manages itself
            </h1>
            <p className="text-[17px] text-slate-500 max-w-sm mb-12 leading-relaxed">
              Real-time insight into your audience, minimize research bias and
              put survey management on autopilot with AI.
            </p>
            <div className="flex items-center gap-4">
              <button className="bg-black text-white px-10 py-4 rounded-full text-[15px] hover:bg-slate-800 transition-all">
                Book a meeting
              </button>
              <button className="bg-[#f2f4f7] text-slate-900 px-10 py-4 rounded-full text-[15px] hover:bg-slate-200 transition-all">
                Start your free trial
              </button>
            </div>

            <div className="mt-24">
              <div className="text-[13px] text-slate-500 mb-4">
                7,000+ positive reviews
              </div>
              <div className="flex items-center gap-1 text-slate-900">
                {[1, 2, 3, 4, 5].map((i) => (
                  <svg
                    key={i}
                    className="w-4 h-4 fill-current"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                  </svg>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Visuals */}
          <div className="lg:col-span-7 relative">
            <div className="grid grid-cols-2 gap-6 items-start">
              <div className="space-y-6 reveal" style={{ transitionDelay: "0.2s" }}>
                <div className="bg-[#e0e3e7] rounded-3xl p-1 overflow-hidden">
                  <div className="bg-white rounded-[1.4rem] h-48 relative overflow-hidden p-6 flex flex-col justify-end">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-[#e31e24] rounded-full translate-x-8 -translate-y-8" />
                    <div className="absolute top-0 left-0 w-24 h-24 bg-[#111c4e] rounded-full -translate-x-4 -translate-y-4" />
                    <div className="text-[10px] text-slate-400 mb-2 uppercase tracking-widest">
                      Survey Participant ID
                    </div>
                    <div className="text-lg font-mono tracking-tighter">
                      MESH 5678 9101 2456
                    </div>
                  </div>
                </div>

                <div className="bg-[#e0e3e7] rounded-[3rem] p-3 border-[6px] border-[#d1d5db]">
                  <div className="bg-white rounded-[2.2rem] min-h-[500px] overflow-hidden p-6">
                    <div className="flex justify-between items-center mb-8">
                      <span className="text-[12px] font-mono">9:41</span>
                      <div className="w-16 h-5 bg-black rounded-full" />
                    </div>
                    <h3 className="text-2xl mb-6 text-slate-900">
                      Active Campaigns
                    </h3>
                    <div className="flex bg-[#f2f4f7] rounded-full p-1 mb-8">
                      <button className="flex-1 bg-white rounded-full py-1 text-[12px] shadow-sm text-slate-900">
                        Live
                      </button>
                      <button className="flex-1 py-1 text-[12px] text-slate-400">
                        Drafts
                      </button>
                    </div>
                    <div className="space-y-6">
                      {[
                        {
                          title: "Gen Z Habits",
                          val: "142 responses",
                          col: "emerald",
                        },
                        {
                          title: "Remote Work",
                          val: "89 responses",
                          col: "emerald",
                        },
                        {
                          title: "Coffee Pricing",
                          val: "Pending",
                          col: "amber",
                        },
                      ].map((item, i) => (
                        <div
                          key={i}
                          className="flex justify-between items-center py-2 border-b border-slate-50 text-slate-900"
                        >
                          <div>
                            <div className="text-[14px]">{item.title}</div>
                            <div className="text-[11px] text-slate-400">
                              24.02.2024
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-[14px]">{item.val}</div>
                            <div
                              className={
                                item.col === "amber"
                                  ? "text-[10px] text-amber-500"
                                  : "text-[10px] text-emerald-500"
                              }
                            >
                              • Active
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="reveal" style={{ transitionDelay: "0.4s" }}>
                <div className="bg-[#e0e3e7] rounded-[2rem] p-4 min-h-[600px]">
                  <div className="bg-white rounded-2xl h-full shadow-sm p-6">
                    <div className="flex items-center gap-2 mb-8">
                      <div className="w-4 h-4 bg-black rounded-full" />
                      <span className="text-sm text-slate-900">MeshAi</span>
                    </div>
                    <div className="space-y-4 text-[13px] text-slate-500 mb-12">
                      <div className="flex items-center gap-3 p-2 bg-slate-50 rounded-lg text-slate-900">
                        <div className="w-4 h-4 rounded border border-slate-300" />
                        Insights Dashboard
                      </div>
                      <div className="flex items-center gap-3 p-2">
                        <div className="w-4 h-4 rounded border border-slate-200" />
                        Audience Builder
                      </div>
                      <div className="flex items-center gap-3 p-2">
                        <div className="w-4 h-4 rounded border border-slate-200" />
                        Survey Library
                      </div>
                    </div>
                    <div className="border-t pt-8">
                      <div className="text-[11px] uppercase text-slate-400 mb-4">
                        Recent Respondents
                      </div>
                      <div className="space-y-4">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <div
                            key={i}
                            className="flex justify-between text-[12px] border-b border-slate-50 pb-2 text-slate-900"
                          >
                            <span>User_{i * 123}</span>
                            <span className="text-slate-400">Verified</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
