import request from './request'

export function fetchDashboardSummary() {
  return request.get('/dashboard/summary')
}

