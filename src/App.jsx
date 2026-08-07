import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, CheckCircle2, Clock, Loader2, Sparkles, 
  FileText, Code, Search, ShieldCheck, Terminal 
} from 'lucide-react';

const initialAgents = [
  { id: 1, name: 'Planner Agent', desc: 'Analyzing goal and creating execution plan', icon: FileText, status: 'pending' },
  { id: 2, name: 'Research Agent', desc: 'Researching information and gathering data', icon: Search, status: 'pending' },
  { id: 3, name: 'Developer Agent', desc: 'Developing solution and implementation', icon: Code, status: 'pending' },
  { id: 4, name: 'Reviewer Agent', desc: 'Reviewing solution for quality and accuracy', icon: ShieldCheck, status: 'pending' },
  { id: 5, name: 'Reporter Agent', desc: 'Generating final report and recommendations', icon: Bot, status: 'pending' },
];

export default function App() {
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [agents, setAgents] = useState(initialAgents);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);

  const handleSolve = async () => {
    if (!goal) return;
    setLoading(true);
    setResult(null);
    setLogs([]);
    setProgress(10);

    updateAgentStatus(0, 'in_progress', 'Planner Agent started analyzing the goal');
    
    try {
      setTimeout(() => {
        updateAgentStatus(0, 'completed', 'Planner Agent completed execution plan');
        updateAgentStatus(1, 'in_progress', 'Research Agent started research process');
        setProgress(40);
      }, 1500);

      // Connecting with your FastAPI Backend
      const response = await axios.post('http://127.0.0.1:8000/solve', { goal });
      
      setTimeout(() => {
        setAgents(prev => prev.map(a => ({ ...a, status: 'completed' })));
        setProgress(100);
        setResult(response.data.result || JSON.stringify(response.data, null, 2));
        setLoading(false);
      }, 3500);

    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, `${new Date().toLocaleTimeString()} - Error connecting to backend (Make sure FastAPI is running)`]);
      setLoading(false);
    }
  };

  const updateAgentStatus = (index, status, logMsg) => {
    setAgents(prev => prev.map((ag, i) => i === index ? { ...ag, status } : ag));
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()} - ${logMsg}`]);
  };

  return (
    <div className="min-h-screen bg-[#0A0D14] text-slate-200 font-sans p-6">
      {/* Header */}
      <header className="flex justify-between items-center max-w-7xl mx-auto mb-10 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600/20 text-purple-400 rounded-lg border border-purple-500/30">
            <Bot size={28} />
          </div>
          <h1 className="text-xl font-bold text-white tracking-wide">AgentForge <span className="text-purple-500">AI</span></h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="px-3 py-1 bg-slate-900 border border-slate-800 rounded-full flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${loading ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'}`}></span>
            Status: {loading ? 'Processing' : 'Ready'}
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-8">
        {/* Goal Input Section */}
        <section className="text-center max-w-3xl mx-auto space-y-4">
          <h2 className="text-4xl font-extrabold text-white tracking-tight">
            Multi-Agent Collaboration <br />
            <span className="bg-gradient-to-r from-purple-400 to-indigo-500 bg-clip-text text-transparent">
              for Complex Goal Solving
            </span>
          </h2>
          
          <div className="relative mt-6 bg-[#111622] p-2 rounded-xl border border-slate-800 shadow-2xl">
            <textarea
              rows="3"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Example: Build a sustainable smart city roadmap for 2030..."
              className="w-full bg-transparent p-3 text-slate-100 placeholder-slate-500 focus:outline-none resize-none"
            />
            <div className="flex justify-between items-center px-3 pt-2 border-t border-slate-800/60">
              <span className="text-xs text-slate-500">{goal.length}/1000</span>
              <button
                onClick={handleSolve}
                disabled={loading || !goal}
                className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium px-5 py-2.5 rounded-lg transition-all duration-200 flex items-center gap-2 shadow-lg shadow-purple-600/20 cursor-pointer"
              >
                {loading ? <Loader2 className="animate-spin" size={18} /> : <Sparkles size={18} />}
                Solve with AI Agents
              </button>
            </div>
          </div>
        </section>

        {/* Dashboard Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Panel: Workflow & Agents */}
          <div className="lg:col-span-7 bg-[#111622] rounded-xl border border-slate-800/80 p-6 space-y-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Bot className="text-purple-400" size={20} /> AI Agents in Action
            </h3>

            <div className="space-y-3">
              {agents.map((agent) => {
                const Icon = agent.icon;
                return (
                  <motion.div 
                    key={agent.id}
                    animate={{ scale: agent.status === 'in_progress' ? 1.02 : 1 }}
                    className={`flex items-center justify-between p-3.5 rounded-lg border transition-all ${
                      agent.status === 'in_progress' 
                        ? 'bg-purple-950/20 border-purple-500/50' 
                        : 'bg-slate-900/40 border-slate-800/60'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-md ${agent.status === 'in_progress' ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'}`}>
                        <Icon size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">{agent.name}</p>
                        <p className="text-xs text-slate-400">{agent.desc}</p>
                      </div>
                    </div>
                    <div>
                      {agent.status === 'completed' && <span className="text-emerald-400 text-xs flex items-center gap-1 font-medium"><CheckCircle2 size={14} /> Completed</span>}
                      {agent.status === 'in_progress' && <span className="text-purple-400 text-xs flex items-center gap-1 font-medium"><Loader2 size={14} className="animate-spin" /> In Progress</span>}
                      {agent.status === 'pending' && <span className="text-slate-500 text-xs flex items-center gap-1"><Clock size={14} /> Pending</span>}
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Progress Bar & Logs */}
            <div className="pt-4 border-t border-slate-800/80 space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Overall Progress</span>
                  <span className="text-purple-400 font-bold">{progress}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <motion.div 
                    className="bg-purple-500 h-full" 
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              <div className="bg-[#0A0D14] p-3 rounded-lg border border-slate-800 text-xs font-mono h-28 overflow-y-auto space-y-1">
                <p className="text-slate-500 flex items-center gap-1 border-b border-slate-800/50 pb-1 mb-1">
                  <Terminal size={12} /> Live Execution Logs
                </p>
                {logs.length === 0 && <span className="text-slate-600">Waiting for task start...</span>}
                {logs.map((log, index) => (
                  <p key={index} className="text-purple-300/80">{log}</p>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel: Output */}
          <div className="lg:col-span-5 bg-[#111622] rounded-xl border border-slate-800/80 p-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <FileText className="text-purple-400" size={20} /> Final Result
                </h3>
                <span className="text-xs bg-slate-800 px-2.5 py-1 rounded-full text-slate-400">
                  {result ? 'Completed' : 'Waiting'}
                </span>
              </div>

              <div className="min-h-[300px] flex items-center justify-center border border-dashed border-slate-800 rounded-lg p-4">
                <AnimatePresence mode="wait">
                  {result ? (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="w-full text-sm text-slate-300 font-mono whitespace-pre-wrap bg-[#0A0D14] p-4 rounded-lg overflow-auto max-h-[350px]"
                    >
                      {result}
                    </motion.div>
                  ) : (
                    <div className="text-center space-y-2 text-slate-500">
                      <Bot size={40} className="mx-auto text-slate-700 animate-pulse" />
                      <p className="text-sm font-medium text-slate-400">Final report will appear here</p>
                      <p className="text-xs max-w-xs">The AI agents are working together to generate a comprehensive solution for your goal.</p>
                    </div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}