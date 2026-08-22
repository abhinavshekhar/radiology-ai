const STEPS = [

  { id: 1, label: 'Preprocessing', desc: 'CLAHE, denoise, normalize' },

  { id: 2, label: 'AI Inference', desc: 'DenseNet121 analysis' },

  { id: 3, label: 'Grad-CAM', desc: 'Generating heatmap' },

  { id: 4, label: 'Report', desc: 'Clinical findings' },

  { id: 5, label: 'Complete', desc: 'Results ready' },

]



export default function PipelineSteps({ currentStep }) {

  return (

    <div className="card bg-gradient-to-r from-cyan-50 to-violet-50 border-cyan-200 animate-fade-in-up">

      <div className="flex items-center justify-between gap-2 overflow-x-auto pb-1">

        {STEPS.map((step, i) => {

          const done = currentStep >= step.id

          const active = currentStep === step.id

          return (

            <div key={step.id} className="flex items-center gap-2 flex-1 min-w-0">

              <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold transition-all duration-500 ${

                done ? 'bg-gradient-to-br from-cyan-500 to-violet-500 text-white shadow-md scale-105' :

                active ? 'bg-cyan-100 text-cyan-700 border border-cyan-300 animate-pulse' :

                'bg-slate-100 text-slate-400 border border-slate-200'

              }`}>

                {done && currentStep > step.id ? '✓' : step.id}

              </div>

              <div className="min-w-0 hidden sm:block">

                <p className={`text-sm font-medium truncate ${done ? 'text-cyan-700' : 'text-slate-500'}`}>

                  {step.label}

                </p>

                <p className="text-xs text-slate-400 truncate">{step.desc}</p>

              </div>

              {i < STEPS.length - 1 && (

                <div className={`flex-1 h-0.5 mx-1 rounded-full transition-all duration-500 ${

                  done ? 'bg-gradient-to-r from-cyan-400 to-violet-500' : 'bg-slate-200'

                }`} />

              )}

            </div>

          )

        })}

      </div>

    </div>

  )

}


