from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import spacy
import re

app = FastAPI()

# Load SpaCy transformer model
nlp = spacy.load("en_core_web_trf")

# Regex patterns
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?)?((3\d{2})[-.\s]?\d{7})\b"
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

class TextInput(BaseModel):
    text: str

def extract_info(text: str):
    doc = nlp(text)

    emails = re.findall(EMAIL_REGEX, text)
    phone_numbers = re.findall(PHONE_REGEX, text)
    phone_numbers = ["".join(number).strip() for number in phone_numbers if number]

    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    addresses = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]
    organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    return {
        "Names": list(set(names)),
        "Emails": list(set(emails)),
        "Phone Numbers": list(set(phone_numbers)),
        "Addresses": list(set(addresses)),
        "Organizations": list(set(organizations))
    }

@app.post("/extract")
async def extract_text(data: TextInput):
    result = extract_info(data.text)
    return result
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
