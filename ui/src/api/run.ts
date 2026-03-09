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
    const response = await api.get(`/runs/${runId}`);

    return response.data;
  } catch (error) {
    console.error(`Error fetching run ${runId}:`, error);
    throw error;
  }
};