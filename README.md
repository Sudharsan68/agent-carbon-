# AgentCarbon

AgentCarbon is a comprehensive Carbon Footprint Analysis System designed to accurately measure, track, and forecast carbon emissions. 

## Project Structure

This project is divided into two main components:
- **Backend:** A robust API built with Python and FastAPI, handling calculations, AI predictions, and RAG-based explanations.
- **Frontend:** A modern, interactive web application built with React, Vite, and Tailwind CSS.

---

## Getting Started

Follow the instructions below to set up and run both the frontend and backend locally.

### Prerequisites
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js / npm](https://nodejs.org/en) (or [Bun](https://bun.sh/))

---

### Running the Backend (FastAPI)

1. **Navigate to the backend directory:**
   ```bash
   cd agentcarbon/backend
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   *The backend API will run at `http://localhost:8000` (Access the interactive API docs at `http://localhost:8000/docs`).*

---

### Running the Frontend (React + Vite)

1. **Navigate to the frontend directory:**
   ```bash
   cd agentcarbon/frontend/carbon-footprint-insights
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # Or if you are using Bun: bun install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   # Or if you are using Bun: bun run dev
   ```
   *The local server will start, typically accessible at `http://localhost:5173` (check the terminal output for the exact URL).*
