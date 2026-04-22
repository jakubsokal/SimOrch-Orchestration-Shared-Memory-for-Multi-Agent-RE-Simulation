# SimOrch-Orchestration-Shared-Memory-for-Multi-Agent-RE-Simulation

## Setup

### Python
Create/activate your virtual environment, then install dependencies open new bash terminal:

```bash
cd src
pip install -r imports.txt
```

### UI
Dependencies are pinned in ui/package.json, open new bash terminal:

```bash
cd ui
npm install
```

## How to run
1. Add a new scenario file or use an existing one (templates in /scenarios).
2. Run a simulation locally (writes logs under /runs):

```bash
python -m src.main --config scenario_001.yaml
```

3. Start the API:

```bash
python -m uvicorn src.api.app:app --reload
```

4. Start the UI:

```bash
npm --prefix ui run dev
```

In the UI you can pick a predefined scenario or create a custom one by following the steps.

## Notes
- If using OLLAMA, install Ollama and pull a model locally before running (e.g. `ollama pull <model>`).
- If using predefined scenarios, either change the provider to ollama and model to <model> or if you have an openai api key create a .env folder in src using the .env.example
