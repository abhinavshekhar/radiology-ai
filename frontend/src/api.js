import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const auth = {
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  },
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const patients = {
  list: () => api.get('/patients'),
  create: (data) => api.post('/patients', data),
  timeline: (id) => api.get(`/patients/${id}/timeline`),
}

export const studies = {
  upload: (patientId, file, modality = 'XR') => {
    const form = new FormData()
    form.append('patient_id', patientId)
    form.append('file', file)
    form.append('modality', modality)
    return api.post('/upload', form)
  },
  predict: (studyId) => api.post(`/predict/${studyId}`),
  predictAsync: (studyId) => api.post(`/predict/${studyId}/async`),
  gradcam: (studyId) => api.post(`/gradcam/${studyId}`),
  report: (studyId) => api.post(`/report/${studyId}`),
  get: (studyId) => api.get(`/studies/${studyId}`),
  image: (studyId) => `/api/v1/studies/${studyId}/image`,
}

export const dashboard = {
  history: () => api.get('/history'),
  metrics: () => api.get('/metrics'),
  demoSamples: () => api.get('/demo/samples'),
  auditLogs: () => api.get('/audit-logs'),
}

export const chat = {
  send: (message, studyContext = null) =>
    api.post('/chat', { message, study_context: studyContext }),
  sendPublic: (message, studyContext = null) =>
    api.post('/chat/public', { message, study_context: studyContext }),
}

export const pacs = {
  status: () => api.get('/pacs/status'),
  patients: () => api.get('/pacs/patients'),
  qido: () => api.get('/dicomweb/studies'),
  modalities: () => api.get('/modalities'),
}

export default api
