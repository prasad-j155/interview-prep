# interview-prep

# 🎙️ AcePrep: Your AI Mock Interview Coach

**AcePrep** is an AI-powered mock interview web app built with Streamlit. It helps you prepare for technical interviews by asking domain-specific questions, allowing voice or typed responses, and giving real-time evaluation using large language models (LLMs).

---

## 🚀 Features

- 🎯 Choose interview domain (Machine Learning, Java Full Stack, Electrical Engineering)
- 🎤 Voice input via browser mic (auto-transcribed)
- ✍️ Text input with editable transcription
- 📊 Real-time scoring (0–5) with detailed feedback
- 🧠 Final summary and improvement suggestions
- 💡 Clean, mobile-friendly UI with dark mode support

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) – UI and app framework  
- [Together.ai](https://www.together.ai/) – LLM-powered evaluation (Meta LLaMA 3.1)
- `audio_recorder_streamlit` – Voice input recorder
- `SpeechRecognition` – Transcribe voice to text
- `python-dotenv` – Environment variable loader

---

## 🧪 Live Demo

👉 Coming soon! (Deployed via [Streamlit Community Cloud](https://streamlit.io/cloud))

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/prasad-j155/interview-prep.git


# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

##  🔐 Setup API Key
Create a .env file in the root directory:

```bash
TOGETHER_API_KEY=your_actual_together_api_key_here
```
---
