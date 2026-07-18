# Slack Productivity Agents

An AI-powered productivity platform for Slack that brings intelligent workplace assistants directly into your Slack workspace.

The platform consists of three specialized AI agents, each designed for a specific purpose:

* **Personal Agent** – Employee productivity assistant for daily workplace tasks.
* **Knowledge Agent** – Company knowledge assistant powered by Hybrid Search and RAG.
* **Engineering Agent** – Developer assistant for monitoring, debugging, observability, and codebase support.

---

# Agents

## Personal Agent - The Personal Agent helps employees perform everyday workplace tasks.

### Features

* General AI assistant * Attendance management * Slack messaging * Personal productivity tools

Example:
> How many sick leaves do I have left?
> Message Backend Team that deployment is complete.
> Explain LangChain.

---

## Knowledge Agent - The Knowledge Agent retrieves answers from your organization's internal knowledge base.

### Features

* Hybrid Search - Vector Search + BM25
* Retrieval-Augmented Generation (RAG) over Company documentation search
 
Example:

> Explain the deployment pipeline.
> What is the leave policy?
> Summarize the onboarding guide.

---

## Engineering Agent - Assists developers by monitoring engineering systems and helping investigate issues across services.

### Features

#### MLflow Monitoring - Monitor MLflow experiments and model serving.

Example:
> Show today's failed inference requests.
> Which model version is currently deployed?
> What is the average API latency?

---

#### API Observability - Analyze application behavior and operational metrics.

---


# Architecture

```text
                           Slack
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
 Personal Agent         Knowledge Agent        Engineering Agent
      │                        │                        │
      │                        │                        │
 Attendance              Hybrid Search           MLflow
 Slack Messaging         Vector Database         API Logs
 Personal Tools          Company Docs            Observability
 General LLM             RAG                     Codebase Assistant
                                                   Technical Docs
```

---

## 🧪 Demo Images

## 1. Personal Agent(Attendance management)
<img width="2500" height="1155" alt="SCR-20260708-bgwc" src="https://github.com/user-attachments/assets/034dc3dc-c502-44eb-a054-154c0d0eae34" />

## 2. Kowledge Agent (Org Documents search and answering)
<img width="2548" height="1314" alt="SCR-20260714-duuf-2" src="https://github.com/user-attachments/assets/10853a56-de61-413b-9b57-f08a302536a7" />

## 3. AutoText Feature (Flags unusual logs in bakend to monitor systems (logs, models, latencies and more))
<img width="2538" height="1281" alt="SCR-20260718-meli" src="https://github.com/user-attachments/assets/9eda9beb-174d-4dea-91b0-beaa646401c4" />


---
# Future Integrations

* GitHub
* Jira
* Kubernetes
* Docker
* MLflow

---

# Vision

Slack Productivity Agents provides a unified AI workspace where employees, developers, and engineering teams can interact with specialized AI assistants directly inside Slack.

Instead of relying on a single general-purpose chatbot, the platform routes requests to domain-specific agents:

* **Personal Agent** for employee productivity and workplace actions.
* **Knowledge Agent** for trusted, retrieval-grounded company knowledge.
* **Engineering Agent** for software development, system observability, ML operations, and technical troubleshooting.

This modular architecture enables organizations to continuously expand their AI capabilities by introducing new specialized agents and tools without affecting existing workflows.
