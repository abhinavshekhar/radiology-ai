import { useState } from 'react'

import { auth } from '../api'

import MeshBackground from '../components/MeshBackground'
import ChatAssistant from '../components/ChatAssistant'



const DEMO_ACCOUNTS = [

  { email: 'doctor@radiology.ai', role: 'Doctor', desc: 'Upload & analyze scans', icon: '🩺' },

  { email: 'radiologist@radiology.ai', role: 'Radiologist', desc: 'Full access + audit logs', icon: '🔬' },

  { email: 'admin@radiology.ai', role: 'Admin', desc: 'System administration', icon: '⚙️' },

]



const FEATURES = ['DenseNet121 AI', 'Grad-CAM', '12+ Diagnoses', 'DICOM + PACS', 'PDF Reports']



export default function Login({ onLogin }) {

  const [email, setEmail] = useState('doctor@radiology.ai')

  const [password, setPassword] = useState('demo1234')

  const [error, setError] = useState('')

  const [loading, setLoading] = useState(false)



  const handleSubmit = async (e) => {

    e.preventDefault()

    setLoading(true)

    setError('')

    try {

      const { data } = await auth.login(email, password)

      localStorage.setItem('token', data.access_token)

      const me = await auth.me()

      onLogin(data.access_token, me.data)

    } catch {

      setError('Invalid credentials')

    } finally {

      setLoading(false)

    }

  }



  const quickLogin = (account) => {

    setEmail(account.email)

    setPassword('demo1234')

  }



  return (

    <div className="min-h-screen relative flex items-center justify-center p-4">

      <MeshBackground />



      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-10 items-center relative z-10">

        <div className="space-y-8 animate-fade-in-up hidden lg:block">

          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-200 bg-cyan-50 text-cyan-700 text-xs font-medium">

            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />

            SIH 2026 · HealthTech

          </div>



          <div>

            <h1 className="text-5xl font-display font-bold text-slate-900 leading-tight">

              Radiology

              <span className="block bg-gradient-to-r from-cyan-600 via-violet-600 to-pink-600 bg-clip-text text-transparent">

                AI Assistant

              </span>

            </h1>

            <p className="text-slate-600 text-lg mt-4 max-w-md leading-relaxed">

              Explainable multi-modality clinical decision support with transparent AI insights.

            </p>

          </div>



          <div className="flex flex-wrap gap-2">

            {FEATURES.map((f, i) => (

              <span

                key={f}

                className="px-3 py-1.5 rounded-xl text-sm text-slate-600 border border-slate-200 bg-white/70 backdrop-blur-sm shadow-sm"

                style={{ animationDelay: `${i * 80}ms` }}

              >

                {f}

              </span>

            ))}

          </div>

        </div>



        <div className="card card-glow animate-fade-in-up lg:stagger-2">

          <div className="mb-8">

            <h2 className="text-2xl font-display font-bold text-slate-900">Welcome back</h2>

            <p className="text-slate-500 text-sm mt-1">Sign in to your clinical workspace</p>

          </div>



          <form onSubmit={handleSubmit} className="space-y-5">

            <div>

              <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>

              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" required />

            </div>

            <div>

              <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>

              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" required />

            </div>

            {error && (

              <p className="text-rose-600 text-sm bg-rose-50 border border-rose-200 rounded-xl px-4 py-2">{error}</p>

            )}

            <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 text-base">

              {loading ? (

                <span className="flex items-center justify-center gap-2">

                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />

                  Signing in...

                </span>

              ) : 'Sign In →'}

            </button>

          </form>



          <div className="mt-8 pt-6 border-t border-slate-200">

            <p className="text-xs text-slate-500 mb-4 font-medium uppercase tracking-widest">Quick Demo Login</p>

            <div className="space-y-2">

              {DEMO_ACCOUNTS.map((acc) => (

                <button

                  key={acc.email}

                  onClick={() => quickLogin(acc)}

                  className="w-full text-left p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white hover:border-cyan-300 transition-all duration-300 group"

                >

                  <div className="flex justify-between items-center">

                    <span className="font-medium text-sm text-slate-800 flex items-center gap-2">

                      <span className="text-lg">{acc.icon}</span>

                      {acc.role}

                    </span>

                    <span className="text-xs text-slate-400 group-hover:text-cyan-600 transition-colors">demo1234</span>

                  </div>

                  <p className="text-xs text-slate-500 mt-1 ml-7">{acc.desc}</p>

                </button>

              ))}

            </div>

          </div>

        </div>

      </div>

      <ChatAssistant />
    </div>

  )

}


