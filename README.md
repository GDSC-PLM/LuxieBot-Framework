# Luxie Framework

This bot is about making the GDGoC discord server more lively and easier to navigate. It’s being developed to integrate the organizations’ main resources (mainly Notion) to have a better experience for Googlers and Nooglers alike. This is catered for all members of the organization, with varying read and write permissions.

## Table of Contents

| Section                                     | Component / Sub-section                                       | Description                                         |
| :------------------------------------------ | :------------------------------------------------------------ | :-------------------------------------------------- |
| **[Architecture](#architecture)**           | [Frontend](#frontend)                                         | Discord.js bot & Next.js dashboard stack            |
|                                             | [Backend](#backend)                                           | Bun runtime, FastAPI core, and Docker orchestration |
| **[Environment Setup](#environment-setup)** | [Docker Compose](#recommended---docker-compose)               | All-in-one orchestrator                             |
|                                             | [Discord Bot & Dashboard](#spin-up-discord-bot-and-dashboard) | Step-by-step setup using Bun                        |
|                                             | [Python Backend](#spin-up-python-backend)                     | Virtual environment and dependency configuration    |

## Overview

```
root
├── services
│    ├── bot
│    ├── dashboard
│    └── core
└── shared/sdk/@luxie-framework/sdk
```

The `services` folder contains all the microservices needed for Luxie to run.

- `bot` is a node/bun module. It runs the Discord Bot API via Discord.js.
- `dashboard` is also a node/bun module. It uses Next.js to display a role-based dashboard where users can login via OAuth; admins can freely modify the bot behavior and rewards, whereas normal users can login to view their status in the GDGoC Discord Server.
- `core` is a Python backend. It uses JWT authorization to manage both the `bot` and `dashboard` sessions.

## Architecture

The Luxie Framework uses a polyglot monorepo + microservices setup that power its frontend and backend.

### Frontend

- Discord.js for Discord Bot (Interface used by members of the GDGoC-PLM Discord Server)
- Next.js for Dashboard Frontend & Backend (Integrates with FastAPI)

### Backend

- Bun for JavaScript runtime
- Python via FastAPI (Business Logic)
- Docker Compose for Containerization and Microservices Orchestration

## Environment Setup

### Recommended - Docker Compose

TODO

### Manual Setup - Spin up Discord Bot and Dashboard

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
# Assuming you're currently in /LuxieBot-Framework/services/bot/
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

#### Select Python Interpreter (VS Code)

This is important because you'd want your IDE to recognize imports and such.

```
CTRL + Shift + P
Look for "Python: Select Interpreter"
Enter interpreter path...
Find...
Locate the .venv folder within LuxieBot-Framework
Open the Scripts folder inside, and then look for Python.exe
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
