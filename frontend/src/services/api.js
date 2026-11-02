// frontend/src/services/api.js

export function getToken() {
  return localStorage.getItem('token') || '';
}

export function setToken(token) {
  if (token) {
    localStorage.setItem('token', token);
  } else {
    localStorage.removeItem('token');
  }
}

export function removeToken() {
  localStorage.removeItem('token');
}

export async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = options.headers ? { ...options.headers } : {};

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Nếu không gửi FormData thì mặc định là application/json
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeToken();
    window.dispatchEvent(new CustomEvent('auth-expired'));
  }

  return response;
}

// 1. Auth API
export async function apiLogin(username, password) {
  const res = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  return res;
}

export async function apiRegister(fullname, username, email, password) {
  const res = await apiRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      full_name: fullname,
      username,
      email,
      password,
    }),
  });
  return res;
}

export async function apiGetMe() {
  const res = await apiRequest('/api/auth/me', { method: 'GET' });
  return res;
}

export async function apiChangePassword(oldPassword, newPassword) {
  const res = await apiRequest('/api/auth/change-password', {
    method: 'POST',
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  });
  return res;
}

// 2. Results & History API
export async function apiGetResults(search = '', limit = 50, offset = 0) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  params.append('limit', limit);
  params.append('offset', offset);

  const res = await apiRequest(`/api/results?${params.toString()}`, { method: 'GET' });
  return res;
}

export async function apiGetResultDetail(id) {
  const res = await apiRequest(`/api/results/${id}`, { method: 'GET' });
  return res;
}

export async function apiUpdateResult(id, payload) {
  const res = await apiRequest(`/api/results/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
  return res;
}

export async function apiDeleteResult(id) {
  const res = await apiRequest(`/api/results/${id}`, { method: 'DELETE' });
  return res;
}

export async function apiGetHistory() {
  const res = await apiRequest('/api/history', { method: 'GET' });
  return res;
}

// 3. Statistics & AI Corrections API
export async function apiGetStatistics() {
  const res = await apiRequest('/api/statistics', { method: 'GET' });
  return res;
}

export async function apiGetDemographics() {
  const res = await apiRequest('/api/statistics/demographics', { method: 'GET' });
  return res;
}

export async function apiGetAIQuality() {
  const res = await apiRequest('/api/statistics/ai-quality', { method: 'GET' });
  return res;
}

export async function apiGetCorrections() {
  const res = await apiRequest('/api/corrections', { method: 'GET' });
  return res;
}

// 4. OCR & Camera Probe API
export function getUserAIKey() {
  return localStorage.getItem('cccd_user_ai_key') || '';
}

export function setUserAIKey(key, provider = 'gemini') {
  if (key) {
    localStorage.setItem('cccd_user_ai_key', key.trim());
    localStorage.setItem('cccd_user_ai_provider', provider);
  } else {
    localStorage.removeItem('cccd_user_ai_key');
  }
}

export function getUserAIProvider() {
  return localStorage.getItem('cccd_user_ai_provider') || 'gemini';
}

export function removeUserAIKey() {
  localStorage.removeItem('cccd_user_ai_key');
}

export async function apiGetEvaluateStatus() {
  const res = await apiRequest('/predict/evaluate-status', { method: 'GET' });
  return res;
}

export async function apiTestEvaluateKey(apiKey = '', provider = 'gemini') {
  const formData = new FormData();
  if (apiKey) formData.append('api_key', apiKey.trim());
  formData.append('provider', provider);

  const res = await apiRequest('/predict/evaluate-test-key', {
    method: 'POST',
    body: formData,
  });
  return res;
}

export async function apiEvaluateOnDemand(fileOrBlob, localData) {
  const formData = new FormData();
  formData.append('file', fileOrBlob);
  formData.append('local_data_json', JSON.stringify(localData));

  const userKey = getUserAIKey();
  const provider = getUserAIProvider();
  const headers = {};
  if (userKey) {
    headers['X-AI-API-Key'] = userKey;
  }
  headers['X-AI-Provider'] = provider;

  const res = await apiRequest('/predict/evaluate-on-demand', {
    method: 'POST',
    headers,
    body: formData,
  });
  return res;
}

export async function apiPredictImage(fileOrBlob, inputSource = 'IMAGE', evaluateWithAi = false) {
  const formData = new FormData();
  formData.append('file', fileOrBlob, fileOrBlob.name || 'cccd_upload.jpg');
  formData.append('input_source', inputSource);
  if (evaluateWithAi) {
    formData.append('evaluate_with_ai', 'true');
  }

  const userKey = getUserAIKey();
  const provider = getUserAIProvider();
  const headers = {};
  if (userKey) {
    headers['X-AI-API-Key'] = userKey;
  }
  headers['X-AI-Provider'] = provider;

  const res = await apiRequest('/predict/image', {
    method: 'POST',
    headers,
    body: formData,
  });
  return res;
}

export async function apiProbeCamera(fileOrBlob, signal) {
  const formData = new FormData();
  formData.append('file', fileOrBlob, 'camera_frame.jpg');

  const res = await apiRequest('/predict/camera-probe', {
    method: 'POST',
    body: formData,
    signal,
  });
  return res;
}

