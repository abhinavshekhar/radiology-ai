# Judge Q&A Cheat Sheet — Keep on your phone

## Accuracy & Validation
**Q: How accurate?**
→ DenseNet121 on ChestX-ray14, AUC 0.84+. Confidence thresholds + human review for edge cases.

**Q: Did you train your own model?**
→ Used pretrained TorchXRayVision (validated on 100K+ images). Focused hackathon time on explainability + workflow, not training from scratch. We have a train.py for fine-tuning on RSNA dataset.

**Q: How do you validate?**
→ Confidence scoring, uncertainty flagging, differential diagnosis cross-check. Low confidence → "Needs Human Review."

## Clinical Safety
**Q: Can it replace doctors?**
→ NO. Clinical decision SUPPORT only. Every report: "Final interpretation by qualified radiologist required."

**Q: FDA approval?**
→ Not needed for decision support tools. We position as assistant, not autonomous diagnostic device.

**Q: Wrong diagnosis consequences?**
→ System flags uncertainty. Doctor always reviews. Heatmap lets doctor verify AI reasoning visually.

## Technical
**Q: Why DenseNet121?**
→ State-of-art for chest X-ray. CheXNet paper (Stanford) proved it works. TorchXRayVision provides pretrained weights.

**Q: What is Grad-CAM?**
→ Gradient-weighted Class Activation Mapping. Shows which image regions influenced the AI decision. Published at ICML 2017.

**Q: DICOM support?**
→ Yes. pydicom for parsing, windowing, pixel spacing. Orthanc PACS via Docker for hospital workflow simulation.

**Q: Scalability?**
→ Microservices: API → Inference Server → Model Registry → Storage. Celery + Redis for async. Docker Compose deployment.

## Business
**Q: Business model?**
→ SaaS per hospital. Freemium for rural clinics. API licensing for telemedicine.

**Q: Competitors?**
→ Qure.ai, Niramai — but we focus on EXPLAINABILITY + full workflow (report generation + differential dx), not just detection.

**Q: Go-to-market?**
→ Partner with 1 rural hospital for pilot. Tele-radiology integration. Government Ayushman Bharat alignment.

## Team
**Q: What was hardest?**
→ Balancing AI accuracy with explainability. Making Grad-CAM work reliably. Building production UI in 7 days.

**Q: Division of work?**
→ [Fill in your team roles: AI/ML, Backend, Frontend, DevOps, Presentation]

**Q: What's next?**
→ CT/MRI support, LLM reports, hospital pilot, HL7/FHIR integration.

## Trick Questions
**Q: Why only pneumonia?**
→ "One polished workflow > ten unfinished features. Judges see working demo, not promises."

**Q: Your model is wrong on this image.**
→ "That's why we have confidence scoring and human review. The heatmap lets the doctor see what AI saw and override."

**Q: Open source?**
→ "Architecture is modular. Core AI uses published pretrained models. Our innovation is the clinical workflow integration."

## Numbers to Remember
- 1 radiologist per 100,000 in India
- 2,500 children die daily from pneumonia
- 30 min → 30 sec reporting time reduction
- 18 pathology classes supported
- 96%+ confidence on clear cases
- 7 days to build full system
- AUC 0.84+ (ChestX-ray14 benchmark)
