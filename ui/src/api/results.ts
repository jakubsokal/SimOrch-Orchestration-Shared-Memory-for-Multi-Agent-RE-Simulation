import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface EvalResultSummary {
  id: string;
  createdOn: string;
  sizeBytes: number;
}

export const getEvalResults = async (): Promise<EvalResultSummary[]> => {
  const response = await api.get('/results/');
  return response.data;
};

export const getEvalResultById = async (resultId: string): Promise<unknown> => {
  const response = await api.get(`/results/${encodeURIComponent(resultId)}`);
  return response.data;
};
