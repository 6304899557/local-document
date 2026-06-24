import os
import streamlit as st
import tempfile
from llama_cpp import Llama
import pymupdf4llm

# Set up the web page layout
st.set_page_config(page_title="Universal Doc AI", page_icon="🤖", layout="wide")
st.title("🚀 Universal Local Document AI")
st.caption("Chat with any document securely and completely offline using Qwen 2.5")

# Cache the AI model in memory
@st.cache_resource
def load_llm():
    return Llama(model_path="qwen2.5-3b-instruct-q4_k_m.gguf", n_ctx=4048, n_threads=4, verbose=False)

# Parse any uploaded PDF file path
def parse_pdf_to_sections(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path)
    lines = md_text.split("\n")
    sections = {}
    current_heading = "Introduction / General Overview"
    current_content = []
    
    for line in lines:
        if line.strip().startswith("#"):
            if current_content:
                sections[current_heading] = "\n".join(current_content).strip()
                current_content = []
            current_heading = line.strip()
        else:
            current_content.append(line)
    if current_content:
        sections[current_heading] = "\n".join(current_content).strip()
    return sections

def find_relevant_headings(question, headings, llm):
    headings_string = "\n".join([f"- {h}" for h in headings])
    prompt = f"""<|im_start|>system
You are a precise document router. Analyze the user's question and select the exact headings from the list below that likely contain the information needed to answer.
Output ONLY the exact text of the chosen headings, one per line. Do not write introductory text or explanations.
<|im_end|>
<|im_start|>user
Question: {question}

Available Headings:
{headings_string}
<|im_end|>
<|im_start|>assistant
"""
    response = llm(prompt, max_tokens=250, temperature=0.1)
    return response["choices"][0]["text"].strip()

def generate_answer(question, context, llm):
    prompt = f"""<|im_start|>system
You are a helpful document assistant. Answer the user's question using ONLY the provided document context below. If you cannot find the answer, state that you don't know.
<|im_end|>
<|im_start|>user
Context text:
{context}

Question: {question}
<|im_end|>
<|im_start|>assistant
"""
    response = llm(prompt, max_tokens=1024, temperature=0.7)
    return response["choices"][0]["text"].strip()

# Initialize AI Engine
llm = load_llm()

# Layout split
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 Document Hub")
    # Interactive file uploader module
    uploaded_file = st.file_uploader("Drag and drop your own PDF here", type=["pdf"])
    
    sections = None
    if uploaded_file is not None:
        # Create a temporary file safely to let PyMuPDF4LLM map it out
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
            
        try:
            sections = parse_pdf_to_sections(tmp_path)
            st.success(f"Successfully processed: {uploaded_file.name}")
            st.write(f"**Detected Chapters:** {len(sections)}")
            
            # Show interactive chapters layout
            for heading in sections.keys():
                with st.expander(heading):
                    st.text_area("Snippet content", sections[heading][:200] + "...", height=70, disabled=True, key=heading)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        st.info("Upload a PDF file to begin mapping structure.")

with col2:
    st.header("💬 Intelligent Assistant Portal")
    user_question = st.text_input("Ask a question about the uploaded document:", placeholder="e.g., Summarize the main points...")
    
    if user_question:
        if sections:
            with st.spinner("🔍 Routing question to target sections..."):
                choices = find_relevant_headings(user_question, list(sections.keys()), llm)
            
            retrieved_context = ""
            matched_headings = []
            for heading, content in sections.items():
                clean_heading = heading.replace('#', '').strip().lower()
                if clean_heading in choices.lower() or choices.lower() in clean_heading:
                    matched_headings.append(heading)
                    retrieved_context += f"\n\n--- {heading} ---\n{content}"
            
            if not retrieved_context:
                retrieved_context = list(sections.values())[0]
                matched_headings.append(list(sections.keys())[0])
            
            st.info(f"📍 **Context extracted from:** {', '.join(matched_headings)}")
            
            with st.spinner("✍️ Formulating perfect answer..."):
                answer = generate_answer(user_question, retrieved_context, llm)
            
            st.markdown("### ✨ Answer Response")
            st.write(answer)
        else:
            st.warning("Please upload a valid PDF document on the left panel first.")
