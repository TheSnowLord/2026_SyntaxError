import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot, CheckCircle2, Clock, Loader2, Sparkles,
  FileText, Code, Search, ShieldCheck, Terminal
} from 'lucide-react';

const initialAgents = [
  { id: 1, name: 'Planner Agent', desc: 'Analyzing goal and breaking into sub-tasks' },
  { id: 2, name: 'Research Agent', desc: 'Gathering context and data' },
  { id: 3, name: 'Developer Agent', desc: 'Executing core tasks and generating code' },
  { id: 4, name: 'Reviewer Agent', desc: 'Validating output and checking quality' },
  { id: 5, name: 'Reporter Agent', desc: 'Compiling final structured response' }
];

export default function App() {
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [agents, setAgents] = useState(initialAgents);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);

  const updateAgentStatus = (index, status, logMsg) => {
    setAgents(prev => prev.map((agent, i) => i === index ? { ...agent, status } : agent));
    if (logMsg) {
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${logMsg}`]);
    }
  };

  const handleSolve = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setResult(null);
    setLogs([]);
    setProgress(10);

    // Reset agents
    setAgents(initialAgents.map(a => ({ ...a, status: 'pending' })));
    updateAgentStatus(0, 'in_progress', 'Planner Agent started analyzing the goal');

    try {
      // Step 1: Submit task to backend
      const solveRes = await axios.post('http://127.0.0.1:8000/solve', { goal });
      const sessionId = solveRes.data.session_id;
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Task accepted. Session ID: ${sessionId}`]);

      // Step 2: Poll status until completion
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await axios.get(`http://127.0.0.1:8000/solve/${sessionId}`);
          const { status, current_agent, progress: serverProgress, result: finalResult } = statusRes.data;

          setProgress(serverProgress > 0 ? serverProgress : 20);

          if (current_agent === 'Planner') {
            updateAgentStatus(0, 'in_progress', 'Planner Agent forming execution plan');
          } else if (current_agent === 'Decomposer') {
            updateAgentStatus(0, 'completed');
            updateAgentStatus(1, 'in_progress', 'Decomposer Agent breaking into sub-tasks');
          } else if (current_agent === 'Researcher') {
            updateAgentStatus(1, 'completed');
            updateAgentStatus(2, 'in_progress', 'Researcher Agent gathering technical specs');
          } else if (current_agent === 'Developer') {
            updateAgentStatus(2, 'completed');
            updateAgentStatus(3, 'in_progress', 'Developer Agent generating production code');
          } else if (current_agent === 'Evaluator' || status === 'completed') {
            updateAgentStatus(3, 'completed');
            updateAgentStatus(4, 'completed', 'Evaluator Agent verifying final response');
          }

          if (status === 'completed' || status === 'failed') {
            clearInterval(pollInterval);
            setProgress(100);
            setResult(finalResult || 'Multi-Agent pipeline execution finished.');
            setLoading(false);
          }
        } catch (err) {
          console.error('Error polling status:', err);
        }
      }, 800);

    } catch (error) {
      console.error("Error connecting to backend:", error);
      setLogs(prev => [...prev, `[ERROR] Failed to reach backend: ${error.message}`]);
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 rounded-lg text-white">
            <Bot size={24} />
          </div>
          <div>
            <h1 className="font-bold text-xl tracking-wide bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              AgentForge AI
            </h1>
            <p className="text-xs text-slate-400">Autonomous Multi-Agent Orchestration Engine</p>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Input & Agents Panel */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          
          {/* Goal Input Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
            <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
              <Sparkles size={16} className="text-indigo-400" /> Enter Your Goal / Task
            </label>
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g., Create a strategy to build a React and FastAPI microservice app..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-200 resize-none h-28"
            />
            <button
              onClick={handleSolve}
              disabled={loading || !goal.trim()}
              className="mt-3 w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" /> Processing Goal...
                </>
              ) : (
                'Start Agents / Solve'
              )}
            </button>
          </div>

          {/* Agents Pipeline */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex-1">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                <Bot size={16} className="text-cyan-400" /> Active Agents Pipeline
              </h2>
              <span className="text-xs font-mono text-indigo-400">{progress}%</span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-950 rounded-full h-1.5 mb-5 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-1.5 transition-all duration-500" 
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="space-y-3">
              {agents.map((agent) => (
                <div 
                  key={agent.id} 
                  className={`p-3 rounded-lg border text-xs flex items-center justify-between transition ${
                    agent.status === 'in_progress' 
                      ? 'border-indigo-500/50 bg-indigo-950/20' 
                      : agent.status === 'completed'
                      ? 'border-emerald-500/30 bg-emerald-950/10'
                      : 'border-slate-800 bg-slate-950/50 opacity-60'
                  }`}
                >
                  <div>
                    <div className="font-semibold text-slate-200">{agent.name}</div>
                    <div className="text-slate-400 text-[11px]">{agent.desc}</div>
                  </div>
                  <div>
                    {agent.status === 'in_progress' && <Loader2 size={16} className="animate-spin text-indigo-400" />}
                    {agent.status === 'completed' && <CheckCircle2 size={16} className="text-emerald-400" />}
                    {(!agent.status || agent.status === 'pending') && <Clock size={16} className="text-slate-600" />}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Execution Logs & Final AI Output */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          
          {/* Output Display */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex-1 flex flex-col">
            <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <Sparkles size={16} className="text-indigo-400" /> AgentForge AI Multi-Agent Generated Output
            </h2>
            
            <div className="min-h-[300px] flex-1 border border-slate-800 rounded-lg p-4 bg-slate-950 overflow-y-auto">
              <AnimatePresence mode="wait">
                {result ? (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-slate-200 font-sans whitespace-pre-wrap leading-relaxed"
                  >
                    {result}
                  </motion.div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-slate-500 text-center py-12">
                    <Bot size={40} className="mb-2 text-slate-700 animate-pulse" />
                    <p className="text-sm font-medium text-slate-400">Final report will appear here</p>
                    <p className="text-xs text-slate-600 max-w-xs mt-1">
                      Enter your goal and hit solve to see real-time AI generation.
                    </p>
                  </div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Terminal Console Logs */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-2 mb-2 text-xs font-mono text-slate-400">
              <Terminal size={14} className="text-indigo-400" /> Execution Logs
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-xs text-slate-400 h-28 overflow-y-auto space-y-1">
              {logs.length === 0 ? (
                <span className="text-slate-600 italic">No logs yet. Waiting for command...</span>
              ) : (
                logs.map((log, index) => <div key={index}>{log}</div>)
              )}
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}