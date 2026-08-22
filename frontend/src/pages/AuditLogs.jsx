import { useEffect, useState } from 'react'
import { dashboard, pacs } from '../api'

export default function AuditLogs() {
  const [logs, setLogs] = useState([])
  const [pacsStatus, setPacsStatus] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    dashboard.auditLogs()
      .then((r) => setLogs(r.data))
      .catch(() => setError('Audit logs require admin or radiologist role'))
    pacs.status().then((r) => setPacsStatus(r.data)).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="page-title">Audit & PACS</h2>
        <p className="page-subtitle">Security audit trail and PACS integration status</p>
      </div>

      {pacsStatus && (
        <div className={`card ${pacsStatus.connected ? 'border-emerald-300 bg-emerald-50' : 'border-amber-300 bg-amber-50'}`}>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${pacsStatus.connected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <div>
              <p className="font-semibold text-slate-900">Orthanc PACS — {pacsStatus.connected ? 'Connected' : 'Offline'}</p>
              <p className="text-sm text-slate-600">{pacsStatus.message}</p>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="font-display font-semibold text-slate-900 mb-4">Audit Logs</h3>
        {error ? (
          <p className="text-amber-700 text-sm">{error}</p>
        ) : logs.length === 0 ? (
          <p className="text-slate-500 text-sm">No audit logs yet</p>
        ) : (
          <table className="w-full text-sm table-glass">
            <thead>
              <tr>
                <th className="pb-2 text-left">Time</th>
                <th className="pb-2 text-left">User</th>
                <th className="pb-2 text-left">Action</th>
                <th className="pb-2 text-left">Resource</th>
                <th className="pb-2 text-left">Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="py-2 text-slate-500">{new Date(log.created_at).toLocaleString()}</td>
                  <td className="py-2">
                    <span className="font-medium text-slate-800">{log.user}</span>
                    {log.role && <span className="text-xs text-slate-500 ml-1">({log.role})</span>}
                  </td>
                  <td className="py-2">
                    <span className="badge">{log.action}</span>
                  </td>
                  <td className="py-2 text-slate-400">{log.resource_type} #{log.resource_id}</td>
                  <td className="py-2 text-slate-500">{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
