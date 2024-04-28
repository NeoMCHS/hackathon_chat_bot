#Creates plain text representations of the lectures

import pypandoc
from transformers import pipeline
from pathlib import Path

pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-en")

def main():
    pathlist = Path("train_Assessor/materials/introduction").glob('**/*.*')
    for path in pathlist:
        file_name = path.name
        pypandoc.convert_file(str(path), 'plain', outputfile=f"train_Assessor/materials/introduction_processed/{file_name[:-5]}.txt")
    pathlist = Path("train_Assessor/materials/process").glob('**/*.*')
    for path in pathlist:
        file_name = path.name
        pypandoc.convert_file(str(path), 'plain', outputfile=f"train_Assessor/materials/introduction_processed/{file_name[:-5]}.txt")

main()