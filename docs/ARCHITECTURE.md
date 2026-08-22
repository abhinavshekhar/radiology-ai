# Radiology AI Assistant

## Architecture

```
Frontend (React + Tailwind)
        │
        ▼
   API Gateway (FastAPI)
        │
        ▼
  Inference Server (PyTorch + TorchXRayVision)
        │
   ┌────┴────┐
   ▼         ▼
Grad-CAM   Report Generator
   │         │
   └────┬────┘
        ▼
   SQLite DB + File Storage
```

## AI Pipeline

1. **Upload** — PNG, JPG, or DICOM chest X-ray
2. **Preprocessing** — CLAHE, denoising, resize, normalize
3. **Prediction** — DenseNet121 (TorchXRayVision pretrained)
4. **Explainability** — Grad-CAM heatmap overlay
5. **Report** — Template-based radiology report + PDF export

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | JWT authentication |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/patients` | Create patient |
| GET | `/api/v1/patients` | List patients |
| POST | `/api/v1/upload` | Upload scan |
| POST | `/api/v1/predict/{study_id}` | Run full AI analysis |
| GET | `/api/v1/studies/{study_id}` | Get study with results |
| GET | `/api/v1/history` | Study history |
| GET | `/api/v1/metrics` | Dashboard metrics |

## Database Schema

- **users** — Authentication (doctor, radiologist, admin)
- **patients** — Patient demographics
- **studies** — Uploaded scans
- **predictions** — AI results with confidence, severity, differential
- **reports** — Generated radiology reports
- **audit_logs** — Security audit trail

## Security

- JWT-based authentication
- Role-based access (doctor, radiologist, admin)
- Audit logging for all actions
- Demo credentials: `doctor@radiology.ai` / `demo1234`

## Future Extensions

- Orthanc PACS integration (Docker profile: `pacs`)
- OHIF DICOM viewer
- LLM-powered report generation (Gemini/OpenAI)
- CT/MRI modality support
- HL7/FHIR integration
- Celery async task queue for batch processing
