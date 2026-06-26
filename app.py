import os
import streamlit as str  # Imported for UI components
from llama_cpp import Llama
import pymupdf4llm
from huggingface_hub import hf_hub_download

# --- Streamlit Page Configuration ---
str.set_page_config(page_title="Local-First Document QA", page_icon="📄", layout="wide")
str.title("📄 Local-First Document QA")

# --- Helper Functions ---
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

# --- Cached Model & File Processing ---
# caching prevents downloading/reloading the model on every click
@str.cache_resource
def load_llm():
    with str.spinner("📥 Downloading and initializing Qwen2 model from Hugging Face..."):
        model_path = hf_hub_download(
            repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF", 
            filename="qwen2-0_5b-instruct-q4_k_m.gguf"
        )
        return Llama(model_path=model_path, n_ctx=4048, n_threads=4, verbose=False)

@str.cache_data
def process_uploaded_file(uploaded_file):
    # Save uploaded file temporarily
    temp_filename = "temp_uploaded_doc.pdf"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return parse_pdf_to_sections(temp_filename)

# --- Main Streamlit App Execution ---
def main():
    # Load Model
    llm = load_llm()
    str.success("🤖 Local LLM Ready!")

    # Sidebar for PDF uploads
    str.sidebar.header("Document Setup")
    uploaded_file = str.sidebar.file_uploader("Upload your sample.pdf", type=["pdf"])

    if uploaded_file is not None:
        sections = process_uploaded_file(uploaded_file)
        str.sidebar.success(f"✅ Document split into {len(sections)} sections.")
        
        # Question Input Area
        question = str.text_input("❓ Ask a question about your document:")
        
        if question:
            with str.spinner("🔍 [FIND]: Selecting relevant document sections..."):
                choices = find_relevant_headings(question, list(sections.keys()), llm)
            
            retrieved_context = ""
            for heading, content in sections.items():
                if heading.lower() in choices.lower():
                    retrieved_context += f"\n\n--- {heading} ---\n{content}"
            
            if not retrieved_context:
                retrieved_context = list(sections.values())[0]
                
            with str.spinner("✍️ [ANSWER]: Generating answer text..."):
                answer = generate_answer(question, retrieved_context, llm)
            
            str.subheader("✨ ANSWER:")
            str.write(answer)
            
            with str.expander("Show Retrieved Context Blocks"):
                str.code(retrieved_context)
    else:
        str.info("Please upload a PDF document in the sidebar to get started.")

if __name__ == "__main__":
    main()
