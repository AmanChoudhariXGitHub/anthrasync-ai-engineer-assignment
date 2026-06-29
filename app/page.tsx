'use client'

import { ExternalLink, BookOpen, Play, Code2, Database, Zap } from 'lucide-react'
import { useState } from 'react'

export default function Page() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <Database size={18} className="text-white" />
            </div>
            <h1 className="text-xl font-bold">Enterprise Knowledge Assistant</h1>
          </div>
          <a
            href="https://github.com/AmanChoudhariXGitHub/anthrasync-ai-engineer-assignment"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition"
          >
            <ExternalLink size={18} />
            GitHub
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl lg:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Production-Ready RAG System
            </h2>
            <p className="text-lg text-slate-300 mb-8">
              Enterprise knowledge assistant powered by Groq's free LLM APIs, ChromaDB vector storage, and semantic search. Zero cost, maximum capability.
            </p>
            <div className="flex flex-wrap gap-4">
              <a
                href="#quick-start"
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition transform hover:scale-105"
              >
                Get Started
              </a>
              <a
                href="https://console.groq.com"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 bg-slate-800 rounded-lg font-semibold hover:bg-slate-700 transition"
              >
                Get Groq API Key
              </a>
            </div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8 backdrop-blur-sm">
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg">
                <Zap className="text-yellow-400" size={24} />
                <div>
                  <p className="font-semibold">Lightning Fast</p>
                  <p className="text-sm text-slate-400">Sub-second token generation</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg">
                <Code2 className="text-blue-400" size={24} />
                <div>
                  <p className="font-semibold">API First</p>
                  <p className="text-sm text-slate-400">6 REST endpoints + Swagger docs</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg">
                <Database className="text-cyan-400" size={24} />
                <div>
                  <p className="font-semibold">Semantic Search</p>
                  <p className="text-sm text-slate-400">ChromaDB + Sentence Transformers</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tabs Section */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex gap-4 mb-8 border-b border-slate-800 overflow-x-auto">
          {[
            { id: 'overview', label: 'Overview', icon: BookOpen },
            { id: 'features', label: 'Features', icon: Zap },
            { id: 'setup', label: 'Quick Start', icon: Play },
            { id: 'resources', label: 'Resources', icon: Code2 },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 font-semibold whitespace-nowrap border-b-2 transition ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-6 backdrop-blur-sm">
              <h3 className="text-xl font-bold mb-4 text-cyan-400">System Overview</h3>
              <p className="text-slate-300 mb-4">
                The Enterprise Knowledge Assistant is a production-grade Retrieval-Augmented Generation (RAG) system designed for enterprise document analysis and question answering.
              </p>
              <div className="grid md:grid-cols-3 gap-4 mt-6">
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                  <p className="font-semibold text-blue-400">3,500+ Lines</p>
                  <p className="text-sm text-slate-400">Production-grade code</p>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                  <p className="font-semibold text-cyan-400">4,500+ Lines</p>
                  <p className="text-sm text-slate-400">Comprehensive documentation</p>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                  <p className="font-semibold text-purple-400">$0 Cost</p>
                  <p className="text-sm text-slate-400">Free Groq LLM tier</p>
                </div>
              </div>
            </div>

            <div className="bg-slate-800/30 border border-slate-700 rounded-xl p-6 backdrop-blur-sm">
              <h3 className="text-xl font-bold mb-4 text-cyan-400">Technology Stack</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="font-semibold text-blue-400 mb-2">Backend</p>
                  <ul className="space-y-2 text-slate-300">
                    <li>• FastAPI (REST API)</li>
                    <li>• Groq LLM APIs</li>
                    <li>• ChromaDB (Vector Store)</li>
                    <li>• Sentence Transformers</li>
                  </ul>
                </div>
                <div>
                  <p className="font-semibold text-cyan-400 mb-2">Frontend</p>
                  <ul className="space-y-2 text-slate-300">
                    <li>• Streamlit Web UI</li>
                    <li>• Next.js Landing</li>
                    <li>• Real-time Chat</li>
                    <li>• Evaluation Dashboard</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Features Tab */}
        {activeTab === 'features' && (
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                title: 'Document Processing',
                desc: 'PDF, DOCX, TXT with intelligent chunking',
                icon: '📄',
              },
              {
                title: 'Semantic Search',
                desc: '384-dim embeddings with similarity scoring',
                icon: '🔍',
              },
              {
                title: 'LLM Generation',
                desc: 'Groq API with automatic model fallback',
                icon: '🧠',
              },
              {
                title: 'Source Attribution',
                desc: 'Answers include source documents',
                icon: '📚',
              },
              {
                title: 'REST API',
                desc: '6 production endpoints with Swagger docs',
                icon: '🔌',
              },
              {
                title: 'Evaluation',
                desc: 'BLEU, ROUGE, token overlap metrics',
                icon: '📊',
              },
              {
                title: 'Web UI',
                desc: 'Streamlit interface with real-time feedback',
                icon: '🎨',
              },
              {
                title: 'Scalable',
                desc: 'Horizontal scaling ready architecture',
                icon: '📈',
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="bg-slate-800/30 border border-slate-700 rounded-xl p-6 backdrop-blur-sm hover:border-cyan-500/50 transition"
              >
                <p className="text-3xl mb-3">{feature.icon}</p>
                <h4 className="font-semibold text-cyan-400 mb-2">{feature.title}</h4>
                <p className="text-slate-300 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        )}

        {/* Quick Start Tab */}
        {activeTab === 'setup' && (
          <div id="quick-start" className="space-y-6">
            <div className="bg-gradient-to-r from-blue-900/20 to-cyan-900/20 border border-cyan-500/30 rounded-xl p-8 backdrop-blur-sm">
              <h3 className="text-2xl font-bold mb-6 text-cyan-400">Quick Start (10 Minutes)</h3>
              
              <div className="space-y-6">
                {[
                  {
                    step: '1',
                    title: 'Get Groq API Key',
                    time: '2 min',
                    desc: 'Visit console.groq.com, sign up (no credit card), create API key',
                  },
                  {
                    step: '2',
                    title: 'Configure Project',
                    time: '3 min',
                    desc: 'Clone repo, add GROQ_API_KEY to .env, install dependencies',
                  },
                  {
                    step: '3',
                    title: 'Start System',
                    time: '2 min',
                    desc: 'Run FastAPI backend and Streamlit UI in separate terminals',
                  },
                  {
                    step: '4',
                    title: 'Start Using',
                    time: '1 min',
                    desc: 'Upload documents, ask questions, evaluate answers',
                  },
                ].map((item, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center font-bold flex-shrink-0">
                      {item.step}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-lg">{item.title}</h4>
                        <span className="text-sm text-slate-400">{item.time}</span>
                      </div>
                      <p className="text-slate-300">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                <p className="font-mono text-sm">
                  <span className="text-cyan-400"># Clone repository</span>
                  <br />
                  git clone &lt;repo-url&gt;
                  <br />
                  <br />
                  <span className="text-cyan-400"># Configure</span>
                  <br />
                  echo &quot;GROQ_API_KEY=your_key&quot; &gt; .env
                  <br />
                  pip install -r requirements.txt
                  <br />
                  <br />
                  <span className="text-cyan-400"># Run</span>
                  <br />
                  ./run.sh
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Resources Tab */}
        {activeTab === 'resources' && (
          <div className="space-y-4">
            {[
              {
                name: 'Quick Start Guide',
                desc: '5-minute setup to running system',
                file: 'QUICK_START.md',
              },
              {
                name: 'Complete Setup Guide',
                desc: 'Detailed installation with troubleshooting',
                file: 'SETUP.md',
              },
              {
                name: 'Groq Integration Guide',
                desc: 'API configuration and advanced options',
                file: 'GROQ_INTEGRATION_GUIDE.md',
              },
              {
                name: 'API Reference',
                desc: '6 REST endpoints with examples',
                file: 'API.md',
              },
              {
                name: 'Architecture Document',
                desc: 'System design and data flows',
                file: 'ARCHITECTURE.md',
              },
              {
                name: 'Video Script',
                desc: 'Professional 17-23 minute demo script',
                file: 'VIDEO_SCRIPT.md',
              },
              {
                name: 'Video Walkthrough',
                desc: 'Detailed step-by-step recording guide',
                file: 'VIDEO_WALKTHROUGH.md',
              },
              {
                name: 'Final Summary',
                desc: 'Complete project overview and status',
                file: 'FINAL_SUMMARY.txt',
              },
            ].map((resource, i) => (
              <div
                key={i}
                className="bg-slate-800/30 border border-slate-700 rounded-lg p-4 hover:border-cyan-500/50 transition flex items-start justify-between"
              >
                <div>
                  <h4 className="font-semibold text-cyan-400 mb-1">{resource.name}</h4>
                  <p className="text-sm text-slate-400">{resource.desc}</p>
                </div>
                <code className="text-xs bg-slate-900/50 px-3 py-1 rounded text-slate-300 whitespace-nowrap ml-4">
                  {resource.file}
                </code>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* CTA Section */}
      <section className="max-w-6xl mx-auto px-4 py-16 border-t border-slate-800">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Get Started?</h2>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            Get your Groq API key in 2 minutes and have the RAG system running in 10 minutes. Everything is documented and ready to deploy.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <a
              href="https://console.groq.com"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition transform hover:scale-105"
            >
              Get Groq API Key
            </a>
            <a
              href="https://github.com/AmanChoudhariXGitHub/anthrasync-ai-engineer-assignment"
              className="px-8 py-3 bg-slate-800 rounded-lg font-semibold hover:bg-slate-700 transition"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 mt-16">
        <div className="max-w-6xl mx-auto px-4 text-center text-slate-400">
          <p>Enterprise Knowledge Assistant • Production-Ready RAG System • Powered by Groq</p>
          <p className="text-sm mt-2">
            Built with FastAPI, Streamlit, ChromaDB, and Next.js
          </p>
        </div>
      </footer>
    </main>
  )
}
