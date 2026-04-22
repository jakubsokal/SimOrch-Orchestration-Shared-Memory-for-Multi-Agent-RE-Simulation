import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAllRuns = async (): Promise<unknown> => {
  try {
    const response = await api.get('/runs/');

    return response.data;
  } catch (error) {
    console.error('Error fetching runs:', error);
    throw error;
  }
};

export const getRunById = async (runId: string | number): Promise<unknown> => {
  try {
    const id = String(runId);
    if (id.includes('/')) {
      const [scenarioId, nestedRunId] = id.split('/', 2);
      const response = await api.get(`/runs/${scenarioId}/${nestedRunId}`);
      return response.data;
    }

    const response = await api.get(`/runs/${id}`);

    return response.data;
  } catch (error) {
    console.error(`Error fetching run ${runId}:`, error);
    throw error;
  }
};

export const getScenarios = async (): Promise<unknown> => {
  try {
    const response = await api.get('/runs/scenarios');
    return response.data;
  } catch (error) {
    console.error('Error fetching scenarios:', error);
    throw error;
  }
};