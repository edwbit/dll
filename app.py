import streamlit as st
from io import BytesIO
from docx import Document
from docx.shared import Pt
from groq import Groq
import re

# Load the API key from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)
my_llm = "llama-3.2-90b-text-preview"

# Function to generate the lesson plan using AI
def generate_lesson_plan(competency, subject, grade_level, selected_strategies, content, past_lesson, part_a, part_b, part_c, part_d, part_e, part_f, part_g, part_h, part_i, language):
    prompt = f"""
    Generate a lesson plan based on the following parameters:
    Competency: {competency}
    Subject: {subject}
    Grade Level: {grade_level}
    Strategies: {selected_strategies}
    Content: {content}
    past_lesson: {past_lesson}
    
    Apply the following structure and the {language} language to generate the lesson plan using plain and simple words and in human-like tone:
    Be sure to use heading and bulleted list always.

    A. Reviewing or Presenting the New Lesson. Time Limit: {part_a} minutes.
    B. Establishing a Purpose for the Lesson. Time Limit: {part_b} minutes.
    C. Presenting Examples/Instances of the New Lesson. Time Limit: {part_c} minutes.
    D. Discussing New Concepts and Practicing New Skills #1. Time Limit: {part_d} minutes.
    E. Discussing New Concepts and Practicing New Skills #2. Time Limit: {part_e} minutes.
    F. Developing Mastery. Time Limit: {part_f} minutes.
    G. Finding Practical Applications of Concepts. Time Limit: {part_g} minutes.
    H. Making Generalizations and Abstractions about the Lesson. Time Limit: {part_h} minutes.
    I. Evaluating Learning. Time Limit: {part_i} minutes.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=my_llm
    )
    return chat_completion.choices[0].message.content

# Function to format the generated lesson plan
def format_lesson_plan(lesson_plan_data):
    formatted_plan = "Daily Lesson Log\n\n"
    sections = lesson_plan_data.split('\n\n')

    for section in sections:
        lines = section.split('\n')
        if lines[0].strip().startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.')):
            formatted_plan += f"**{lines[0].strip()}**\n\n"
            formatted_plan += '\n'.join(lines[1:]).strip() + '\n\n'
        else:
            formatted_plan += section.strip() + '\n\n'
    
    return formatted_plan

# Function to export the lesson plan to DOCX
def export_to_docx(lesson_plan, raw_lesson_plan):
    doc = Document()
    
    # Add title
    title = lesson_plan.split('\n')[0].strip()
    doc.add_heading(title, level=1)
    
    # Process the rest of the content
    lines = lesson_plan.split('\n')[1:]
    current_section = None
    in_list = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('**') and line.endswith('**'):
            # Section header
            current_section = line.strip('**')
            p = doc.add_paragraph()
            run = p.add_run(current_section)
            font = run.font
            font.bold = True
            font.size = Pt(12)
            in_list = False
        elif line.startswith('-'):
            # Bullet point
            if not in_list:
                in_list = True
            doc.add_paragraph(line.lstrip('-').strip(), style='List Bullet')
        elif ':' in line:
            # Key-value pair
            key, value = line.split(':', 1)
            p = doc.add_paragraph()
            p.add_run(key.strip('** ')).bold = True
            p.add_run(f": {value.strip('** ')}")
            in_list = False
        elif line:
            # Regular paragraph
            if in_list and not line[0].isdigit():
                in_list = False
            p = doc.add_paragraph(line)
    
    # Add a page break before the raw text version
    doc.add_page_break()
    
    # Add the raw text version
    doc.add_heading("Raw AI-Generated Version", level=1)
    doc.add_paragraph(raw_lesson_plan)
    
    doc_file = BytesIO()
    doc.save(doc_file)
    doc_file.seek(0)
    return doc_file

# Streamlit app layout
st.title("📚 Daily Lesson Log Generator with AI")
st.caption(f"Generated using {my_llm}. Developed by ebb with AI assistance.")

# Organizing input sections into two columns
col1, col2 = st.columns(2)

with col1:
    language = st.text_input("Language:", "required")
    competency = st.text_input("Competency:", "required")
    subject = st.text_input("Subject:", "required")
    grade_level = st.text_input("Grade Level:", "required")

with col2:
    strategies = ["Project-Based Learning", "Collaborative Learning", "Real-World Applications", "Technology Integration", "Differentiated Instruction"]
    selected_strategies = st.multiselect("Teaching Strategies:", strategies)
    content = st.text_input("Content:", "required")
    past_lesson = st.text_input("Past Lesson:", "required")

st.markdown("---")  # Horizontal divider for clarity

# Time limit inputs
st.subheader("Time Limits (in minutes)")
col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_h, col_i = st.columns(9)

with col_a:
    part_a = st.text_input("A:", "5")

with col_b:
    part_b = st.text_input("B:", "5")

with col_c:
    part_c = st.text_input("C:", "5")

with col_d:
    part_d = st.text_input("D:", "5")

with col_e:
    part_e = st.text_input("E:", "5")

with col_f:
    part_f = st.text_input("F:", "10")

with col_g:
    part_g = st.text_input("G:", "10")

with col_h:
    part_h = st.text_input("H:", "5")

with col_i:
    part_i = st.text_input("I:", "10")

# Generate Lesson Plan button
if st.button("Generate Lesson Plan"):
    if language and competency and subject and grade_level and selected_strategies and content and past_lesson:
        # Generate the lesson plan
        raw_lesson_plan = generate_lesson_plan(
            competency, subject, grade_level, selected_strategies, content, past_lesson, 
            part_a, part_b, part_c, part_d, part_e, part_f, part_g, part_h, part_i, language)
        
        # Format the lesson plan
        formatted_lesson_plan = format_lesson_plan(raw_lesson_plan)

        # Display the formatted lesson plan
        st.markdown(formatted_lesson_plan)

        # Export the lesson plan to DOCX (including raw version)
        docx_file = export_to_docx(formatted_lesson_plan, raw_lesson_plan)

        # Provide download button for the DOCX
        st.download_button(
            label="Download Lesson Plan (DOCX with raw AI output)",
            data=docx_file,
            file_name="lesson_plan_with_raw.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )      
    else:
        st.warning("Please fill in all fields.")
