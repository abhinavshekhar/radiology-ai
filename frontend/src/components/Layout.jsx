import { NavLink, Outlet } from 'react-router-dom'

import MeshBackground from './MeshBackground'

import ChatAssistant from './ChatAssistant'
import { useStudyChat } from '../context/StudyChatContext'



export default function Layout({ user, onLogout }) {
  const { studyContext } = useStudyChat()

  const navClass = ({ isActive }) =>

    `px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${

      isActive

        ? 'bg-gradient-to-r from-cyan-500/15 to-violet-500/15 text-cyan-700 border border-cyan-300/50 shadow-sm'

        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent'

    }`



  return (

    <div className="min-h-screen relative">

      <MeshBackground />



      <header className="glass-nav sticky top-0 z-50 animate-fade-in">

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="flex items-center justify-between h-16 gap-4">

            <div className="flex items-center gap-3">

              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center shadow-md">

                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">

                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}

                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" />

                </svg>

              </div>

              <div>

                <h1 className="text-lg font-display font-bold text-slate-900">Radiology AI</h1>

                <p className="text-[10px] uppercase tracking-widest text-cyan-600">Clinical CDS</p>

              </div>

            </div>



            <nav className="hidden md:flex items-center gap-1">

              <NavLink to="/" className={navClass} end>Dashboard</NavLink>

              <NavLink to="/analyze" className={navClass}>Analyze</NavLink>

              <NavLink to="/patients" className={navClass}>Patients</NavLink>

              <NavLink to="/history" className={navClass}>History</NavLink>

              {(user.role === 'admin' || user.role === 'radiologist') && (

                <NavLink to="/audit" className={navClass}>Audit</NavLink>

              )}

            </nav>



            <div className="flex items-center gap-3">

              <div className="text-right hidden sm:block">

                <p className="text-sm font-medium text-slate-900">{user.full_name}</p>

                <p className="text-xs text-slate-500 capitalize">{user.role}</p>

              </div>

              <button onClick={onLogout} className="btn-secondary text-sm">Logout</button>

            </div>

          </div>

        </div>

      </header>



      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">

        <Outlet />

      </main>



      <ChatAssistant studyContext={studyContext} />

    </div>

  )

}


