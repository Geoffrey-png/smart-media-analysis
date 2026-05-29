import request from './request'

export function fetchAdminSummary() {
  return request.get('/admin/summary')
}

export function fetchOperationLogs(params) {
  return request.get('/admin/logs', { params })
}

export function fetchRoleOptions() {
  return request.get('/admin/roles')
}
