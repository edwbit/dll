import streamlit as st
from io import BytesIO
from docx import Document
from docx.shared import Pt
from groq import Groq

# Load the API key from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

my_llm = "llama-3.2-90b-text-preview"

# Function to generate the lesson plan using AI
def generate_lesson_plan(competency, subject, grade_level, strategies, content, past_lesson, part_a, part_b, part_c, part_d, part_e, part_f, part_g, part_h, part_i):
    prompt = f"""
    Generate a lesson plan based on the following parameters:
    Competency: {competency}
    Subject: {subject}
    Grade Level: {grade_level}
    Strategies: {strategies}
    Content: {content}
	past_lesson: {past_lesson}
    
	Apply the following structure to generate the lesson plan:
	
    	A. Reviewing {past_lesson} or presenting the new lesson. Time limit is {part_a}
		The teacher will activates prior knowledge based on {past_lesson} or introduces new topic.
		The teacher will also ask 2 HOTS questions.
		

	B. Establishing a purpose for the lesson based on {competency}. Time limit is {part_b} 
		The teacher will presents an engaging activity or question to spark interest
		The teacher will also ask 2 HOTS questions.

	C. Presenting examples/instances of the new lesson. Time limit is {part_c}
		The teacher provides concrete examples or demonstrations of the new concept using 21st centutry skills strategies or {strategies}
		

	D. Discussing new concepts and practicing new skills #1. Time limit is {part_d}
		The teacher explains new concepts and guides initial practice using 21st century skills strategies or {strategies}
		

	E. Discussing new concepts and practicing new skills #2. Time limit is {part_e}
		Studentss are engage in addtional discussion and attempt to further apply new knowledge/skills using using 21st century skills strategies or {strategies}

	F. Developing mastery. Time limit is {part_f}
		The teacher provides opportunities for more independent practice
		Students will practice applying new concepts/skills, demonstrating growing competence using 21st century skills strategies or {strategies}

	G. Finding practical applications of concepts. Time limit is {part_g}
		The teacher prompts students to consider real-world applications
		The students will brainstorm and share ideas on how the learning applies to their lives using 21st century skills strategies or {strategies}

	G. Making generalizations and abstractions about the lesson. Time limit is {part_h}
		The teacher will facilitates discussion to summarize key points and broader implications
		The students will articulate main ideas and how they connect to larger concepts

	I. Evaluating learning. Time limit is {part_i}
		The teacher will assign a task to assess understanding and application of learning in a form of a quiz
		The students will complete the assigned task, demonstrating their grasp of the lesson content
    
    Please format the output as follows:
    - Use '**' for bold text, not for bullet points
    - Use '-' for bullet points
    - Use a single line break between paragraphs
    - Use two line breaks between sections
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model= my_llm
    )
    return chat_completion.choices[0].message.content

# Function to format the generated lesson plan
def format_lesson_plan(lesson_plan_data):
    formatted_plan = "4As Lesson Plan\n\n"
    sections = lesson_plan_data.split('\n\n')

    for section in sections:
        lines = section.split('\n')
        if lines[0].strip().lower() in ['activity', 'analysis', 'abstraction', 'application', 'assessment']:
            formatted_plan += f"**{lines[0].strip()}**\n\n"
            formatted_plan += '\n'.join(lines[1:]).strip() + '\n\n'
        else:
            formatted_plan += section.strip() + '\n\n'

    # Remove extra asterisks from key-value pairs
    formatted_plan = '\n'.join([line.replace('**: **', ': ') if ': ' in line else line for line in formatted_plan.split('\n')])

    return formatted_plan

# Function to export the lesson plan to DOCX
def export_to_docx(lesson_plan):
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
            # # Section header
            # current_section = line.strip('**')
            # doc.add_heading(current_section, level=2)
            # in_list = False

            # Section header
            current_section = line.strip('**')
            p = doc.add_paragraph()
            run = p.add_run(current_section)
            font = run.font
            font.bold = True
            font.size = Pt(12)
            in_list = False
            doc.add_paragraph()  # Add a line break
            
        elif line.startswith('-**'):
            # Bullet point with bold text
            if not in_list:
                in_list = True
            p = doc.add_paragraph(line.lstrip('-**').strip(), style='List Bullet')
            p.runs[0].bold = True
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
        elif line.startswith('*') and line.endswith('*'):
            # Emphasized text
            doc.add_paragraph(line.strip('*')).italic = True
        elif line:
            # Regular paragraph
            if in_list and not line[0].isdigit():
                in_list = False
            p = doc.add_paragraph()
            parts = line.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part.strip())
                if i % 2 == 1:  # Odd-indexed parts were between ** in the original text
                    run.bold = True
    
    doc_file = BytesIO()
    doc.save(doc_file)
    doc_file.seek(0)
    return doc_file

# Function to export the lesson plan to plain text
def export_to_txt(lesson_plan):
    txt_file = BytesIO()
    txt_file.write(lesson_plan.encode('utf-8'))
    txt_file.seek(0)
    return txt_file

# Streamlit app layout
st.title(f"4As Lesson Plan Generator using {my_LLM}")

# User inputs
competency = st.text_input("1. Competency:", "")
subject = st.text_input("2. Subject:", "")
grade_level = st.text_input("3. Grade level:", "")
strategies = st.text_input("4. Teaching strategies:", "")
content = st.text_input("5. Content:", "")

past_lesson = st.text_input("6. Past lesson:")
part_a = st.text_input("7. Reviewing previous lesson or presenting the new lesson time limi(minutes):", "5")
part_b = st.text_input("8. Establishing a purpose for the lesson time limi(minutes):", "5")
part_c = st.text_input("9. Presenting examples/instances of the new lesson time limit (minutes):", "5")
part_d = st.text_input("10. Discussing new concepts and practicing new skills #1 time limi(minutes):", "5")
part_e = st.text_input("11. Discussing new concepts and practicing new skills #2 time limit (minutes):", "5")
part_f = st.text_input("12. Developing mastery time limit (minutes):", "10")
part_g = st.text_input("13. Finding practical applications of concepts time limit (minutes):", "10")
part_h = st.text_input("14. Making generalizations and abstractions about the lesson time limit (minutes):", "5")
part_i = st.text_input("15. Evaluating learning time limit (minutes):", "10")

if st.button("Generate Lesson Plan"):
    if competency and subject and grade_level and strategies and content:
        # Generate the lesson plan
        raw_lesson_plan = generate_lesson_plan(
            competency, subject, grade_level, strategies, content, past_lesson, part_a, part_b, part_c, part_d, part_e, part_f, part_g, part_h, part_i)
        
        # Format the lesson plan
        formatted_lesson_plan = format_lesson_plan(raw_lesson_plan)

        # Display the formatted lesson plan
        st.markdown(formatted_lesson_plan)

        # Export the formatted lesson plan to DOCX
        docx_file = export_to_docx(formatted_lesson_plan)

        # Provide download button for the DOCX
        st.download_button(
            label="Download as DOCX",
            data=docx_file,
            file_name="lesson_plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    else:
        st.warning("Please fill in all fields.")
                    
