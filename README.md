## 🩺 Sterile AI OR Assistant (Hackathon Prototype)

A touchless, AI-powered operating room monitor that allows surgeons to access patient records and radiological imaging completely sterile—using only hand gestures and voice commands.

## 💡 The Problem

During surgery, physicians frequently need to check CT slices, lab results, or allergy profiles. Touching a mouse or keyboard breaks the sterile field. Delegating these tasks to assistants takes time, disrupts workflow, and increases the risk of communication errors.

## 🚀 The Solution

This project solves the sterility dilemma with a zero-touch interface. By combining MediaPipe Hands for intuitive gesture control and an OpenAI-powered AI Agent for complex voice commands, surgeons can retrieve critical data autonomously, quickly, and safely within the OR.

## ✨ Key Features (MVP)

* **Sterile Gesture Control**: Intuitive hand gestures (e.g., swipe to scroll CT slices, pinch to zoom, open hand to reset) captured via a standard webcam.
* **AI Voice Assistant (OpenAI Tool Calling)**: Understands natural language requests like "Show me the coagulation levels" or "Are there any allergies?" to control the dashboard autonomously.
* **Intelligent Context Analysis**: The LLM compares lab values on demand ("What changed since yesterday?") or filters the patient file for surgery-relevant risks.
* **OR Dashboard**: A high-performance frontend for simultaneous display of imaging (CT/MRI), vital parameters, and patient records.

## 🛠️ Tech Stack

* **Backend**: Python, FastAPI (Data API & OpenAI Agent logic)
* **Frontend**: React / Streamlit (Real-time OR monitor)
* **AI / Vision**: OpenAI API (Function Calling / LLM), MediaPipe (Hand-Tracking)

## 📁 Project Structure

```text
backend/          # API & OpenAI agent logic
frontend/         # Dashboard UI (Gesture & voice feedback)
assets/           # Medical imaging data (CT slices, MRI, X-ray)
data/             # Simulated patient and lab records (JSON)
```

---

*Developed for the OpenAI Codex Hackathon.*
