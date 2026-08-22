export default function DifferentialList({ items }) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={item.condition} className="flex items-center gap-3">
          <span className="text-xs text-slate-400 w-4">{i + 1}</span>
          <div className="flex-1">
            <div className="flex justify-between text-sm mb-0.5">
              <span className="font-medium text-slate-700">{item.condition}</span>
              <span className="text-slate-500">{(item.probability * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-clinical-500 rounded-full"
                style={{ width: `${item.probability * 100}%` }} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
