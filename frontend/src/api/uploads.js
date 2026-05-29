import request from './request'

export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/uploads', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
