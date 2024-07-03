import streamlit as st
from app.mcq_generation import MCQGenerator
import textwrap
import random
import pdfplumber

# Function to display MCQs on Streamlit UI
def display_mcqs(questions):
    for i, question in enumerate(questions):
        st.subheader("Question:")
        st.write(question.questionText)

        st.subheader("Options:")
        options = get_or_create_options(i, question)  # Get or create options for this question
        user_choice = st.radio("Choose an option:", options, key=f"question_{i}")

        with st.form(key=f"form_{i}"):
            submitted = st.form_submit_button(f"Submit_{i+1}")

            if submitted:
                if user_choice == question.answerText:
                    st.write("Correct!", unsafe_allow_html=True)
                else:
                    st.write("Wrong! Correct answer is:", question.answerText, unsafe_allow_html=True)

# Function to get or create shuffled options for a question
def get_or_create_options(i, question):
    options_key = f"options_{i}"
    if options_key not in st.session_state:
        options = [question.answerText] + question.distractors
        random.shuffle(options)
        st.session_state[options_key] = options
    else:
        options = st.session_state[options_key]
    return options

# Main function
def main():
    st.title("MCQ Quiz")

    # Accept input type from the user
    input_type = st.radio("Choose input type:", ("Upload File", "Enter Paragraph"))

    if input_type == "Upload File":
        uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf"])
        if uploaded_file is not None:
            if uploaded_file.type == "text/plain":  # If it's a text file
                content = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":  # If it's a PDF file
                content = extract_text_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a text or PDF file.")
                return

            num_questions = st.number_input("Enter the number of questions:", min_value=1, step=1, value=5)

            if content:
                questions = generate_mcq_questions(content, num_questions)

                # Display MCQs
                display_mcqs(questions)
    else:
        content = st.text_area("Enter Paragraph", "")
        num_questions = st.number_input("Enter the number of questions:", min_value=1, step=1, value=5)

        if content:
            questions = generate_mcq_questions(content, num_questions)

            # Display MCQs
            display_mcqs(questions)


# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Generate MCQs and cache the result
@st.cache_data()
def generate_mcq_questions(context, count):
    return MCQGenerator().generate_mcq_questions(context, count)[:count]

if __name__ == "__main__":
    main()
