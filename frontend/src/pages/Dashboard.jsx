import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { Doughnut, Bar } from 'react-chartjs-2'
import { dashboard } from '../api'
import PacsPanel from '../components/PacsPanel'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

const chartDefaults = {
  plugins: { legend: { labels: { color: '#64748b' } } },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(15,23,42,0.06)' } },
    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(15,23,42,0.06)' } },
  },
}

function MetricCard({ label, value, sub, gradient, delay = '' }) {
  return (
    <div className={`card card-glow ${delay}`}>
      <div className={`absolute top-0 right-0 w-28 h-28 rounded-full blur-2xl opacity-30 -mr-6 -mt-6 bg-gradient-to-br ${gradient}`} />
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="text-4xl font-display font-bold text-slate-900 mt-2">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-2">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    dashboard.metrics().then((r) => setMetrics(r.data)).catch(() => setMetrics({
      total_studies: 0, total_patients: 0, pneumonia_cases: 0,
      normal_cases: 0, avg_confidence: 0, needs_review_count: 0,
    }))
    dashboard.history().then((r) => setHistory(r.data.slice(0, 5))).catch(() => {})
  }, [])

  if (!metrics) {
    return (
      <div className="flex justify-center py-24">
        <div className="w-12 h-12 rounded-full border-2 border-cyan-200 border-t-cyan-600 animate-spin" />
      </div>
    )
  }

  const pieData = {
    labels: ['Pneumonia', 'Normal', 'Other'],
    datasets: [{
      data: [metrics.pneumonia_cases, metrics.normal_cases,
        Math.max(0, metrics.total_studies - metrics.pneumonia_cases - metrics.normal_cases)],
      backgroundColor: ['rgba(244,63,94,0.8)', 'rgba(52,211,153,0.8)', 'rgba(148,163,184,0.6)'],
      borderWidth: 0,
    }],
  }

  const confidenceData = {
    labels: history.map((h) => h.patient_name.split(' ')[0]),
    datasets: [{
      label: 'Confidence %',
      data: history.map((h) => (h.confidence * 100).toFixed(1)),
      backgroundColor: 'rgba(34, 211, 238, 0.6)',
      borderRadius: 8,
      borderSkipped: false,
    }],
  }

  return (
    <div className="space-y-8">
      <div className="hero-glass stagger-1">
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-float" />
        <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <p className="text-cyan-600 text-xs font-semibold uppercase tracking-[0.2em]">Clinical AI</p>
            <h2 className="text-4xl font-display font-bold text-slate-900 mt-2">Radiology AI Assistant</h2>
            <p className="text-slate-600 mt-3 max-w-lg leading-relaxed">
              Explainable chest X-ray analysis with Grad-CAM, differential diagnosis,
              and auto-generated radiology reports.
            </p>
          </div>
          <Link to="/analyze" className="btn-primary inline-flex items-center gap-2 px-8 py-4 self-start text-base">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Start Analysis
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Total Studies" value={metrics.total_studies} gradient="from-cyan-400 to-blue-500" delay="stagger-2" />
        <MetricCard label="Patients" value={metrics.total_patients} gradient="from-emerald-400 to-teal-500" delay="stagger-3" />
        <MetricCard label="Avg Confidence" value={`${(metrics.avg_confidence * 100).toFixed(1)}%`} gradient="from-amber-400 to-orange-500" delay="stagger-4" />
        <MetricCard label="Needs Review" value={metrics.needs_review_count} sub="Low confidence" gradient="from-rose-400 to-pink-500" delay="stagger-5" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card animate-fade-in-up">
          <h3 className="font-display font-semibold text-slate-900 mb-4">Finding Distribution</h3>
          <div className="h-56 flex items-center justify-center">
            {metrics.total_studies > 0 ? (
              <Doughnut data={pieData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } } }} />
            ) : (
              <div className="text-center text-slate-500">
                <p>No studies yet</p>
                <Link to="/analyze" className="text-cyan-600 text-sm hover:underline mt-2 inline-block">Run your first analysis →</Link>
              </div>
            )}
          </div>
        </div>
        <div className="card animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <h3 className="font-display font-semibold text-slate-900 mb-4">Confidence Scores</h3>
          <div className="h-56">
            {history.length > 0 ? (
              <Bar data={confidenceData} options={{
                ...chartDefaults,
                maintainAspectRatio: false,
                scales: { ...chartDefaults.scales, y: { ...chartDefaults.scales.y, max: 100, ticks: { ...chartDefaults.scales.y.ticks, callback: (v) => v + '%' } } },
                plugins: { legend: { display: false } },
              }} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">No data yet</div>
            )}
          </div>
        </div>
      </div>

      <PacsPanel />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { title: 'X-Ray MVP', desc: 'DenseNet121 pneumonia + 12 chest findings with Grad-CAM', icon: '🫁', color: 'from-cyan-500/20 to-blue-500/10' },
          { title: 'CT / MRI / US', desc: 'Multi-modality pipelines for nodules, tumors, BI-RADS', icon: '🧠', color: 'from-violet-500/20 to-purple-500/10' },
          { title: 'PACS + FHIR', desc: 'Orthanc, DICOMweb, HL7 FHIR integration', icon: '🏥', color: 'from-pink-500/20 to-rose-500/10' },
        ].map((f, i) => (
          <div key={f.title} className={`card card-glow text-center bg-gradient-to-br ${f.color}`} style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="text-4xl mb-3 animate-float" style={{ animationDelay: `${i * 0.5}s` }}>{f.icon}</div>
            <h4 className="font-display font-semibold text-slate-900">{f.title}</h4>
            <p className="text-sm text-slate-600 mt-2">{f.desc}</p>
          </div>
        ))}
      </div>

      {history.length > 0 && (
        <div className="card animate-fade-in-up">
          <h3 className="font-display font-semibold text-slate-900 mb-4">Recent Studies</h3>
          <table className="w-full text-sm table-glass">
            <thead>
              <tr>
                <th className="pb-3 text-left">Patient</th>
                <th className="pb-3 text-left">Finding</th>
                <th className="pb-3 text-left">Confidence</th>
                <th className="pb-3 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.study_id}>
                  <td className="py-3 font-medium text-slate-800">{h.patient_name}</td>
                  <td className="py-3">
                    <span className={h.primary_label === 'Normal' ? 'badge-success' : 'badge-danger'}>
                      {h.primary_label}
                    </span>
                  </td>
                  <td className="py-3 text-slate-600">{(h.confidence * 100).toFixed(1)}%</td>
                  <td className="py-3 text-slate-500">{new Date(h.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
