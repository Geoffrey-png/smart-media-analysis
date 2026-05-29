import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/',
    component: AppLayout,
    redirect: '/dashboard',
    children: [
      { path: 'admin', name: 'AdminDashboard', component: () => import('../views/AdminDashboard.vue'), meta: { title: '管理员后台', roles: ['admin'] } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '洞察首页' } },
      { path: 'contents', name: 'Contents', component: () => import('../views/ContentList.vue'), meta: { title: '内容资产' } },
      { path: 'contents/new', name: 'ContentNew', component: () => import('../views/ContentForm.vue'), meta: { title: '新增内容', roles: ['admin', 'editor'] } },
      { path: 'contents/:id', name: 'ContentDetail', component: () => import('../views/ContentDetail.vue'), meta: { title: '内容详情' } },
      { path: 'contents/:id/edit', name: 'ContentEdit', component: () => import('../views/ContentForm.vue'), meta: { title: '编辑内容', roles: ['admin', 'editor'] } },
      { path: 'analysis', name: 'ContentAnalysis', component: () => import('../views/ContentAnalysis.vue'), meta: { title: '智能分析', roles: ['admin', 'editor'] } },
      { path: 'audit', name: 'ContentAudit', component: () => import('../views/ContentAudit.vue'), meta: { title: '内容审核', roles: ['admin', 'auditor'] } },
      { path: 'users', name: 'Users', component: () => import('../views/UserList.vue'), meta: { title: '用户管理', roles: ['admin'] } },
      { path: 'users/:id/profile', name: 'UserProfile', component: () => import('../views/UserProfile.vue'), meta: { title: '用户画像详情' } },
      { path: 'behaviors', name: 'Behaviors', component: () => import('../views/BehaviorLog.vue'), meta: { title: '行为日志', roles: ['admin', 'editor', 'auditor'] } },
      { path: 'recommendations', name: 'Recommendations', component: () => import('../views/Recommendation.vue'), meta: { title: '推荐实验' } },
      { path: 'recommendation-analysis', name: 'RecommendationAnalysis', component: () => import('../views/RecommendationAnalysis.vue'), meta: { title: '推荐效果', roles: ['admin', 'editor', 'auditor'] } },
      { path: 'statistics', name: 'Statistics', component: () => import('../views/Statistics.vue'), meta: { title: '数据统计', roles: ['admin', 'editor', 'auditor'] } },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { title: '系统设置', roles: ['admin'] } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('smart-media-token')
  if (!to.meta.public && !token) {
    next('/login')
    return
  }

  const roles = to.meta.roles
  if (roles?.length) {
    const user = JSON.parse(localStorage.getItem('smart-media-user') || 'null')
    const role = user?.role
    // 如果本地用户信息还没刷新，先放行，后端接口仍会强制拦截。
    if (role && !roles.includes(role)) {
      next('/dashboard')
      return
    }
  }
  next()
})

export default router
