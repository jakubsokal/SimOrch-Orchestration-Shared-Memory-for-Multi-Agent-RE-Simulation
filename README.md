# SimOrch-Orchestration-Shared-Memory-for-Multi-Agent-RE-Simulation

**py packages**</br>
cd src</br>
pip install -U langchain </br>
pip install -U langchain-openai</br>
pip install fastapi</br>
pip install fastapi uvicorn</br>
pip install sqlalchemy psycopg2-binary</br>
pip install websockets </br>

**UI**</br>
cd ui </br>
npm i</br>
npm i react-router-dom axios</br>
npm install @mui/material @emotion/react @emotion/styled</br>
npm install lucide-react</br>
npm install tailwindcss @tailwindcss/vite</br>

# how to run 
1. install all packages above.
2. Add a new scenario file or use an exising one (template can be found in '/scenarios' folder)
3. Open terminal and run following command 'python src/main.py --config FILE_NAME.yaml' or use this to run using predefined scenario 'python src/main.py --config scenario_001.yaml'
4. wait for conversation to be done.
5. next to view our results we can open the ui 
</br>
npm --prefix ui run dev</br>
python -m uvicorn src.api.app:app --reload</br>

#Local Run</br>
python -m src.main --config <scenario_name>.yaml</br>
