# 🎸 Parsons: Cloud-Native AI Orchestration & Vinyl Record Intelligence Platform

> Bridging the gap between messy, unstructured internet data on vintage vinyl records and clean, deterministic web experiences through robust cloud-native AI orchestration.

---

## 🌟 The Problem & Motivation

Searching for rare, niche, or historical data on vintage vinyl records across the web is notoriously painful. Information is scattered across fragmented forum threads, auction listings, disparate discographies, and unstructured web pages—often buried under inconsistent formatting and noisy metadata. 

**Parsons** was built to solve this exact engineering challenge: an intelligent, cloud-native orchestration platform designed to autonomously search the web for unstructured vinyl record data, parse and validate the noise through a strict deterministic AI layer, and render rich, interactive web interfaces on the fly.

---

## 🏗️ System Architecture & Core Mechanics

Parsons is engineered as a secure, containerized full-stack application built for production readiness, leveraging modern cloud infrastructure and LLM tool orchestration.

```text
+-------------------------------------------------------------------+
|                           Parsons UI                              |
|             (Secure Flask App + Identity Management)              |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                    Tool Orchestration Layer                       |
|         (Search Integration + Gemini API Model Calls)             |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                     Deterministic AI Layer                        |
|       (Strict JSON Schemas + Adversarial Prompt Mitigation)       |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        GCP Cloud Run / CI/CD                      |
|                  (Containerized Deployment Pipeline)              |
+-------------------------------------------------------------------+
```

### Core Components
* **Flask Web Interface:** A secure, responsive frontend providing seamless interaction, user identity management, and real-time visualization of retrieved vinyl record datasets.
* **Intelligent Search & Tool Orchestration:** Service-based orchestration layer that queries external web sources for unstructured vinyl data and feeds raw payloads into generative pipelines.
* **Deterministic AI Layer:** Utilizes the **Gemini API** backed by strict **JSON Schemas** to force unstructured web text into rigorous, validated data models—eliminating hallucinations and ensuring guaranteed structural integrity.
* **Adversarial Prompt Mitigation:** Built-in sanitization and boundary enforcement to protect against prompt injection and malformed input from scraping external web sources.

---

## ⚙️ Key Engineering Highlights

* **Cloud-Native Containerization:** Fully containerized via **Docker**, optimized for lightweight execution and seamless scaling.
* **Serverless Deployment on GCP:** Deployed and hosted on **Google Cloud Run**, ensuring automatic scaling from zero, high availability, and zero infrastructure overhead.
* **Automated CI/CD Pipeline:** Integrated with **GitHub Actions** for continuous integration, automated testing, and streamlined container deployments to GCP.
* **Strict Data Integrity:** Solves the core challenge of LLM unreliability by pairing generative search with programmatic JSON schema validation before anything touches the frontend UI.

---


## 🛠️ Tech Stack

* **Backend & UI:** Python, Flask, Gunicorn
* **AI & Orchestration:** Google Gemini API, Custom JSON Schema Validation, Tool Orchestration Layer
* **Cloud & DevOps:** Google Cloud Run, Docker, GitHub Actions, GCP IAM
