# SecureCity —- Lightweight Stream Cipher for Smart City IoT

A software-only demonstration of encrypted Smart City IoT communication using an educational LFSR/NLFSR-based stream cipher.

SecureCity generates simulated sensor readings, encrypts them, verifies message integrity, and displays the decrypted results through a web dashboard. It also includes basic statistical checks and performance measurements.

> Academic prototype: this project demonstrates cryptographic concepts. It is not an independently audited cipher and must not be used to protect sensitive or production data.

---

## Project Overview

Smart City applications exchange information from traffic systems, environmental monitors, street lights, and parking sensors.

This project demonstrates how those messages can be encrypted and checked for modification without requiring physical IoT hardware.

The application includes:

- A simulated IoT sensor data generator.
- An educational stream cipher combining linear and nonlinear feedback shift registers.
- An HMAC-based message integrity check.
- A FastAPI backend for message generation, ingestion, and analysis.
- A responsive web dashboard with plain-language results.
- Automated cipher tests.
- A Docker configuration for container-based deployment.

The sensor generator and central server run within the same application. They represent separate roles in an IoT communication workflow.

## Features

### Simulated Smart City Sensors

Generate sample readings for four use cases:

| Sensor | Generated Values |
|---|---|
| Traffic | Vehicle count and average speed |
| Environment | PM2.5 value and temperature |
| Street lighting | Lamp status and ambient brightness |
| Parking | Available parking spaces |

All readings are randomly generated. The application does not connect to real cameras, physical sensors, or external data services.

### Encryption and Decryption

- Generates a keystream using an LFSR/NLFSR-based design.
- Encrypts plaintext using an XOR operation with the keystream.
- Decrypts ciphertext by applying the same operation with the same key and nonce.
- Uses an 80-bit key and a 64-bit nonce.
- Performs 160 initialization rounds before generating message keystream.

### Message Integrity

- Uses HMAC-SHA256 with an 8-byte truncated tag.
- Authenticates the nonce and ciphertext.
- Checks the tag before decrypting.
- Rejects packets that fail integrity verification.

### Interactive Dashboard

- Send individual sensor readings.
- View the original reading, encrypted packet, and recovered message.
- Modify a packet to demonstrate integrity verification.
- Run basic statistical checks.
- Measure encryption and decryption performance.
- View recently accepted server records.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Application server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Validation | Pydantic |
| Cryptographic utilities | Python `hashlib` and `hmac` |
| Testing | Pytest |
| Containerization | Docker |
| Hardware | Not required |

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── cipher.py           # Keystream generation, encryption, and integrity
│   ├── analysis.py         # Statistical checks and performance measurements
│   └── main.py             # FastAPI endpoints and sensor simulation
├── static/
│   └── index.html          # Dashboard
├── Dockerfile
├── render.yaml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer recommended.
- `pip`.
- A modern web browser.
- Git, if cloning the repository.

Run all commands from the project root, where `requirements.txt` is located.

### 1. Download the Project

Download and extract the repository ZIP, then open the extracted folder in your terminal or VS Code.

Alternatively, clone the repository using its GitHub URL.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Environment

Windows Command Prompt:

```bat
venv\Scripts\activate.bat
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Start the Server

```bash
python -m uvicorn app.main:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

The `--reload` option is intended for development.

### 6. Stop the Application

Press:

```text
Ctrl + C
```

Then exit the virtual environment:

```bash
deactivate
```

## Using the Dashboard

### Send a Sensor Reading

Select Traffic camera, Air quality, Street light, or Parking spot.

The dashboard displays:

1. Sensor says: the original simulated reading.
2. Travels scrambled: the encrypted packet.
3. Server understands: the recovered reading after integrity verification and decryption.

A successful request returns an accepted response.

### Demonstrate Packet Tampering

Select Hacker changes data.

The dashboard changes one bit of a generated packet before sending it to the server. The packet should fail integrity verification and be rejected.

This demonstrates detection of a modified packet. It is not a complete penetration test or proof of security against every attack.

### Check Security

Select Check security to inspect:

- Monobit balance.
- Runs test.
- Byte-frequency entropy.
- Key avalanche behavior.

These are exploratory checks, not a complete security evaluation.

### Check Speed

Select Check speed to measure:

- Encryption time.
- Decryption time.
- Encryption throughput.
- Peak traced Python memory.
- Packet overhead.

### Show Server Data

Select Show server data to view recently accepted readings.

Records are stored in memory and disappear when the application restarts.

## Communication Workflow

```text
Simulated sensor
       |
       v
JSON sensor reading
       |
       v
Stream-cipher encryption
       |
       v
Nonce + ciphertext + integrity tag
       |
       v
Browser forwards packet to ingestion endpoint
       |
       v
Integrity verification
       |
       +---- Invalid tag ----> Reject packet
       |
       v
Decrypt ciphertext
       |
       v
Store accepted reading in memory
       |
       v
Display result on dashboard
```

### Important Simulation Detail

The backend generates both the plaintext and encrypted packet, and the browser forwards that packet to the ingestion endpoint.

The demonstration also deliberately displays plaintext to make the process understandable. It does not model a production deployment in which plaintext remains exclusively on a separate physical sensor.

## Cryptographic Design

### Educational Stream Cipher

The cipher is inspired by Grain-style LFSR/NLFSR constructions.

It combines:

- An 80-bit linear feedback shift register.
- An 80-bit nonlinear feedback shift register.
- A nonlinear output function.
- A key and nonce initialization phase.

It is a custom educational implementation, not a certified or verified implementation of the Grain standard.

### Encryption

The ciphertext is generated by XORing the plaintext with the keystream:

```text
ciphertext = plaintext XOR keystream
```

Decryption uses the same operation:

```text
plaintext = ciphertext XOR keystream
```

The key and nonce must match those used during encryption.

### Packet Format

```text
+----------------+---------------------+----------------+
| Nonce: 8 bytes | Ciphertext: N bytes | Tag: 8 bytes   |
+----------------+---------------------+----------------+
```

The cryptographic packet overhead is 16 bytes.

This excludes Base64 encoding, JSON, HTTP headers, and other transport overhead.

### Integrity Verification

The application uses an encrypt-then-MAC structure:

```text
tag = HMAC-SHA256(mac_key, nonce || ciphertext)[:8]
```

The implementation derives the MAC key by hashing a fixed label and the encryption key.

The server compares the received tag with the expected tag before decrypting the message.

For a production system, use a reviewed authenticated-encryption construction and an appropriate key-management design instead.

### Nonce Handling

The application generates an 8-byte random nonce for each message.

Random generation does not guarantee that nonces will never repeat. Reusing the same key and nonce reuses the keystream, which can expose relationships between plaintext messages.

The prototype does not implement persistent nonce tracking, per-device counters, or replay protection.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Open the dashboard |
| GET | `/docs` | Open interactive API documentation |
| GET | `/api/simulate/{kind}` | Generate and encrypt a sensor reading |
| POST | `/api/ingest` | Verify and decrypt a packet |
| GET | `/api/records` | Return up to 50 recent accepted readings |
| GET | `/api/security` | Run statistical checks |
| GET | `/api/benchmark?size=1024` | Measure performance for a payload size |

Supported `kind` values:

```text
traffic
environment
lighting
parking
```

### Ingest Request Format

```json
{
  "packet_b64": "<Base64-encoded encrypted packet>"
}
```

A valid packet returns an accepted response with the decoded reading and decryption time.

A packet that fails verification returns HTTP `400`.

## Security Evaluation

### Implemented Checks

| Check | What It Examines |
|---|---|
| Monobit test | Balance between zero and one bits |
| Runs test | Sequences of consecutive identical bits |
| Byte entropy | Distribution of byte values |
| Key avalanche check | Output changes after flipping one key bit |
| Tampering test | Rejection of a modified packet |
| Wrong-key test | Rejection when a different key is used |

Statistical results vary between runs because fresh random samples are used.

A statistical test can occasionally fail even for a random source. Conversely, passing these tests does not establish resistance to cryptanalysis.

### Not Established by This Project

The project does not prove resistance to:

- Known-plaintext cryptanalysis.
- Chosen-plaintext cryptanalysis.
- State-recovery attacks.
- Algebraic or correlation attacks.
- Side-channel attacks.
- Exhaustive cryptographic analysis.

An 80-bit key has a theoretical key space of `2^80`, but key-space size alone does not establish the effective security of a custom cipher.

Knowing part of a plaintext reveals the corresponding keystream segment. Fresh nonces help avoid keystream reuse, but do not by themselves prove resistance to state recovery or other attacks.

## Performance Evaluation

The benchmark measures encryption and integrity-tag generation together, and integrity verification and decryption together.

It reports:

| Metric | Meaning |
|---|---|
| Encryption time | Average time to encrypt and authenticate a payload |
| Decryption time | Average time to verify and decrypt a packet |
| Throughput | Plaintext processed per second during encryption |
| Peak memory | Peak allocations traced by Python `tracemalloc` |
| Packet overhead
