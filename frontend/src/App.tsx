import { useState } from 'react';
import { Send, Shield, Zap, Terminal, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

type Trace = { node: string; content: string };
type Message = { role: 'user' | 'ai'; content: string; traces?: Trace[]; isFinal?: boolean };

export default function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: 'Welcome to SafeSurface. Enter a target URL or IP to begin the autonomous penetration test.', isFinal: true, traces: [] }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTraceIdx, setExpandedTraceIdx] = useState<number | null>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg = input;
    setInput('');
    // 加入用户发的消息，同时先丢入一条给AI的初始等待框
    setMessages(prev => [...prev, 
      { role: 'user', content: userMsg },
      { role: 'ai', content: '', traces: [], isFinal: false }
    ]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg })
      });

      if (!res.body) throw new Error('No body returned from server');
      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            setMessages(prev => {
              const newMsgs = [...prev];
              const lastIdx = newMsgs.length - 1;
              const currentAiMsg = newMsgs[lastIdx];

              if (data.type === 'trace') {
                currentAiMsg.traces = [
                  ...(currentAiMsg.traces || []),
                  { node: data.node, content: data.content }
                ];
              } else if (data.type === 'final') {
                currentAiMsg.content = data.content;
                currentAiMsg.isFinal = true;
              } else if (data.type === 'error') {
                currentAiMsg.content = `Server Error: ${data.content}`;
                currentAiMsg.isFinal = true;
              }
              return newMsgs;
            });
          }
        }
      }
    } catch (err) {
      setMessages(prev => {
        const newMsgs = [...prev];
        const lastIdx = newMsgs.length - 1;
        newMsgs[lastIdx].content = 'Simulation Error: Connection to Master Planner failed.';
        newMsgs[lastIdx].isFinal = true;
        return newMsgs;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTrace = (idx: number) => {
    setExpandedTraceIdx(prev => prev === idx ? null : idx);
  };

  return (
    <div className="min-h-screen flex flex-col p-6 max-w-5xl mx-auto">
      {/* Header */}
      <header className="flex items-center gap-3 mb-8 px-2">
        <div className="p-2 bg-black rounded-xl text-white">
          <Shield size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">SafeSurface</h1>
          <p className="text-sm text-gray-500 font-medium">Autonomous Pentesting Agent</p>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="flex-1 glass-panel flex flex-col overflow-hidden mb-6 relative">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div 
                className={`max-w-[85%] rounded-2xl px-5 py-4 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'bg-white shadow-sm border border-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-center gap-2 mb-2 opacity-80">
                  {msg.role === 'ai' && <Terminal size={14} />}
                  <span className="text-xs font-semibold uppercase tracking-wider">
                    {msg.role === 'ai' ? 'Master Planner' : 'You'}
                  </span>
                </div>

                {/* Traces Block / 思考过程 */}
                {msg.traces && msg.traces.length > 0 && (
                  <div className="mb-3">
                    <button 
                      onClick={() => toggleTrace(idx)}
                      className="flex items-center gap-2 text-xs font-medium text-gray-500 hover:text-gray-700 bg-gray-50 px-3 py-1.5 rounded-lg w-full transition-colors"
                    >
                      {!msg.isFinal && <Zap className="animate-pulse text-blue-500" size={14} />}
                      {msg.isFinal ? <span>View Chain of Thought ({msg.traces.length} steps)</span> : <span>Thinking...</span>}
                      {expandedTraceIdx === idx ? <ChevronUp size={14} className="ml-auto" /> : <ChevronDown size={14} className="ml-auto" />}
                    </button>
                    
                    {(expandedTraceIdx === idx || !msg.isFinal) && (
                      <div className="mt-2 pl-2 space-y-2 border-l-2 border-gray-200">
                        {msg.traces.map((t, tIdx) => (
                          <div key={tIdx} className="flex gap-2 text-xs text-gray-600">
                            <CheckCircle2 size={14} className="text-green-500 mt-0.5 shrink-0" />
                            <div>
                              <span className="font-semibold text-gray-700 capitalize">[{t.node}]</span> {t.content}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Final Content */}
                <p className="leading-relaxed whitespace-pre-wrap mt-2">{msg.content}</p>
                {msg.role === 'ai' && !msg.isFinal && msg.traces?.length === 0 && (
                   <div className="flex gap-2 items-center text-sm text-gray-400 mt-2">
                     <Zap className="animate-pulse" size={16} /> Connecting to Agents...
                   </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-100/50 bg-white/50">
          <div className="relative flex items-center">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Deploy agents to target: e.g. http://192.168.1.100..."
              className="w-full bg-white/80 border border-gray-200 rounded-xl py-4 pl-4 pr-12 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
              disabled={isLoading}
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="absolute right-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
