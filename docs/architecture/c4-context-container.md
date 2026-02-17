# C4: Context & Container — Call Center AI Insights

This document explains the system architecture using three complementary views:

1. **Simple Data Flow** — high-level overview of how calls move through the process  
2. **C4 Level 1 (Context)** — how the system interacts with external actors and services  
3. **C4 Level 2 (Container)** — internal technical components and integrations  

The system processes **call-center audio recordings** (prospect ↔ agent) to generate **structured insights** such as sentiment, topics, intent, questions asked, and improvement actions.

---

## Simple Data Flow

<img width="2712" height="1067" alt="simple_data_flow" src="https://github.com/user-attachments/assets/e0c7a31e-a3b4-489b-877a-4595f5c5ce68" />

**Explanation**

This diagram shows the operational path of a call and the role of each actor:

- **Prospective callers:** Contact the institution to ask questions about programs, requirements, or application steps. Their conversation becomes the raw input for analysis.

- **Promotion / Outreach team:** Serves as the institutional contact layer, coordinating communication with prospects and supporting engagement activities.

- **Call-center / Customer service area (key actor):** Agents **place or handle the call**, guide the conversation, and provide information to the prospect.  
  The **call is recorded during this interaction**, making it the primary source of data that is later processed by the analytics system.

- **Admissions / Registry area:** Uses insights derived from recorded calls to identify recurring issues, clarify procedures, and improve the enrollment process.

The diagram is simplified to highlight where the recorded call originates and how it connects the operational interaction with later analysis.



---

## Level 1 — System Context

![lvl1](https://github.com/user-attachments/assets/0eddc7fb-c73c-43b7-a498-224236e6f702)

**Explanation**

The Level 1 diagram shows the system in its environment and how it interacts with external actors and services.

- Internal staff consult dashboards to review reports and metrics derived from processed calls.  
- Recorded calls are provided by an external recording platform.  
- The analytics system sends transcription and language-processing requests to an external AI service.  
- The system exports structured outputs that feed visualization tools used for monitoring trends and insights.

At this level, the focus is on **system boundaries and integrations**, not implementation details.

---

## Level 2 — Container Diagram

![lvl2](https://github.com/user-attachments/assets/9e5d83b1-4207-4b43-a08e-e7857fff1e16)

**Explanation**

The Level 2 diagram describes the main internal components responsible for processing recordings.

- A **workflow engine** orchestrates the pipeline execution, triggers processing, and coordinates transformations.
- A **connectivity/API layer** manages authentication, external requests, and communication with AI services.
- A **local storage layer** handles audio files used during processing.
- The system runs inside a **containerized environment**, ensuring dependency management and reproducibility.
- Processed results are exported to a structured data store and later visualized in dashboards for internal users.

This level highlights **how the system is structured internally**, showing responsibilities of each container and how data moves between them.

---
