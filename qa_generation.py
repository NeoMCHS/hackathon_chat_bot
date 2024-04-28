from pathlib import Path
from docx import Document
import yake
import pandas as pd
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from pymystem3 import Mystem
import time

mystem = Mystem()

model = SentenceTransformer("distiluse-base-multilingual-cased-v1")

model_name = "timpal0l/mdeberta-v3-base-squad2"

nlp = pipeline('question-answering', model=model_name)

def get_full_txt(directory, file):
    file = open(f"train_Assessor/materials/{directory}_processed/{file}.txt", "r")
    raw_text = file.read()
    return raw_text

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

def extract_keywords(question: str):
    language = "ru"
    max_ngram_size = 1
    deduplication_threshold = 0.1
    windowSize = 1
    numOfKeywords = 3
    extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, windowsSize=windowSize, top=numOfKeywords, features=None)
    keywords = extractor.extract_keywords(question)
    output = []
    for kw in keywords:
        output.append(kw[0])
    print(output)
    return output
    

def find_context(keywords: list, paragraphs: list):
    start_find = time.time()
    candidates = []
    for section in paragraphs:
        text = section[1]
        words = text.split()
        for word in words:
            if word in keywords:
                candidates.append(text)
    print("Finding time - %s seconds" % (time.time() - start_find))
    return candidates
                
def gen_ans_bert(question, text):
    res = nlp(question=question, context=text)
    print(res)
    return res

def pipeline(question=None, lesson=None, user_input=None, pos=None, csv_file=None):
    if not csv_file == None:
        df = pd.read_csv(csv_file, header=0, usecols=["Question", "Lesson", "Answer", "Correctness"])

    is_correct = False
    if question == None or lesson == None:
        question = df["Question"][pos]
        lesson = df["Lesson"][pos].split("_", 1)
        directory = lesson[0]
        file = lesson[1]
    else:
        int_lesson = lesson.split("_", 1)
        directory = int_lesson[0]
        file = int_lesson[1]

    keywords = extract_keywords(question)

    paraphs = get_doc_in_sections(f"train_Assessor/materials/{directory}/{file}.docx")

    candidates = find_context(keywords, paraphs)

    answer_candidates = []

    if len(candidates) >= 6:
        candidate = get_full_txt(directory=directory, file=file)
        answer_candidates.append(gen_ans_bert(question, candidate))
        candidates = []
    for candidate in candidates:
        answer = gen_ans_bert(question, candidate)
        answer_candidates.append(answer)
    for answer_candidate in answer_candidates:  
        print(list(answer_candidate.values())[0])
        if list(answer_candidate.values())[0] < 0.1:
            answer_candidates.remove(answer_candidate)
    if answer_candidates == []:    
        candidate = get_full_txt(directory=directory, file=file)
        answer_candidates.append(gen_ans_bert(question, candidate))

    if user_input == None:
        user_answer = df["Answer"][pos]
    else:
        user_answer = user_input

    similarities = []

    for answer in answer_candidates:    
        answer_text = list(answer.values())[3]
        lemmas_answer = mystem.lemmatize(answer_text)
        lemmas_answer = set([l for l in lemmas_answer if l.isalpha()])
        lemmas_usr_answer = mystem.lemmatize(user_answer)
        lemmas_usr_answer = set([l for l in lemmas_usr_answer if l.isalpha()])
        intersection = lemmas_answer.intersection(lemmas_usr_answer)
        union = lemmas_answer.union(lemmas_usr_answer)
        similarity = float(len(intersection)) / len(union)
        similarities.append(similarity)

    print(similarities)

    for similarity in similarities: 
        if similarity > 0.09:
            is_correct = True

    if is_correct == False: 
        return 0

    if is_correct == True:
        return 1

def csv_pipeline():
    start_time = time.time()
    total_batch = 0
    correct_in_batch = 0
    df = pd.read_csv("test_data.csv", header=0, usecols=["Question", "Lesson", "Answer", "hash"])
    print(df.shape[0])
    submission = []
    for i in range(df.shape[0]):
        question = df["Question"][i]
        lesson = df["Lesson"][i]
        answer = df["Answer"][i]
        hash = df["hash"][i]
        print(f"{question} - {lesson} - {answer} - {hash}")
        correctness = pipeline(question=question, lesson=lesson, user_input=answer)
        dictionary = {"hash": hash, "Correctness": correctness}
        submission.append(dictionary)

    print(submission)

    fields = ['hash', 'Correctness']
    
    # name of csv file
    filename = "submission.csv"
    
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)
    
        # writing headers (field names)
        writer.writeheader()
    
        # writing data rows
        writer.writerows(submission)

    print("Execution time - %s seconds" % (time.time() - start_time))
