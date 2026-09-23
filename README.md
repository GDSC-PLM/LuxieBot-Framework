# Overview

This bot is about making the GDGoC discord server more lively and easier to navigate. It’s being developed to integrate the organizations’ main resources (mainly Notion) to have a better experience for Googlers and Nooglers alike. This is catered for all members of the organization, with varying read and write permissions.

## Tech Stack

This bot uses a monorepo setup with microservices that power its frontend and backend.

### Frontend

- Discord.js for Discord Bot (Interface used by members of the GDGoC-PLM Discord Server)
- Next.js for Dashboard Frontend & Backend (Integrates with FastAPI)

### Backend

- Bun for JavaScript runtime
- Python via FastAPI (Business Logic)
- Docker Compose for Containerization and Microservices Orchestration
