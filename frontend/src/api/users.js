import request from './request'

export function fetchUsers(params) {
  return request.get('/users', { params })
}

export function fetchUser(id) {
  return request.get(`/users/${id}`)
}

export function createUser(data) {
  return request.post('/users', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

export function fetchUserProfile(id) {
  return request.get(`/users/${id}/profile`)
}

