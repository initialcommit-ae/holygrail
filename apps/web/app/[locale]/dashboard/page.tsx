"use client";

import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Type } from "@google/genai";
import { useRouter } from 'next/navigation';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Demographics {
  ageRange: string;
  location: string;
  occupation: string;
  count?: number;
}

export default function Dashboard() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hi! I'm MeshAi's research architect. Describe the survey objective you have in mind. Who do you want to reach?" }
  ]);
  const [input, setInput] = useState('');
  const [demographics, setDemographics] = useState<Demographics | null>(null);
  const [questions, setQuestions] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [step, setStep] = useState<'chat' | 'questions' | 'billing' | 'success'>('chat');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isGenerating) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsGenerating(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.NEXT_PUBLIC_GEMINI_API_KEY || '' });
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: [
          { role: 'user', parts: [{ text: `Previous conversation: ${JSON.stringify(messages)}. New User message: ${userMsg}. You are a research architect. Reply naturally and helpful. If you have enough info about target age, location, and occupation, summarize them briefly. Format your extraction as JSON at the very end of your message in a separate line if found, otherwise just chat.` }] }
        ],
        config: {
            systemInstruction: "You are MeshAi's survey architect. Your goal is to help users define their research objective and target audience. Be concise, professional, and friendly. Extract ageRange, location, and occupation details whenever possible."
        }
      });

      const aiText = response.text || "I'm processing that...";

      // Basic extraction check
      if (aiText.includes('{')) {
         // This is a naive demo extraction logic
         setDemographics({
           ageRange: "18-35",
           location: "Global",
           occupation: "Tech Professionals",
           count: Math.floor(Math.random() * 500) + 200
         });
      }

      setMessages(prev => [...prev, { role: 'assistant', content: aiText }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Something went wrong. Let's try again." }]);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateSurveyQuestions = async () => {
    setIsGenerating(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.NEXT_PUBLIC_GEMINI_API_KEY || '' });
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `Based on this objective: "${messages.map(m => m.content).join(' ')}", generate 10 research-grade survey questions.`,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              questions: {
                type: Type.ARRAY,
                items: { type: Type.STRING }
              }
            },
            required: ["questions"]
          }
        }
      });

      const data = JSON.parse(response.text || '{"questions": []}');
      setQuestions(data.questions);
      setStep('questions');
    } catch (error) {
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const startSurvey = () => {
      setStep('success');
  };

  const handleBack = () => {
    router.push('/');
  };

  return (
    <div className="flex h-screen bg-white text-slate-900 font-light overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-100 flex flex-col bg-[#fafafa]">
        <div className="p-8 flex items-center gap-2 cursor-pointer group" onClick={handleBack}>
          <div className="w-5 h-5 bg-black rounded-full flex items-center justify-center transition-transform group-hover:scale-110">
             <div className="w-2.5 h-2.5 bg-white rounded-sm rotate-45" />
          </div>
          <span className="text-xl tracking-tight font-medium">MeshAi</span>
        </div>

        <nav className="flex-grow p-4 space-y-2 text-[13px]">
          <button
            onClick={() => { setStep('chat'); setMessages([{ role: 'assistant', content: "Ready for a new research brief. What's the goal?" }]); }}
            className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${step === 'chat' ? 'bg-black text-white' : 'hover:bg-slate-100 text-slate-500'}`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" /></svg>
            New Survey
          </button>
          <button className="w-full text-left px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-500 transition-all flex items-center gap-3">
             <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
             Past Surveys
          </button>
          <button className="w-full text-left px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-500 transition-all flex items-center gap-3">
             <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
             Conversation
          </button>

          <div className="pt-4 mt-4 border-t border-slate-200/60">
            <button
              onClick={handleBack}
              className="w-full text-left px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-500 transition-all flex items-center gap-3"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
              Exit to Website
            </button>
          </div>
        </nav>

        <div className="p-6 border-t border-slate-100 bg-white">
           <div className="flex items-center gap-3 text-xs text-slate-400">
             <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center">
               <svg className="w-4 h-4 text-slate-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
             </div>
             <div>
               <div className="text-slate-900 font-medium">Research Team</div>
               <div>Standard Plan</div>
             </div>
           </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-grow flex flex-col relative">
        <header className="h-16 border-b border-slate-100 flex items-center justify-between px-8 bg-white/50 backdrop-blur-md sticky top-0 z-10">
           <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-mono">Dashboard / New Campaign</div>
           <div className="flex items-center gap-4">
             {demographics && step === 'chat' && (
               <button
                onClick={generateSurveyQuestions}
                disabled={isGenerating}
                className="bg-black text-white px-6 py-2 rounded-full text-xs hover:bg-slate-800 transition-all disabled:opacity-50"
               >
                 {isGenerating ? 'Architecting...' : 'Review Questions'}
               </button>
             )}
           </div>
        </header>

        <div className="flex-grow overflow-y-auto p-8 flex flex-col items-center">
          {step === 'chat' && (
            <div className="max-w-3xl w-full space-y-6">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-6 py-4 text-[14px] leading-relaxed ${msg.role === 'user' ? 'bg-black text-white' : 'bg-[#f2f4f7] text-slate-800'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isGenerating && (
                <div className="flex justify-start">
                  <div className="bg-[#f2f4f7] rounded-full px-4 py-2 flex gap-1 items-center">
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          )}

          {step === 'questions' && (
            <div className="max-w-3xl w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
               <h2 className="text-3xl mb-8 light-heading">Survey Draft</h2>
               <div className="space-y-4">
                  {questions.map((q, i) => (
                    <div key={i} className="p-6 bg-white border border-slate-100 rounded-2xl flex items-start gap-4 hover:border-slate-300 transition-all group">
                       <span className="text-slate-300 font-mono text-sm pt-1">{i + 1}</span>
                       <p className="flex-grow text-[15px]">{q}</p>
                       <button className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-red-500">
                         <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                       </button>
                    </div>
                  ))}
               </div>
               <div className="mt-12 flex justify-between items-center">
                  <button onClick={() => setStep('chat')} className="text-slate-400 text-sm hover:text-slate-600 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7" /></svg>
                    Refine goal
                  </button>
                  <button onClick={() => setStep('billing')} className="bg-black text-white px-10 py-4 rounded-full text-lg shadow-xl shadow-black/5 active:scale-95 transition-all">
                    Finalize Deployment
                  </button>
               </div>
            </div>
          )}

          {step === 'billing' && (
            <div className="max-w-xl w-full text-center py-20 animate-in zoom-in duration-500">
               <div className="inline-block p-4 bg-emerald-50 text-emerald-600 rounded-full mb-8">
                 <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
               </div>
               <h2 className="text-4xl light-heading mb-4">Research Ready</h2>
               <p className="text-slate-500 mb-12">We've locked in 342 verified respondents matching your target profile.</p>

               <div className="bg-[#f9fafb] rounded-[2.5rem] p-10 mb-12 text-left space-y-4 border border-slate-100">
                  <div className="flex justify-between border-b border-slate-200 pb-4">
                    <span className="text-slate-500 font-mono text-[11px]">VOLUME</span>
                    <span>200 Responses</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-200 pb-4">
                    <span className="text-slate-500 font-mono text-[11px]">AI ENGINE</span>
                    <span className="text-emerald-500">Sentiment Synthesis included</span>
                  </div>
                  <div className="flex justify-between pt-4">
                    <span className="text-slate-900 font-medium">Platform Fee</span>
                    <span className="text-2xl font-medium">$49.00</span>
                  </div>
               </div>

               <button onClick={startSurvey} className="w-full bg-black text-white py-5 rounded-full text-xl shadow-2xl shadow-black/10 active:scale-95 transition-all">
                  Launch My Campaign
               </button>
            </div>
          )}

          {step === 'success' && (
             <div className="max-w-md w-full text-center py-32 animate-in slide-in-from-bottom-8 duration-700">
               <div className="w-24 h-24 bg-emerald-500 rounded-full flex items-center justify-center text-white mx-auto mb-10 shadow-2xl shadow-emerald-500/20">
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
               </div>
               <h2 className="text-4xl light-heading mb-4">Live & Collecting</h2>
               <p className="text-slate-500 mb-10 leading-relaxed">Your campaign is now circulating. Respondents are providing feedback in real-time. Sentiment reports will populate in roughly 15 minutes.</p>
               <div className="flex flex-col gap-4">
                 <button onClick={() => setStep('chat')} className="bg-black text-white px-8 py-4 rounded-full hover:bg-slate-800 transition-all">Go to Analysis</button>
                 <button onClick={handleBack} className="text-slate-400 text-sm hover:text-slate-900 transition-colors">Return to Homepage</button>
               </div>
             </div>
          )}
        </div>

        {/* Input area */}
        {step === 'chat' && (
          <div className="p-8 bg-white border-t border-slate-100">
            <div className="max-w-3xl mx-auto relative">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Describe what you want to learn..."
                className="w-full bg-[#f2f4f7] rounded-full pl-8 pr-16 py-5 text-[14px] focus:outline-none focus:ring-1 focus:ring-black/10 transition-all placeholder:text-slate-400"
              />
              <button
                onClick={handleSendMessage}
                disabled={!input.trim() || isGenerating}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:bg-slate-800 transition-all disabled:opacity-20"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Right Utility Panel */}
      {step === 'chat' && (
        <aside className="w-80 border-l border-slate-100 bg-white p-8">
           <div className="mb-12">
             <h4 className="text-[10px] uppercase tracking-widest text-slate-400 mb-8 font-mono">Real-time Audience</h4>
             {demographics ? (
               <div className="space-y-6">
                 <div>
                    <div className="text-[10px] text-slate-400 mb-1 font-mono">TARGETING</div>
                    <div className="text-sm bg-slate-50 p-3 rounded-xl border border-slate-100">{demographics.ageRange} • {demographics.occupation}</div>
                 </div>
                 <div>
                    <div className="text-[10px] text-slate-400 mb-1 font-mono">REGION</div>
                    <div className="text-sm bg-slate-50 p-3 rounded-xl border border-slate-100">{demographics.location}</div>
                 </div>
                 <div className="p8 border-t border-slate-100 text-center">
                    <div className="text-4xl light-heading tracking-tighter">{demographics.count}</div>
                    <div className="text-[10px] text-emerald-500 font-mono tracking-widest uppercase mt-2">Active Matches</div>
                 </div>
               </div>
             ) : (
               <div className="py-24 flex flex-col items-center justify-center text-center opacity-30 border-2 border-dashed border-slate-100 rounded-3xl">
                  <svg className="w-8 h-8 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                  <p className="text-[12px] leading-relaxed">Tell us your goal to <br /> find your audience</p>
               </div>
             )}
           </div>

           <div className="pt-8 border-t border-slate-100">
              <h4 className="text-[10px] uppercase tracking-widest text-slate-400 mb-4 font-mono">Project Cost</h4>
              <div className="text-3xl light-heading">$0.00</div>
              <p className="text-[11px] text-slate-400 mt-3 leading-relaxed">Calculated based on target complexity and response depth.</p>
           </div>
        </aside>
      )}
    </div>
  );
}
