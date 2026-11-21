"""LFSR + NLFSR stream cipher (Grain-v1-inspired, educational). 80-bit key, 64-bit nonce."""
import hmac, hashlib
class LWCipher:
    def __init__(self, key: bytes, iv: bytes):
        assert len(key)==10 and len(iv)==8
        self.b=[(key[i//8]>>(i%8))&1 for i in range(80)]
        self.s=[(iv[i//8]>>(i%8))&1 for i in range(64)]+[1]*16
        for _ in range(160):
            z=self._out(); self._clock(z)
    def _out(self):
        s,b=self.s,self.b
        x0,x1,x2,x3,x4=s[3],s[25],s[46],s[64],b[63]
        h=(x1^x4^(x0&x3)^(x2&x3)^(x3&x4)^(x0&x1&x2)^(x0&x2&x3)^(x0&x2&x4)^(x1&x2&x4)^(x2&x3&x4))
        return (b[1]^b[2]^b[4]^b[10]^b[31]^b[43]^b[56]^h)&1
    def _clock(self,fb=0):
        s,b=self.s,self.b
        fs=s[62]^s[51]^s[38]^s[23]^s[13]^s[0]^fb
        fb_=(s[0]^b[62]^b[60]^b[52]^b[45]^b[37]^b[33]^b[28]^b[21]^b[14]^b[9]^b[0]
          ^(b[63]&b[60])^(b[37]&b[33])^(b[15]&b[9])^(b[60]&b[52]&b[45])^(b[33]&b[28]&b[21])
          ^(b[63]&b[45]&b[28]&b[9])^(b[60]&b[52]&b[37]&b[33])^(b[63]&b[60]&b[21]&b[15])
          ^(b[63]&b[60]&b[52]&b[45]&b[37])^(b[33]&b[28]&b[21]&b[15]&b[9])
          ^(b[52]&b[45]&b[37]&b[33]&b[28]&b[21])^fb)
        s.pop(0);s.append(fs);b.pop(0);b.append(fb_)
    def keystream(self,n:int)->bytes:
        out=bytearray()
        for _ in range(n):
            v=0
            for i in range(8):
                v|=self._out()<<i; self._clock()
            out.append(v)
        return bytes(out)
    def crypt(self,data:bytes)->bytes:
        return bytes(a^b for a,b in zip(data,self.keystream(len(data))))
TAG=8
def _mk(key): return hashlib.sha256(b"mac"+key).digest()
def seal(key:bytes,nonce:bytes,pt:bytes)->bytes:
    ct=LWCipher(key,nonce).crypt(pt)
    return nonce+ct+hmac.new(_mk(key),nonce+ct,hashlib.sha256).digest()[:TAG]
def open_(key:bytes,msg:bytes)->bytes:
    n,ct,tag=msg[:8],msg[8:-TAG],msg[-TAG:]
    if not hmac.compare_digest(tag,hmac.new(_mk(key),n+ct,hashlib.sha256).digest()[:TAG]):
        raise ValueError("integrity check failed")
    return LWCipher(key,n).crypt(ct)
