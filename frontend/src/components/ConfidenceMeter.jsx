export default function ConfidenceMeter({ confidence }) {

  const pct = Math.round(confidence * 1000) / 10

  const gradient = confidence >= 0.85

    ? 'from-emerald-400 to-teal-500'

    : confidence >= 0.65

    ? 'from-amber-400 to-orange-500'

    : 'from-rose-400 to-pink-500'



  return (

    <div>

      <div className="flex justify-between text-sm mb-2">

        <span className="text-slate-500">AI Confidence</span>

        <span className="font-display font-bold text-slate-900">{pct}%</span>

      </div>

      <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden border border-slate-200">

        <div

          className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all duration-1000 ease-out`}

          style={{ width: `${pct}%` }}

        />

      </div>

    </div>

  )

}


