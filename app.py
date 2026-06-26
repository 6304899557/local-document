import os
from llama_cpp import Llama
import pymupdf4llm

def parse_pdf_to_sections(pdf_path):
    print(f"📖 Processing PDF layout: {pdf_path}")
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

def main():
    pdf_file = "sample.pdf"  
    model_file = "qwen2.5-3b-instruct-q4_k_m.gguf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ Error: Please place a PDF document named '{pdf_file}' in this folder.")
        return

    sections = parse_pdf_to_sections(pdf_file)
    print(f"✅ Document split into {len(sections)} sections.")
    from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import os


model_path = hf_hub_download(
    repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF", 
    filename="qwen2-0_5b-instruct-q4_k_m.gguf"
)

print("\n🤖 Loading local LLM via llama.cpp...")
llm = Llama(model_path=model_path, n_ctx=4048, n_threads=4, verbose=False)
print("✅ Local LLM ready.")
    print("\n🤖 Loading local LLM via Llama.cpp...")
    llm = Llama(model_path=model_file, n_ctx=4048, n_threads=4, verbose=False)
    print("✅ Local LLM ready.")
    
    while True:
        question = input("\n❓ Question (or 'exit'): ")
        if question.lower() == "exit":
            break
            
        print("\n🔍 [FIND]: Selecting relevant document sections...")
        choices = find_relevant_headings(question, list(sections.keys()), llm)
        
        retrieved_context = ""
        for heading, content in sections.items():
            if heading.lower() in choices.lower():
                retrieved_context += f"\n\n--- {heading} ---\n{content}"
                
        if not retrieved_context:
            retrieved_context = list(sections.values())[0]
            
        print("✍️ [ANSWER]: Generating answer text...")
        answer = generate_answer(question, retrieved_context, llm)
        print(f"\n✨ ANSWER:\n{answer}")

if __name__ == "__main__":
    main()
