import { useEffect, useState } from 'react'

import { pacs } from '../api'



export default function PacsPanel() {

  const [status, setStatus] = useState(null)

  const [patients, setPatients] = useState([])



  useEffect(() => {

    pacs.status().then((r) => setStatus(r.data)).catch(() =>

      setStatus({ connected: false, message: 'PACS service unavailable' })

    )

    pacs.patients().then((r) => setPatients(r.data || [])).catch(() => {})

  }, [])



  return (

    <div className="card card-glow">

      <div className="flex items-center justify-between mb-4">

        <h3 className="font-display font-semibold text-slate-900">Orthanc PACS Integration</h3>

        <div className="flex items-center gap-2">

          <div className={`w-2.5 h-2.5 rounded-full ${status?.connected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />

          <span className="text-sm font-medium text-slate-600">{status?.connected ? 'Connected' : 'Offline'}</span>

        </div>

      </div>

      <p className="text-sm text-slate-500 mb-3">{status?.message}</p>

      {status?.connected && (

        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 text-sm text-emerald-800">

          DICOM uploads are automatically synced to Orthanc PACS.

          {patients.length > 0 && ` ${patients.length} patient(s) in PACS.`}

        </div>

      )}

      {!status?.connected && (

        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-800">

          Start PACS: <code className="bg-amber-100 px-1.5 py-0.5 rounded text-xs">docker compose --profile pacs up -d</code>

          <br />Orthanc UI: <a href="http://localhost:8042" target="_blank" rel="noreferrer"

            className="underline text-cyan-700">localhost:8042</a> (login: <code className="bg-amber-100 px-1 rounded">orthanc</code> / <code className="bg-amber-100 px-1 rounded">orthanc</code>)

        </div>

      )}

    </div>

  )

}


