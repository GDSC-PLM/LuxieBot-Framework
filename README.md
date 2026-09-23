# Overview

This bot is about making the GDGoC discord server more lively and easier to navigate. It’s being developed to integrate the organizations’ main resources (mainly Notion) to have a better experience for Googlers and Nooglers alike. This is catered for all members of the organization, with varying read and write permissions.

## Table of Contents

| Section                                     | Component / Sub-section                                       | Description                                         |
| :------------------------------------------ | :------------------------------------------------------------ | :-------------------------------------------------- |
| **[Architecture](#architecture)**           | [Frontend](#frontend)                                         | Discord.js bot & Next.js dashboard stack            |
|                                             | [Backend](#backend)                                           | Bun runtime, FastAPI core, and Docker orchestration |
| **[Environment Setup](#environment-setup)** | [Discord Bot & Dashboard](#spin-up-discord-bot-and-dashboard) | Step-by-step setup using Bun                        |
|                                             | [Python Backend](#spin-up-python-backend)                     | Virtual environment and dependency configuration    |

## Architecture

The Luxie Framework uses a monorepo + microservices setup that power its frontend and backend.

### Frontend

- Discord.js for Discord Bot (Interface used by members of the GDGoC-PLM Discord Server)
- Next.js for Dashboard Frontend & Backend (Integrates with FastAPI)

### Backend

- Bun for JavaScript runtime
- Python via FastAPI (Business Logic)
- Docker Compose for Containerization and Microservices Orchestration

## Environment Setup

### Spin up Discord Bot and Dashboard

#### Navigate to Discord Bot

```bash
cd ./services/bot
```

#### Build Bot

```bash
bun run build
```

#### Start Bot

```bash
bun run start
```

#### Navigate to Dashboard

```bash
# Assuming you're currently in /luxie-framework/services/bot/
cd ../
cd ./services/dashboard
```

#### Start Dashboard

```bash
bun run dev
```

### Spin up Python Backend

#### Navigate to Python Backend

```bash
cd ./services/core/
```

#### Create Virtual Environment (venv)

```bash
python -m venv .venv
```

#### Activate the Virtual Environment

Depending on your machine, run **one** of the following:

- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

#### Install Dependencies

Make sure your virtual environment is active before running this:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
