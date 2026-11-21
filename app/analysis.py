import math,os,time,tracemalloc
from .cipher import LWCipher,seal,open_
from math import erfc,sqrt
def monobit(bs):
    bits=[(x>>i)&1 for x in bs for i in range(8)];n=len(bits)
    return erfc(abs(2*sum(bits)-n)/sqrt(n)/sqrt(2))
def runs(bs):
    bits=[(x>>i)&1 for x in bs for i in range(8)];n=len(bits);pi=sum(bits)/n
    if abs(pi-.5)>=2/sqrt(n):return 0.0
    v=1+sum(bits[i]!=bits[i+1] for i in range(n-1))
    return erfc(abs(v-2*n*pi*(1-pi))/(2*sqrt(2*n)*pi*(1-pi)))
def entropy(bs):
    c=[0]*256
    for x in bs:c[x]+=1
    return -sum(k/len(bs)*math.log2(k/len(bs)) for k in c if k)
def avalanche(trials=20,n=64):
    tot=0
    for t in range(trials):
        k=bytearray(os.urandom(10));iv=os.urandom(8)
        a=LWCipher(bytes(k),iv).keystream(n);k[0]^=1<<(t%8)
        b=LWCipher(bytes(k),iv).keystream(n)
        tot+=sum(bin(x^y).count("1") for x,y in zip(a,b))/(n*8)
    return tot/trials
def security_report(n=20000):
    ks=LWCipher(os.urandom(10),os.urandom(8)).keystream(n)
    m,r=monobit(ks),runs(ks)
    return {"keystream_bytes":n,"monobit_p":round(m,4),"runs_p":round(r,4),"entropy_bits_per_byte":round(entropy(ks),4),
     "key_avalanche_ratio":round(avalanche(),4),"brute_force":"2^80 key space (~1.2e24 keys)",
     "known_plaintext":"KPA reveals keystream only; fresh 64-bit nonce per message prevents reuse",
     "pass_monobit":m>0.01,"pass_runs":r>0.01}
def benchmark(size=2048,rounds=5):
    key,pt=os.urandom(10),os.urandom(size);e=d=0
    tracemalloc.start()
    for _ in range(rounds):
        t=time.perf_counter();m=seal(key,os.urandom(8),pt);e+=time.perf_counter()-t
        t=time.perf_counter();open_(key,m);d+=time.perf_counter()-t
    peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
    e/=rounds;d/=rounds
    return {"payload_bytes":size,"encrypt_ms":round(e*1e3,3),"decrypt_ms":round(d*1e3,3),
      "throughput_KBps":round(size/1024/e,2),"peak_memory_KB":round(peak/1024,1),"overhead_bytes":16}
