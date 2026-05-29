<template>
  <div class="page asset-page">
    <section class="page-header asset-hero">
      <div>
        <div class="hero-kicker">CONTENT ASSET INTELLIGENCE</div>
        <h2 class="page-title">内容资产洞察</h2>
        <p class="header-desc">从内容库存、热度、质量、情感和状态维度观察内容池，而不是只做增删改查。</p>
      </div>
      <div class="hero-actions">
        <el-button size="large" :loading="newsLoading" @click="openNewsDialog">采集新闻</el-button>
        <el-button type="primary" size="large" @click="router.push('/contents/new')">新增内容</el-button>
      </div>
    </section>

    <section class="asset-kpis">
      <div class="metric-box">
        <span>总内容量</span>
        <strong>{{ formatNumber(total) }}</strong>
        <small>符合当前筛选条件</small>
      </div>
      <div class="metric-box">
        <span>当前页浏览</span>
        <strong>{{ formatNumber(visibleViewCount) }}</strong>
        <small>列表内容累计浏览</small>
      </div>
      <div class="metric-box">
        <span>平均热度</span>
        <strong>{{ visibleAvgHeat }}</strong>
        <small>当前页热度均值</small>
      </div>
      <div class="metric-box warning">
        <span>待审核</span>
        <strong>{{ pendingCount }}</strong>
        <small>需人工处理内容</small>
      </div>
    </section>

    <section class="content-lens card">
      <div class="toolbar lens-toolbar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题 / 正文 / 标签"
          clearable
          style="width: 280px"
          @keyup.enter="loadData"
        />
        <el-select v-model="filters.category" placeholder="分类" clearable style="width: 150px">
          <el-option v-for="item in categories" :key="item.name" :label="item.name" :value="item.name" />
        </el-select>
        <el-select v-model="filters.content_type" placeholder="类型" clearable style="width: 150px">
          <el-option label="文章" value="article" />
          <el-option label="视频" value="video" />
          <el-option label="图片" value="image" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 150px">
          <el-option label="草稿" value="draft" />
          <el-option label="待审核" value="pending" />
          <el-option label="已发布" value="published" />
          <el-option label="已拒绝" value="rejected" />
          <el-option label="已下架" value="offline" />
        </el-select>
        <el-button type="primary" @click="loadData">筛选</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <div v-loading="loading" class="asset-grid">
        <article v-for="item in spotlightContents" :key="item.id" class="asset-card">
          <div class="asset-card-top">
            <el-tag :type="statusType(item.status)" effect="light">{{ statusLabel(item.status) }}</el-tag>
            <span>{{ contentTypeLabel(item.content_type) }}</span>
          </div>
          <h3>{{ item.title || '未命名内容' }}</h3>
          <p>{{ item.summary || (item.content || '').slice(0, 90) || '暂无摘要' }}</p>
          <div class="tag-list">
            <el-tag v-for="tag in (item.tags || []).slice(0, 4)" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
          <div class="asset-data">
            <div>
              <strong>{{ formatNumber(item.view_count || 0) }}</strong>
              <span>浏览</span>
            </div>
            <div>
              <strong>{{ Number(item.heat_score || 0).toFixed(1) }}</strong>
              <span>热度</span>
            </div>
            <div>
              <strong>{{ Number(item.quality_score || 0).toFixed(1) }}</strong>
              <span>质量</span>
            </div>
          </div>
        </article>
      </div>

      <div class="table-head">
        <div>
          <span class="card-kicker">Content Detail Table</span>
          <h3>内容明细</h3>
        </div>
        <span class="muted">展示 {{ tableData.length }} 条 / 共 {{ total }} 条</span>
      </div>

      <el-table v-loading="loading" :data="tableData">
        <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="110" />
        <el-table-column prop="source_name" label="来源" width="130" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="标签" min-width="190">
          <template #default="{ row }">
            <div class="tag-list">
              <el-tag v-for="tag in row.tags" :key="tag" size="small">{{ tag }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="热度 / 质量" width="170">
          <template #default="{ row }">
            <div class="score-line">
              <span>热 {{ Number(row.heat_score || 0).toFixed(1) }}</span>
              <span>质 {{ Number(row.quality_score || 0).toFixed(1) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="互动" width="130">
          <template #default="{ row }">
            <div class="interaction-cell">
              <span>{{ formatNumber(row.view_count || 0) }} 浏览</span>
              <small>{{ formatNumber(row.like_count || 0) }} 点赞</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="情感" width="100">
          <template #default="{ row }">
            <el-tag :type="sentimentType(row.sentiment)" size="small">{{ sentimentLabel(row.sentiment) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/contents/${row.id}`)">详情</el-button>
            <el-button text type="primary" @click="router.push(`/contents/${row.id}/edit`)">编辑</el-button>
            <el-button text type="success" @click="handleAnalyze(row)">分析</el-button>
            <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="filters.page"
        v-model:page-size="filters.page_size"
        class="asset-pagination"
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        @current-change="loadData"
        @size-change="loadData"
      />
    </section>

    <el-dialog v-model="newsDialogVisible" title="采集真实新闻" width="560px">
      <el-form :model="newsForm" label-width="96px">
        <el-form-item label="新闻源">
          <el-select v-model="newsForm.source_key" style="width: 100%">
            <el-option label="全部默认源" value="all" />
            <el-option label="自定义 RSS" value="custom" />
            <el-option v-for="source in newsSources" :key="source.key" :label="source.name" :value="source.key" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="newsForm.source_key === 'custom'" label="RSS 地址">
          <el-input v-model="newsForm.custom_url" placeholder="https://example.com/rss.xml" />
        </el-form-item>
        <el-form-item v-if="newsForm.source_key === 'custom'" label="源名称">
          <el-input v-model="newsForm.custom_name" placeholder="自定义新闻源" />
        </el-form-item>
        <el-form-item label="导入数量">
          <el-input-number v-model="newsForm.limit" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="抓正文">
          <el-switch v-model="newsForm.fetch_full_text" />
          <span class="muted news-tip">开启后会尝试读取新闻详情页正文，失败则使用 RSS 摘要。</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newsDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="newsLoading" @click="handleImportNews">开始采集</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { analyzeContent, deleteContent, fetchContents } from '../api/content'
import { fetchCategories } from '../api/meta'
import { fetchNewsSources, importNews } from '../api/news'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const categories = ref([])
const newsSources = ref([])
const newsDialogVisible = ref(false)
const newsLoading = ref(false)
const newsForm = reactive({
  source_key: 'all',
  limit: 20,
  fetch_full_text: true,
  custom_url: '',
  custom_name: '自定义新闻源'
})
const filters = reactive({
  page: 1,
  page_size: 10,
  keyword: '',
  category: '',
  content_type: '',
  status: ''
})

const spotlightContents = computed(() => tableData.value.slice(0, 3))
const visibleViewCount = computed(() => tableData.value.reduce((sum, item) => sum + Number(item.view_count || 0), 0))
const pendingCount = computed(() => tableData.value.filter(item => item.status === 'pending').length)
const visibleAvgHeat = computed(() => {
  if (!tableData.value.length) return '0.0'
  const value = tableData.value.reduce((sum, item) => sum + Number(item.heat_score || 0), 0) / tableData.value.length
  return value.toFixed(1)
})

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function contentTypeLabel(value) {
  return {
    article: '文章',
    video: '视频',
    image: '图片'
  }[value] || value || '内容'
}

function sentimentLabel(value) {
  return {
    positive: '正向',
    negative: '负向',
    neutral: '中性'
  }[value] || value || '未知'
}

function sentimentType(value) {
  return value === 'positive' ? 'success' : value === 'negative' ? 'danger' : 'info'
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

function statusType(value) {
  return {
    draft: 'info',
    pending: 'warning',
    published: 'success',
    rejected: 'danger',
    offline: 'info'
  }[value] || 'info'
}

async function loadData() {
  loading.value = true
  try {
    const res = await fetchContents(filters)
    tableData.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const res = await fetchCategories()
  categories.value = res.data || []
}

async function loadNewsSources() {
  const res = await fetchNewsSources()
  newsSources.value = res.data || []
}

async function openNewsDialog() {
  newsDialogVisible.value = true
  if (!newsSources.value.length) {
    await loadNewsSources()
  }
}

async function handleImportNews() {
  if (newsForm.source_key === 'custom' && !newsForm.custom_url) {
    ElMessage.warning('请输入自定义 RSS 地址')
    return
  }
  newsLoading.value = true
  try {
    const res = await importNews(newsForm)
    const data = res.data || {}
    const errorText = data.errors?.length ? `，失败 ${data.errors.length} 条` : ''
    ElMessage.success(`采集完成：新增 ${data.imported_count || 0} 条，跳过 ${data.skipped_count || 0} 条${errorText}`)
    newsDialogVisible.value = false
    await loadData()
  } finally {
    newsLoading.value = false
  }
}

function reset() {
  filters.keyword = ''
  filters.category = ''
  filters.content_type = ''
  filters.status = ''
  filters.page = 1
  loadData()
}

async function handleAnalyze(row) {
  await analyzeContent(row.id)
  ElMessage.success('智能分析完成')
  loadData()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除「${row.title}」？`, '删除确认', { type: 'warning' })
  await deleteContent(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadCategories()
  loadNewsSources()
  loadData()
})
</script>

<style scoped>
.asset-page {
  display: grid;
  gap: 20px;
}

.asset-hero {
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

.hero-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.news-tip {
  margin-left: 10px;
  font-size: 12px;
}

.asset-kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.metric-box {
  padding: 20px;
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
  font-size: 13px;
}

.metric-box strong {
  display: block;
  margin: 10px 0 4px;
  color: #0f172a;
  font-size: 31px;
  font-weight: 950;
  letter-spacing: -0.05em;
}

.content-lens {
  padding: 20px;
}

.lens-toolbar {
  margin: 0 0 18px;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.asset-grid {
  min-height: 142px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.asset-card {
  min-height: 212px;
  display: flex;
  flex-direction: column;
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.68)),
    radial-gradient(circle at right top, rgba(14, 165, 233, 0.1), transparent 42%);
}

.asset-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 800;
}

.asset-card h3 {
  margin: 16px 0 8px;
  color: #0f172a;
  font-size: 17px;
  line-height: 1.45;
}

.asset-card p {
  min-height: 44px;
  margin: 0 0 14px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
}

.asset-data {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: auto;
  padding-top: 16px;
}

.asset-data div {
  padding: 10px;
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.86);
}

.asset-data strong,
.asset-data span {
  display: block;
}

.asset-data strong {
  color: #0f172a;
  font-size: 17px;
  font-weight: 900;
}

.asset-data span {
  margin-top: 3px;
  color: #94a3b8;
  font-size: 12px;
}

.table-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.table-head h3 {
  margin: 5px 0 0;
  font-size: 19px;
  font-weight: 900;
}

.score-line,
.interaction-cell {
  display: grid;
  gap: 3px;
}

.score-line span {
  color: #475569;
  font-size: 12px;
  font-weight: 800;
}

.interaction-cell span {
  color: #0f172a;
  font-size: 13px;
  font-weight: 800;
}

.interaction-cell small {
  color: #94a3b8;
}

.asset-pagination {
  margin-top: 18px;
}

@media (max-width: 1280px) {
  .asset-kpis,
  .asset-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
