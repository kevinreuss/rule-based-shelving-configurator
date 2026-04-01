# Internal Shelving Quoting Tool — Prototype

A simplified B2B internal quoting tool for commercial shelving and retail fixtures. Enter shelving parameters (length, height, depth, color, options) and receive a complete bill of materials with generated SKUs, quantities, and pricing.

## What this demonstrates

- Rule-based configuration: shelving is divided into 1 m sections with calculated component counts
- SKU generation from dimensions and options
- Simplified pricing engine with per-component and per-color modifiers
- Clean separation between a Python API backend and a plain HTML/CSS/JS frontend

## Stack

| Layer    | Technology                            |
| -------- | ------------------------------------- |
| Backend  | Python, FastAPI, Pydantic             |
| Frontend | HTML, CSS, JavaScript (no frameworks) |

## Running locally

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API starts at **http://localhost:8000**. Verify with `GET /health`.

### 2. Frontend

Open `frontend/index.html` in a browser — no build step required.

> Make sure the backend is running on port 8000 so the frontend can reach the API.

## Note

This is a **simplified prototype for discussion purposes**. Pricing, SKU logic, and business rules are intentionally minimal and do not reflect a production system.
