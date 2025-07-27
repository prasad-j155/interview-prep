import streamlit as st
import os
from dotenv import load_dotenv
from together import Together
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import tempfile
import time

# Load API Key
load_dotenv()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

# Subject Questions
subject_questions = {
    "Machine Learning": [
        "What is the difference between supervised and unsupervised learning?",
        "Can you explain overfitting and how to avoid it?",
        "What is the bias-variance tradeoff?",
        "How does a decision tree algorithm work?",
        "What is gradient descent, and how is it used in ML?"
    ],
    "Java Full Stack": [
        "What is the role of Spring Boot in Java full-stack development?",
        "Explain the difference between REST and SOAP web services.",
        "How does Angular or React integrate with Java backends?",
        "What are some ways to secure a full-stack web application?",
        "Explain the MVC architecture in the context of a Java web app."
    ],
    "Electrical Engineering": [
        "What is Ohm's Law and how is it used?",
        "Explain Kirchhoff’s Current Law (KCL).",
        "What are Fleming’s Left and Right Hand Rules?",
        "How does resistance affect current flow in a circuit?",
        "What is the difference between voltage and current?"
    ]
}

# --- 🔊 Audio to Text ---
def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio")
        except sr.RequestError as e:
            st.error(f"🌐 Could not request results; {e}")
    return ""

# --- 📊 AI Evaluation ---
def evaluate_answer(question, answer):
    try:
        prompt = f"""
You are a strict but fair technical interviewer.

Evaluate the candidate's answer to the question below:

Question:
{question}

Candidate's Answer:
{answer}

Before scoring, correct any obvious spelling or transcription errors based on context.

Please provide:
- Score (0 to 5)
- Brief Reason for the score (based on clarity, correctness, and completeness)

Format your response like:
Score: X/5
Reason: ...
"""
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- 🧾 Overall Summary ---
def get_final_feedback(qna_blocks, subject):
    prompt = f"""
The candidate completed a mock interview on the subject: {subject}.

{qna_blocks}

Provide:
- Feedback for each question
- 2–3 improvement suggestions
- Overall summary
"""
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()


# --- 🎨 Custom UI Styling ---
st.set_page_config(page_title="AcePrep: Your AI Mock Interview Coach", page_icon="🧠", layout="centered")

st.markdown("""
<style>
/* Interview Title */
h1 {
    color: var(--text-color);
}

/* Question Box */
.question-box {
    background-color: var(--secondary-background-color);
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #4B8BBE;
    font-size: 16px;
    margin-bottom: 20px;
}

/* Overall feedback box */
.feedback-box {
    background-color: var(--secondary-background-color);
    padding: 20px;
    border-left: 5px solid #1f77b4;
    border-radius: 8px;
    font-size: 15px;
}

/* Audio Recorder visibility fix (force visible outline & mic button) */
audio-recorder {
    filter: invert(100%);

}

/* For mobile: Make sure inputs are bigger and spacing is good */
@media screen and (max-width: 600px) {
    .element-container textarea {
        font-size: 16px !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🧠 AI Mock Interview Coach</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Answer questions and get instant AI feedback to sharpen your skills!</p>", unsafe_allow_html=True)
st.divider()

# --- 🔁 Session State ---
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.answers = []
    st.session_state.evaluations = []
    st.session_state.evaluated = False
    st.session_state.feedback = ""
    st.session_state.total_score = 0

if 'recording_start_time' not in st.session_state:
    st.session_state.recording_start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'recording' not in st.session_state:
    st.session_state.recording = False

# --- 🎯 Subject Select ---
subject = st.selectbox("🎯 Choose your interview domain:", list(subject_questions.keys()),
                       disabled=st.session_state.question_index > 0)
questions = subject_questions[subject]
i = st.session_state.question_index
total_questions = len(questions)

st.progress((i / total_questions) if total_questions > 0 else 0)

# --- 🧠 Interview Q&A ---
text = ""
if i < total_questions:
    question = questions[i]
    st.subheader(f"❓ Question {i+1} of {total_questions}")
    st.markdown(f"<div class='question-box'>{question}</div>", unsafe_allow_html=True)

    if st.session_state.recording:
        st.session_state.elapsed_time = int(time.time() - st.session_state.recording_start_time)
        st.info(f"⏱️ Recording... {st.session_state.elapsed_time} seconds")
        if st.session_state.elapsed_time >= 60:
            st.warning("🛑 Auto-stopping after 60 seconds.")
            st.session_state.recording = False
        else:
            st.rerun()

    # --- 🎙️ Audio Recorder ---
    
    audio_bytes = audio_recorder(pause_threshold=1.5)
    if audio_bytes and len(audio_bytes) < 10000:
        st.warning("🎤 Please try again. Mic may not have initialized properly.")
        audio_bytes = None

    if audio_bytes:
        st.session_state.recording = False
        text = transcribe_audio(audio_bytes)
        if text:
            st.session_state.transcription_success = True
        if st.session_state.get("transcription_success"):
            st.success("✅ Transcription complete and inserted below!")
            

    answer = st.text_area("✍️ Type or edit your answer below:", key=f"answer_{i}", value=text)

    if st.button("🚀 Submit Answer"):
        st.session_state.answers.append((question, answer))
        st.session_state.question_index += 1
        # 🧹 Clear previous question-related states
        st.session_state[f"answer_{st.session_state.question_index}"] = ""
        st.session_state['transcription_success'] = False
        text=""

        st.rerun()

# --- ⚙️ Evaluation ---
elif not st.session_state.evaluated:
    st.header("⚙️ Evaluating your answers... Please wait ⏳")
    total_score = 0
    all_qna_blocks = ""

    for idx, (question, answer) in enumerate(st.session_state.answers):
        eval_result = evaluate_answer(question, answer)
        try:
            score_line = [line for line in eval_result.split("\n") if "Score:" in line][0]
            score = int(score_line.split("Score:")[1].split("/")[0].strip())
        except:
            score = 0

        total_score += score
        st.session_state.evaluations.append({
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": eval_result
        })
        all_qna_blocks += f"Q{idx+1}: {question}\nA: {answer}\n{eval_result}\n\n"

    st.session_state.total_score = total_score
    st.session_state.feedback = get_final_feedback(all_qna_blocks, subject)
    st.session_state.evaluated = True
    st.rerun()

# --- ✅ Final Results ---
else:
    st.success("✅ Interview Complete!")
    score_color = "#28a745" if st.session_state.total_score >= (total_questions * 0.7) else "#d9534f"
    st.markdown(f"<h3>Total Score: <span style='color:{score_color}'>{st.session_state.total_score}/{total_questions * 5}</span></h3>", unsafe_allow_html=True)

    st.subheader("📋 Per-Question Feedback")
    for idx, item in enumerate(st.session_state.evaluations):
        st.markdown(f"**Q{idx+1}:** {item['question']}")
        st.markdown(f"*Your Answer:* {item['answer']}")
        st.markdown(f"*Score:* {item['score']}/5")
        st.markdown(f"*Feedback:* {item['feedback']}")
        st.divider()

    st.subheader("🔍 Overall Suggestions")
    st.markdown(f"<div class='feedback-box'>{st.session_state.feedback}</div>", unsafe_allow_html=True)

    if st.button("🔁 Restart Interview"):
        st.session_state.clear()


