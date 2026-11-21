import os,json,base64,random,time
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .cipher import seal,open_
from .analysis import security_report,benchmark
app=FastAPI(title="Lightweight Stream Cipher - Smart City IoT")
KEY=bytes.fromhex(os.getenv("CIPHER_KEY_HEX","00112233445566778899"))
DB=[]
class Packet(BaseModel): packet_b64:str
def sensor(kind):
    g={"traffic":lambda:{"vehicles":random.randint(0,80),"speed_kmph":random.randint(10,70)},
       "environment":lambda:{"pm25":round(random.uniform(10,200),1),"temp_c":round(random.uniform(15,40),1)},
       "lighting":lambda:{"lamp_on":random.random()>.4,"lux":random.randint(0,300)},
       "parking":lambda:{"free_slots":random.randint(0,50)}}
    if kind not in g:raise HTTPException(400,"unknown sensor")
    return {"type":kind,"ts":time.time(),**g[kind]()}
@app.get("/api/simulate/{kind}")
def simulate(kind:str):
    pt=json.dumps(sensor(kind)).encode();t=time.perf_counter()
    pkt=seal(KEY,os.urandom(8),pt)
    return {"plaintext":pt.decode(),"packet_hex":pkt.hex(),"packet_b64":base64.b64encode(pkt).decode(),"encrypt_ms":round((time.perf_counter()-t)*1e3,3)}
@app.post("/api/ingest")
def ingest(p:Packet):
    t=time.perf_counter()
    try:data=json.loads(open_(KEY,base64.b64decode(p.packet_b64)))
    except Exception:raise HTTPException(400,"integrity/decryption failure")
    DB.append(data);return {"status":"accepted","data":data,"decrypt_ms":round((time.perf_counter()-t)*1e3,3)}
@app.get("/api/records")
def records():return DB[-50:]
@app.get("/api/security")
def sec():return security_report()
@app.get("/api/benchmark")
def bench(size:int=1024):return benchmark(min(size,65536))
@app.get("/")
def home():return FileResponse("static/index.html")
