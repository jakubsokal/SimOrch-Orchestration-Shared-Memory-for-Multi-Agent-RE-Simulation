# SimOrch-Orchestration-Shared-Memory-for-Multi-Agent-RE-Simulation

**py packages**
pip install -U langchain
pip install -U langchain-openai
pip install fastapi
pip install fastapi uvicorn
pip install sqlalchemy psycopg2-binary
pip install websockets

**UI**
npm create vite@latest ui -- --template react-ts
cd ui 
npm i
npm i react-router-dom axios
npm install @mui/material @emotion/react @emotion/styled
npm install lucide-react
npm install tailwindcss @tailwindcss/vite

# how to run 
1. install all packages above.
2. Add a new scenario file or use an exising one (template can be found in '/scenarios' folder)
3. Open terminal and run following command 'python src/main.py --config FILE_NAME.yaml' or use this to run using predefined scenario 'python src/main.py --config scenario_001.yaml'
4. wait for conversation to be done.
5. next to view our results we can open the ui 

npm --prefix ui run dev
python -m uvicorn src.api.app:app --reload

#Local Run
python -m src.main --config <scenario_name>.yaml