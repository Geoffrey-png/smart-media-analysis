<template>
  <div class="page admin-page">
    <section class="page-header admin-hero">
      <div>
        <div class="hero-kicker">ADMIN CONTROL CENTER</div>
        <h2 class="page-title">管理员后台</h2>
        <p class="header-desc">这里是真正的管理员入口：角色权限、系统概览、操作审计都从这里查看。</p>
      </div>
      <el-button type="primary" size="large" :loading="loading" @click="loadData">刷新后台数据</el-button>
    </section>

    <section class="admin-kpis">
      <div class="metric-box">
        <span>用户总数</span>
        <strong>{{ summary.user_count || 0 }}</strong>
        <small>正常 {{ summary.active_user_count || 0 }} / 禁用 {{ summary.disabled_user_count || 0 }}</small>
      </div>
      <div class="metric-box">
        <span>内容总数</span>
        <strong>{{ summary.content_count || 0 }}</strong>
        <small>系统内容资产</small>
      </div>
      <div class="metric-box">
        <span>新闻采集</span>
        <strong>{{ summary.news_count || 0 }}</strong>
        <small>带来源链接的新闻内容</small>
      </div>
      <div class="metric-box warning">
        <span>待审核</span>
        <strong>{{ summary.pending_audit_count || 0 }}</strong>
        <small>需要审核员处理</small>
      </div>
      <div class="metric-box">
        <span>行为日志</span>
        <strong>{{ summary.behavior_count || 0 }}</strong>
        <small>用户浏览、点赞等行为</small>
      </div>
      <div class="metric-box">
        <span>操作审计</span>
        <strong>{{ summary.operation_log_count || 0 }}</strong>
        <small>今日操作 {{ summary.today_operation_count || 0 }} 次</small>
      </div>
    </section>

    <section class="admin-grid">
      <article class="admin-card card">
        <div class="card-head">
          <span class="card-kicker">Role Distribution</span>
          <h3>角色分布</h3>
        </div>
        <div class="pill-list">
          <div v-for="item in summary.role_distribution || []" :key="item.name" class="pill-row">
            <span>{{ roleLabel(item.name) }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </article>

      <article class="admin-card card">
        <div class="card-head">
          <span class="card-kicker">Account Status</span>
          <h3>账号状态</h3>
        </div>
        <div class="pill-list">
          <div v-for="item in summary.user_status_distribution || []" :key="item.name" class="pill-row">
            <span>{{ userStatusLabel(item.name) }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </article>

      <article class="admin-card card">
        <div class="card-head">
          <span class="card-kicker">Content Status</span>
          <h3>内容状态</h3>
        </div>
        <div class="pill-list">
          <div v-for="item in summary.content_status_distribution || []" :key="item.name" class="pill-row">
            <span>{{ statusLabel(item.name) }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </article>

      <article class="admin-card card">
        <div class="card-head">
          <span class="card-kicker">News Sources</span>
          <h3>新闻来源</h3>
        </div>
        <div class="pill-list">
          <div v-for="item in summary.news_source_distribution || []" :key="item.name" class="pill-row">
            <span>{{ item.name || '未知来源' }}</span>
            <strong>{{ item.value }}</strong>
          </div>
          <el-empty v-if="!summary.news_source_distribution?.length" description="暂无新闻采集数据" />
        </div>
      </article>
    </section>

    <section class="log-card card">
      <div class="log-head">
        <div>
          <span class="card-kicker">Operation Audit</span>
          <h3>操作日志</h3>
        </div>
        <div class="log-filter">
          <el-input v-model="query.keyword" placeholder="搜索用户 / 动作 / 详情" clearable @keyup.enter="loadLogs" />
          <el-button type="primary" @click="loadLogs">查询</el-button>
        </div>
      </div>

      <el-table v-loading="logLoading" :data="logs">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="username" label="操作人" width="130" />
        <el-table-column label="角色" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="110" />
        <el-table-column prop="action" label="动作" width="150" />
        <el-table-column prop="target_id" label="对象ID" width="100" />
        <el-table-column prop="detail" label="详情" min-width="260" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP" width="140" />
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        class="log-pagination"
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        @current-change="loadLogs"
        @size-change="loadLogs"
      />
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { fetchAdminSummary, fetchOperationLogs } from '../api/admin'

const loading = ref(false)
const logLoading = ref(false)
const summary = ref({})
const logs = ref([])
const total = ref(0)
const query = reactive({
  page: 1,
  page_size: 20,
  keyword: ''
})

function roleLabel(value) {
  return {
    admin: '管理员',
    editor: '编辑',
    auditor: '审核员',
    viewer: '观察者'
  }[value] || value || '观察者'
}

function statusLabel(value) {
  return {
    draft: '草稿',
    pending: '待审核',
    published: '已发布',
    rejected: '已拒绝',
    offline: '已下架'
  }[value] || value || '未知'
}

function userStatusLabel(value) {
  return {
    active: '正常',
    disabled: '已禁用'
  }[value] || value || '未知'
}

function formatTime(value) {
  return value ? value.replace('T', ' ').slice(0, 19) : '-'
}

async function loadSummary() {
  loading.value = true
  try {
    const res = await fetchAdminSummary()
    summary.value = res.data || {}
  } finally {
    loading.value = false
  }
}

async function loadLogs() {
  logLoading.value = true
  try {
    const res = await fetchOperationLogs(query)
    logs.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    logLoading.value = false
  }
}

function loadData() {
  loadSummary()
  loadLogs()
}

onMounted(loadData)
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 20px;
}

.admin-hero {
  align-items: center;
}

.hero-kicker,
.card-kicker {
  color: #2563eb;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.header-desc {
  max-width: 760px;
  margin: 9px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.admin-kpis {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.metric-box {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.86)),
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.1), transparent 40%);
  box-shadow: var(--shadow-card);
}

.metric-box.warning {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(255, 251, 235, 0.86)),
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.15), transparent 40%);
}

.metric-box span,
.metric-box small {
  display: block;
  color: #64748b;
  font-size: 12px;
}

.metric-box strong {
  display: block;
  margin: 9px 0 4px;
  color: #0f172a;
  font-size: 30px;
  font-weight: 950;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.admin-card,
.log-card {
  padding: 22px;
}

.card-head {
  margin-bottom: 16px;
}

.card-head h3,
.log-head h3 {
  margin: 6px 0 0;
  font-size: 19px;
  font-weight: 900;
}

.pill-list {
  display: grid;
  gap: 12px;
}

.pill-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
}

.pill-row span {
  color: #475569;
  font-weight: 800;
}

.pill-row strong {
  color: #2563eb;
  font-size: 20px;
  font-weight: 950;
}

.log-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.log-filter {
  display: flex;
  gap: 10px;
  width: 420px;
}

.log-pagination {
  margin-top: 18px;
}

@media (max-width: 1400px) {
  .admin-kpis {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .admin-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1180px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
