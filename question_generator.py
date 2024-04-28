# This tool is meant to help with the question generation process. It utilizes open-source LLM model Llama developed by Meta.
# Outputs from this file are not logged, so make sure you save all interesting questions before exiting the terminal session.

from gpt4all import GPT4All
from docx import Document

model = GPT4All(model_name= "Meta-Llama-3-8B-Instruct.Q4_0.gguf")

def get_doc_in_sections(path: str):
    doc = Document(path)

    sec = ""
    secs = []
    for par in doc.paragraphs:
        if "heading" in par.style.name.lower() or "title" in par.style.name.lower():
            secs.append((par.text, sec))
            sec = ""
        else:
            sec += par.text

    return secs

prompt = """I am going to provide you with a paragraph of text in Russian. Please analyze it and make up some questions to check a reader's understanding of it. Give concise answers to these questions.
The questions and answers should also be in Russian. Format your response as a NON-NUMBERED series of lines like `{QUESTION} | {ANSWER}`. Do NOT give any additional information.
"""

user_input = input("Please input RELATIVE path (from the location of THIS file) to the lesson you want to generate question/answer pairs to: ")

for heading, text in get_doc_in_sections(user_input):
    with model.chat_session(system_prompt=prompt):
        print(model.generate(heading + "\n" + text) + "\n")
