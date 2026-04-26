const rawUrl = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";
export const PYTHON_BACKEND_URL = rawUrl.endsWith("/") ? rawUrl.slice(0, -1) : rawUrl;