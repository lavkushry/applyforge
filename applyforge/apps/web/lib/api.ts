const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const isForm = options.body instanceof FormData
  const headers: HeadersInit = { ...(isForm ? {} : {'Content-Type':'application/json'}), ...(options.headers||{}), ...(token ? { Authorization: `Bearer ${token}` } : {}) }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) throw new Error(await res.text() || 'Request failed')
  return res.json() as Promise<T>
}
