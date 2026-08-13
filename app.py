
import streamlit as st
import google.generativeai as genai
import os
import json
import re


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Interactive Question Generator",
    page_icon="🧠",
    layout="centered"
)


# -----------------------------
# GEMINI CONFIGURATION
# -----------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("Gemini API key is not configured.")
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-3.6-flash")


# -----------------------------
# PAGE TITLE
# -----------------------------

st.title("🧠 Interactive Question Generator")

st.write(
    "Generate questions on any topic and test your knowledge interactively."
)


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("Question Settings")

topic = st.sidebar.text_input(
    "Enter Topic",
    placeholder="Example: Python Functions"
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

question_type = st.sidebar.selectbox(
    "Question Type",
    ["MCQ", "True/False", "Short Answer"]
)

number_of_questions = st.sidebar.slider(
    "Number of Questions",
    min_value=1,
    max_value=10,
    value=5
)


# -----------------------------
# GENERATE QUESTIONS
# -----------------------------

if st.sidebar.button("Generate Questions"):

    if not topic:
        st.warning("Please enter a topic.")
        st.stop()

    prompt = f"""
    Generate {number_of_questions} questions about {topic}.

    Difficulty: {difficulty}
    Question Type: {question_type}

    Return ONLY valid JSON.

    For MCQ use this format:

    [
      {{
        "question": "Question text",
        "options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "answer": "Correct option",
        "explanation": "Short explanation"
      }}
    ]

    For True/False use:

    [
      {{
        "question": "Question text",
        "options": ["True", "False"],
        "answer": "True",
        "explanation": "Short explanation"
      }}
    ]

    For Short Answer use:

    [
      {{
        "question": "Question text",
        "answer": "Expected answer",
        "explanation": "Short explanation"
      }}
    ]

    Do not add markdown.
    Do not add ```json.
    Return only JSON.
    """

    with st.spinner("Generating questions..."):

        try:

            response = model.generate_content(prompt)

            response_text = response.text.strip()

            # Remove accidental markdown formatting
            response_text = re.sub(
                r"```json|```",
                "",
                response_text
            ).strip()

            questions = json.loads(response_text)

            st.session_state.questions = questions
            st.session_state.topic = topic
            st.session_state.score = 0
            st.session_state.submitted = {}

        except Exception as e:

            st.error("Unable to generate questions.")
            st.write(e)


# -----------------------------
# DISPLAY QUESTIONS
# -----------------------------

if "questions" in st.session_state:

    st.subheader(
        f"📚 Topic: {st.session_state.topic}"
    )

    questions = st.session_state.questions

    for i, q in enumerate(questions):

        st.markdown(
            f"### Question {i + 1}"
        )

        st.write(q["question"])

        if "options" in q:

            selected_answer = st.radio(
                "Choose your answer:",
                q["options"],
                key=f"question_{i}"
            )

            if st.button(
                f"Submit Answer {i + 1}",
                key=f"submit_{i}"
            ):

                if selected_answer == q["answer"]:

                    st.success("✅ Correct!")

                    st.session_state.score += 1

                else:

                    st.error(
                        f"❌ Incorrect! Correct answer: {q['answer']}"
                    )

                st.info(
                    f"💡 Explanation: {q['explanation']}"
                )

        else:

            user_answer = st.text_input(
                "Your answer:",
                key=f"answer_{i}"
            )

            if st.button(
                f"Submit Answer {i + 1}",
                key=f"submit_short_{i}"
            ):

                st.info(
                    f"Expected answer: {q['answer']}"
                )

                st.info(
                    f"💡 Explanation: {q['explanation']}"
                )


    # -----------------------------
    # SCORE
    # -----------------------------

    st.divider()

    if st.button("🏆 Show Score"):

        total = len(questions)

        score = st.session_state.score

        percentage = (score / total) * 100

        st.subheader("🎉 Your Result")

        st.write(
            f"Score: **{score}/{total}**"
        )

        st.write(
            f"Percentage: **{percentage:.1f}%**"
        )

        if percentage >= 80:

            st.success(
                "Excellent! 🎉 You have a strong understanding of the topic."
            )

        elif percentage >= 50:

            st.warning(
                "Good attempt! 👍 You can improve with more practice."
            )

        else:

            st.error(
                "Keep practicing! 📚 Review the topic and try again."
            )
