# SikLayag Installation Guide

## Prerequisites

- Windows with PowerShell (commands below), Git, and Python 3.10 or later.
- Internet access to install Python dependencies and use academic search.
- A Semantic Scholar API key is optional. Searches may be rate-limited without one.

## Local setup

1. Clone the repository and enter its directory:

   ```powershell
   git clone https://github.com/fuhlisuhtee/SikLayag.git
   cd SikLayag
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the appropriate execution policy allowed on your machine or run the environment's Python directly as `.\.venv\Scripts\python.exe`.

3. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Configure the optional API key:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Set `SEMANTIC_SCHOLAR_API_KEY` in `.env`. Keep this file private; it is ignored by Git. The application loads it locally through `python-dotenv`.

5. Start the development server:

   ```powershell
   py app.py
   ```

6. Open <http://127.0.0.1:5000>. Check <http://127.0.0.1:5000/api/health> for the health response.

## Hosted deployment

The repository includes starter Render and Gunicorn configuration in `render.yaml` and `Procfile`; deployment setup is not finalized. Set `SEMANTIC_SCHOLAR_API_KEY` in the hosting provider's private environment settings. Do not deploy the local `.env` file. The current limiter and search cache are in-process, so the supplied single-worker configuration is intended to keep their state together.

## Optional project checks

The repository README documents the current Python and JavaScript checks. Install Node.js if you want to run the JavaScript syntax or citation tests; Node.js is not required to run the application.
