# Call Center AI Insights

Automated pipeline for analyzing call-center conversations and generating structured insights using transcription and language models.

---

## Overview

This project presents a prototype system designed to transform recorded call-center conversations into structured, analyzable information.  
The system processes audio recordings between prospective applicants and service agents, extracting conversational signals such as sentiment, topics, intent, questions, and improvement opportunities.

The goal is to support institutional teams in understanding recurring concerns, improving communication processes, and identifying patterns in applicant interactions.

---

## Key Features

- Automated call transcription
- Sentiment, emotion, and interest analysis
- Topic and intent extraction
- Identification of prospect questions and keywords
- Generation of improvement recommendations
- Structured data export for analytics and dashboards

---

## Architecture

The solution follows a workflow-based architecture in n8n:

1. Call recordings are obtained from an external recording platform  
2. Audio is transcribed using an AI transcription service  
3. Language models analyze the transcript to extract structured information  
4. Results are exported to structured datasets  
5. Dashboards visualize aggregated insights for institutional teams  

Detailed diagrams:

- 📄 [C4 Context & Container](docs/architecture/c4-context-container.md)

---

## Methodology

The project was developed using an iterative approach inspired by Lean Startup principles:

- Exploration of operational needs  
- Prototype construction and experimentation  
- Validation with real and simulated data  
- Iterative refinement of prompts and workflow  
- Visualization of results for institutional interpretation  

More details:

- 📄 [Methodology](docs/methodology.md)

---

## Evaluation Results

The prototype was evaluated by comparing automated outputs against human-generated references.

**Transcription**
- WER ≈ 24.4%  
- Accuracy ≈ 75–76%

**Conversational Analysis**
- Precision ≈ 77.9%  
- F1-score ≈ 0.665  

Human variability in transcription and annotation was considered part of the evaluation baseline.

More details:

- 📄 [Metrics Summary](docs/metrics-summary.md)

---

## Prompt Design

The analysis pipeline relies on structured prompts for different tasks:

- Sentiment, emotion, and interest analysis  
- Topic and intent extraction  
- Improvement action recommendations  

See:

- 📄 `docs/prompts/`

---

## Repository Structure


