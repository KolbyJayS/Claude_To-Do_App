import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

// Attach stored access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, attempt a silent token refresh then replay the original request
let refreshPromise = null
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      if (!refreshPromise) {
        refreshPromise = axios
          .post('/api/auth/refresh', {}, { withCredentials: true })
          .then((r) => {
            localStorage.setItem('access_token', r.data.access_token)
          })
          .catch(() => {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
          })
          .finally(() => { refreshPromise = null })
      }
      await refreshPromise
      original.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`
      return api(original)
    }
    return Promise.reject(err)
  }
)

export default api
