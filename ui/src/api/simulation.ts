import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const initiateSimulation = async (
    config: any): Promise<unknown> => {
    try {
        const response = await api.post('/initiate/', config);

        return response.data;
    } catch (error) {
        console.error('Error initiating simulation:', error);
        throw error;
    }
};