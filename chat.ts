import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ChatRequest {
  prompt: string;
  max_tokens?: number;
  temperature?: number;
}

export interface ChatResponse {
  response: string;
  prompt: string;
}

export interface ModelInfo {
  model_repo: string;
  model_file: string;
  max_tokens: number;
  temperature: number;
  top_p: number;
  loaded: boolean;
}

export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await axios.post<ChatResponse>(`${API_URL}/chat`, request);
  return response.data;
};

export const getModelInfo = async (): Promise<ModelInfo> => {
  const response = await axios.get<ModelInfo>(`${API_URL}/model-info`);
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string; model_loaded: boolean }> => {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
};
