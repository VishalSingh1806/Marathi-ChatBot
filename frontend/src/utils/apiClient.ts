// Encrypted API client to mask API calls
const API_BASE = 'http://localhost:8000';

// Simple obfuscation (not real encryption for demo)
function encrypt(data: any): string {
  const jsonStr = JSON.stringify(data);
  return btoa(jsonStr); // Simple base64 encoding
}

function decrypt(encryptedData: string): any {
  const decoded = atob(encryptedData);
  return JSON.parse(decoded);
}

// Obfuscated API routes
const ROUTES = {
  SECURE_QUERY: '/api/v1/secure/process',
  SECURE_AUDIO: '/api/v1/secure/audio',
  CSRF_TOKEN: '/csrf-token'
};

export class SecureApiClient {
  private static async makeRequest(url: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  static async secureQuery(text: string, sessionId?: string, csrfToken?: string) {
    const requestData = { text, session_id: sessionId, csrf_token: csrfToken };
    const encryptedRequest = encrypt(requestData);

    const response = await this.makeRequest('/api/v1/secure/process', {
      method: 'POST',
      body: JSON.stringify({ data: encryptedRequest }),
    });

    return decrypt(response.data);
  }

  static async getCsrfToken() {
    return this.makeRequest('/csrf-token');
  }
}