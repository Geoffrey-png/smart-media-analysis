import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000
})

request.interceptors.request.use(config => {
  const token = localStorage.getItem('smart-media-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  response => {
    const payload = response.data
    if (payload && payload.code !== 0) {
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(payload)
    }
    return payload
  },
  error => {
    const message = error?.response?.data?.message || error.message || '网络异常'
    if (error?.response?.status === 401) {
      localStorage.removeItem('smart-media-token')
      localStorage.removeItem('smart-media-user')
      if (location.pathname !== '/login') {
        location.href = '/login'
      }
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
