/** Client-side radiology assistant — works even if API is unreachable. */

const TOPICS = [
  {
    keys: ['grad-cam', 'gradcam', 'heatmap', 'explain', 'explainability', 'why ai'],
    answer:
      'Grad-CAM highlights image regions that influenced the AI prediction. Warmer colors show where DenseNet121 focused when detecting findings like pneumonia. Generate a Grad-CAM overlay on the Analyze page after running inference.',
  },
  {
    keys: ['pneumonia', 'lung infection', 'consolidation'],
    answer:
      'Pneumonia on chest X-ray appears as airspace consolidation. Our AI uses DenseNet121 to screen for pneumonia and 12+ other chest pathologies. Always correlate with clinical symptoms — AI is decision support, not a final diagnosis.',
  },
  {
    keys: ['densnet', 'densenet', 'model', 'neural', 'deep learning', 'ai model', 'torch', 'how does ai work'],
    answer:
      'We use DenseNet121 pretrained on ChestX-ray14 (TorchXRayVision) for chest X-rays. CT, MRI, and Ultrasound use dedicated CV pipelines (nnU-Net, MONAI, MedSAM paths).',
  },
  {
    keys: ['confidence', 'score', 'threshold', 'review'],
    answer:
      'Confidence score is 0–100%. ≥85% is high confidence; 65–85% warrants review; below 65% is flagged as Needs Review on the dashboard.',
  },
  {
    keys: ['dicom', 'pacs', 'orthanc', 'dicomweb'],
    answer:
      'Orthanc PACS integrates via DICOMweb. Start with: docker compose --profile pacs up -d. Orthanc UI: http://localhost:8042 (orthanc / orthanc).',
  },
  {
    keys: ['ct', 'computed tomography', 'nodule', 'lung nodule'],
    answer: 'CT Chest analysis targets lung nodule detection. Select CT Chest on the Analyze page and upload a slice or use the demo case.',
  },
  {
    keys: ['mri', 'mr ', 'brain', 'tumor', 'brats'],
    answer: 'MRI Brain analysis focuses on tumor detection (BraTS / MONAI path). Select MRI Brain on the Analyze page.',
  },
  {
    keys: ['ultrasound', 'us ', 'breast', 'bi-rads', 'birads'],
    answer: 'Ultrasound breast analysis provides BI-RADS-style assessment. Select Ultrasound modality on Analyze.',
  },
  {
    keys: ['x-ray', 'xray', 'chest x', 'cxr', 'chest ray', 'chest'],
    answer:
      'Chest X-Ray is our MVP. Go to Analyze → X-Ray → upload or pick demo → Run AI Analysis. You get findings, Grad-CAM, differential, and PDF report.',
  },
  {
    keys: ['report', 'pdf', 'download'],
    answer: 'After analysis, click Generate PDF Report on the Analyze page for a structured radiology report you can download.',
  },
  {
    keys: ['upload', 'analyze', 'how to', 'use app', 'how do i', 'steps', 'workflow', 'start'],
    answer:
      'Workflow: Analyze → enter patient → pick modality → upload scan → Run AI Analysis → review findings & Grad-CAM → download PDF. Demo login: doctor@radiology.ai / demo1234',
  },
  {
    keys: ['patient', 'history', 'timeline'],
    answer: 'Patients page lists records. History shows all analyzed studies. Patient timelines track progression over time.',
  },
  {
    keys: ['normal', 'negative', 'no finding', 'healthy'],
    answer:
      'Normal means no significant pathology above threshold. Clinical correlation is still essential — subtle disease may be missed.',
  },
  {
    keys: ['login', 'password', 'demo', 'sign in', 'account'],
    answer: 'Demo accounts: doctor@radiology.ai, radiologist@radiology.ai, admin@radiology.ai — password: demo1234',
  },
  {
    keys: ['hello', 'hi', 'hey', 'help', 'start'],
    answer:
      "Hello! I'm your Radiology AI assistant. Ask about Grad-CAM, pneumonia, how to analyze scans, modalities (X-Ray/CT/MRI/US), reports, or PACS.",
  },
]

function normalize(text) {
  return text.toLowerCase().replace(/\s+/g, ' ').trim()
}

function replyFromStudy(text, ctx) {
  if (!ctx?.primary_label) return null
  const t = normalize(text)
  if (!/(this|my|result|finding|diagnosis|study|patient|mean|wrong|disease)/.test(t)) return null
  const pct = ctx.confidence != null ? Math.round(Number(ctx.confidence) * 1000) / 10 : null
  const conf = pct != null ? `${pct}%` : 'N/A'
  return `For the current study (${ctx.modality || 'XR'}): primary finding is ${ctx.primary_label} with ${conf} AI confidence. Review the Grad-CAM heatmap and correlate with clinical presentation before finalizing your impression.`
}

export function getLocalChatReply(message, studyContext = null) {
  const text = normalize(message)
  if (!text) return 'Please type a question.'

  const studyReply = replyFromStudy(text, studyContext)
  if (studyReply) return studyReply

  for (const { keys, answer } of TOPICS) {
    if (keys.some((k) => text.includes(k))) return answer
  }

  if (/\?/.test(message) || /^(what|how|why|when|where|can|does|is|who|which)\b/.test(text)) {
    return (
      'I can help with radiology AI topics: Grad-CAM, pneumonia, chest X-ray analysis, CT/MRI/US modalities, PDF reports, PACS, and how to use this platform. Try: "How do I analyze a chest X-ray?" or "What is Grad-CAM?"'
    )
  }

  return (
    'I\'m your Radiology AI assistant. Ask about findings, Grad-CAM, supported modalities, uploading scans, or generating reports. Type "help" for examples.'
  )
}
