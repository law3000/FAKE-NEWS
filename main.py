# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy, os, hashlib, json, redis
from dotenv import load_dotenv

load_dotenv()

nlp = spacy.load("en_core_web_sm")
rdb = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

api = FastAPI()

class VerifyRequest(BaseModel):
    text: str

class ClaimOut(BaseModel):
    claim: str

def _hash(txt: str) -> str:
    return hashlib.sha256(txt.lower().strip().encode()).hexdigest()

@api.get("/health")
def health():
    return {"status": "ok"}

@api.post("/verify", response_model=list[ClaimOut])
def verify(req: VerifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    key = _hash(req.text)
    if cached := rdb.get(key):
        return json.loads(cached)

    doc = nlp(req.text)
    claims = [
        {"claim": sent.text.strip()}
        for sent in doc.sents
        if any(tok.like_num or tok.text == "%" for tok in sent)
    ]
    rdb.setex(key, 60 * 60 * 24, json.dumps(claims))  # 24 h TTL
    return claims
