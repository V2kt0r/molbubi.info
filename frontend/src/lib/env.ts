// Environment variables with fallbacks
export const ENV = {
  // In development, use relative URL to leverage Vite proxy. In production, use full URL.
  API_BASE_URL: import.meta.env.DEV 
    ? '/api/v1' // Development: use proxy
    : (import.meta.env.VITE_API_BASE_URL || '/api/v1'), // Production: use full URL from env
  ENVIRONMENT: import.meta.env.VITE_ENVIRONMENT || 'development',
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
} as const;

// Validate required environment variables
if (!ENV.API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL is required');
}