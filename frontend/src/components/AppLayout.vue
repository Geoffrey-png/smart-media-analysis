<template>
  <div class="app-shell">
    <aside class="side-panel">
      <div class="brand">
        <div class="brand-logo"><span>AI</span></div>
        <div>
          <div class="brand-title">MediaMind</div>
          <div class="brand-subtitle">智能传媒洞察平台</div>
        </div>
      </div>

      <div class="side-card">
        <div class="side-card-label">当前权限</div>
        <div class="role-name">{{ roleLabel(auth.user?.role) }}</div>
        <div class="side-card-desc">{{ roleDesc(auth.user?.role) }}</div>
      </div>

      <nav class="nav-list">
        <RouterLink
          v-for="item in visibleNavItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item) }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div class="topbar-title">
          <div class="eyebrow">SMART MEDIA ANALYTICS</div>
          <strong>{{ route.meta.title || '数据工作台' }}</strong>
        </div>

        <div class="topbar-tools">
          <div class="global-search">
            <el-icon><Search /></el-icon>
            <span>搜索内容、标签、用户画像</span>
          </div>
          <div class="live-pill">
            <span class="live-dot"></span>
            Live
          </div>
          <div class="user-chip">
            <div class="avatar">{{ userInitial }}</div>
            <div class="user-meta">
              <span>{{ auth.user?.nickname || auth.user?.username || '分析员' }}</span>
              <small>{{ roleLabel(auth.user?.role) }}</small>
            </div>
          </div>
          <el-button class="logout-btn" text @click="logout">退出</el-button>
        </div>
      </header>

      <main class="main">
        <router-view />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  CircleCheck,
  DataAnalysis,
  Document,
  Histogram,
  List,
  Lock,
  MagicStick,
  Promotion,
  Search,
  Setting,
  TrendCharts,
  User
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const navItems = [
  { path: '/admin', label: '管理员后台', icon: Lock, match: '/admin', roles: ['admin'] },
  { path: '/dashboard', label: '洞察首页', icon: DataAnalysis, match: '/dashboard', roles: ['admin', 'editor', 'auditor', 'viewer'] },
  { path: '/contents', label: '内容资产', icon: Document, match: '/contents', roles: ['admin', 'editor', 'auditor', 'viewer'] },
  { path: '/analysis', label: '智能分析', icon: MagicStick, match: '/analysis', roles: ['admin', 'editor'] },
  { path: '/audit', label: '内容审核', icon: CircleCheck, match: '/audit', roles: ['admin', 'auditor'] },
  { path: '/users', label: '用户管理', icon: User, match: '/users', roles: ['admin'] },
  { path: '/behaviors', label: '行为日志', icon: List, match: '/behaviors', roles: ['admin', 'editor', 'auditor'] },
  { path: '/recommendations', label: '推荐实验', icon: Promotion, match: '/recommendations', roles: ['admin', 'editor', 'viewer'] },
  { path: '/recommendation-analysis', label: '推荐效果', icon: TrendCharts, match: '/recommendation-analysis', roles: ['admin', 'editor', 'auditor'] },
  { path: '/statistics', label: '数据统计', icon: Histogram, match: '/statistics', roles: ['admin', 'editor', 'auditor'] },
  { path: '/settings', label: '系统设置', icon: Setting, match: '/settings', roles: ['admin'] }
]

const currentRole = computed(() => auth.user?.role || 'viewer')
const visibleNavItems = computed(() => navItems.filter(item => item.roles.includes(currentRole.value)))

const userInitial = computed(() => {
  const name = auth.user?.nickname || auth.user?.username || 'A'
  return String(name).trim().slice(0, 1).toUpperCase()
})

function roleLabel(role) {
  return {
    admin: '管理员',
    editor: '编辑',
    auditor: '审核员',
    viewer: '观察者'
  }[role || 'viewer'] || '观察者'
}

function roleDesc(role) {
  return {
    admin: '拥有用户、内容、审核、采集、日志全部权限',
    editor: '可采集新闻、编辑内容、查看推荐分析',
    auditor: '可审核内容、查看行为和推荐效果',
    viewer: '只能浏览内容和查看自己的推荐'
  }[role || 'viewer']
}

function isActive(item) {
  return route.path === item.path || route.path.startsWith(item.match)
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  auth.loadCurrentUser().catch(() => {})
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  color: var(--text-primary);
  background:
    radial-gradient(circle at 18% 8%, rgba(56, 189, 248, 0.18), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(99, 102, 241, 0.18), transparent 30%),
    var(--app-bg);
}

.side-panel {
  position: sticky;
  top: 0;
  width: 272px;
  height: 100vh;
  padding: 22px 18px;
  overflow-y: auto;
  background:
    linear-gradient(180deg, rgba(7, 15, 31, 0.98), rgba(15, 23, 42, 0.94)),
    radial-gradient(circle at top left, rgba(34, 211, 238, 0.28), transparent 34%);
  border-right: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 24px 0 60px rgba(15, 23, 42, 0.18);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 58px;
}

.brand-logo {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  color: white;
  font-weight: 900;
  background: linear-gradient(135deg, #22d3ee, #2563eb 56%, #8b5cf6);
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.38);
}

.brand-title {
  color: #fff;
  font-size: 18px;
  font-weight: 850;
}

.brand-subtitle {
  margin-top: 3px;
  color: #8fa4c7;
  font-size: 12px;
}

.side-card {
  margin: 24px 0 18px;
  padding: 16px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.72));
}

.side-card-label {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 800;
}

.role-name {
  margin-top: 10px;
  color: #fff;
  font-size: 22px;
  font-weight: 950;
}

.side-card-desc {
  margin-top: 8px;
  color: #8fa4c7;
  font-size: 12px;
  line-height: 1.6;
}

.nav-list {
  display: grid;
  gap: 7px;
  padding-bottom: 18px;
}

.nav-item {
  position: relative;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 14px;
  color: #a8b6d3;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 650;
  transition: 0.2s ease;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.07);
  transform: translateX(2px);
}

.nav-item.active {
  color: #fff;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.96), rgba(14, 165, 233, 0.88));
  box-shadow: 0 16px 30px rgba(37, 99, 235, 0.24);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  right: 12px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #a7f3d0;
}

.workspace {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  min-height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 0 30px;
  background: rgba(246, 249, 254, 0.78);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  backdrop-filter: blur(18px);
}

.topbar-title strong {
  display: block;
  margin-top: 4px;
  color: #0f172a;
  font-size: 22px;
  font-weight: 850;
}

.eyebrow {
  color: #2563eb;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.16em;
}

.topbar-tools {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.global-search {
  min-width: 260px;
  height: 42px;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 0 14px;
  color: #64748b;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
  font-size: 13px;
}

.live-pill {
  height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 13px;
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.18);
  border-radius: 999px;
  background: rgba(236, 253, 245, 0.92);
  font-size: 13px;
  font-weight: 800;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.14);
}

.user-chip {
  height: 46px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 12px 5px 6px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
}

.avatar {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  color: white;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  font-weight: 850;
}

.user-meta {
  display: grid;
  line-height: 1.1;
}

.user-meta span {
  color: #0f172a;
  font-size: 13px;
  font-weight: 800;
}

.user-meta small {
  margin-top: 3px;
  color: #64748b;
  font-size: 11px;
}

.logout-btn {
  color: #64748b;
}

.main {
  flex: 1;
  padding: 26px 30px 34px;
}

@media (max-width: 1180px) {
  .side-panel {
    width: 232px;
  }

  .global-search {
    display: none;
  }
}
</style>
