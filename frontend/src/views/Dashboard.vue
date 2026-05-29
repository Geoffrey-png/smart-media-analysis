<template>
  <div class="insight-page">
    <section class="dashboard-hero">
      <div class="hero-copy">
        <div class="hero-kicker">
          <span class="pulse-dot"></span>
          内容热度 / 用户兴趣 / 推荐转化一屏掌控
        </div>
        <h1>智能传媒内容洞察中心</h1>
        <p>
          面向编辑、运营和算法团队，把内容资产、用户行为、推荐效果转成可读的数据故事，
          不再只是录入、删除、审核的后台表格。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" :loading="loading" @click="loadData">刷新洞察</el-button>
          <span class="update-time">当前版本：本地训练项目 · FastAPI + Vue</span>
        </div>
      </div>

      <div class="hero-panel">
        <div class="panel-title">今日推荐信号</div>
        <div class="signal-score">{{ todayClickRate }}</div>
        <div class="panel-desc">推荐点击 / 今日浏览</div>
        <div class="score-ring">
          <span style="--i: 1"></span>
          <span style="--i: 2"></span>
          <span style="--i: 3"></span>
        </div>
        <div class="mini-metrics">
          <div>
            <strong>{{ formatNumber(summary.today_views || 0) }}</strong>
            <small>今日浏览</small>
          </div>
          <div>
            <strong>{{ formatNumber(summary.today_recommend_clicks || 0) }}</strong>
            <small>推荐点击</small>
          </div>
        </div>
      </div>
    </section>

    <section class="kpi-grid">
      <StatCard
        label="内容资产"
        :value="formatNumber(summary.content_count || 0)"
        desc="已入库并可参与分析的内容"
        icon="文"
        tone="blue"
        change="+ 内容池"
      />
      <StatCard
        label="用户画像"
        :value="formatNumber(summary.user_count || 0)"
        desc="用于兴趣建模的用户规模"
        icon="人"
        tone="cyan"
        change="+ 标签"
      />
      <StatCard
        label="今日浏览"
        :value="formatNumber(summary.today_views || 0)"
        desc="当天 view 行为的实时汇总"
        icon="眼"
        tone="purple"
        :change="todayViewSignal"
      />
      <StatCard
        label="行为日志"
        :value="formatNumber(summary.behavior_count || 0)"
        desc="累计采集的交互行为"
        icon="流"
        tone="orange"
        change="行为流"
      />
    </section>

    <section class="analysis-grid">
      <article class="analytics-card trend-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Behavior Trend</span>
            <h3>近 7 日用户行为趋势</h3>
          </div>
          <span class="card-badge">实时分析</span>
        </div>
        <div ref="trendRef" class="chart chart-large"></div>
      </article>

      <article class="analytics-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Interest Graph</span>
            <h3>兴趣标签分布</h3>
          </div>
          <span class="card-badge light">画像</span>
        </div>
        <div ref="interestRef" class="chart"></div>
      </article>
    </section>

    <section class="bottom-grid">
      <article class="analytics-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Content Mix</span>
            <h3>分类内容结构</h3>
          </div>
          <span class="card-badge light">内容供给</span>
        </div>
        <div ref="categoryRef" class="chart"></div>
      </article>

      <article class="analytics-card hot-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Hot Contents</span>
            <h3>热门内容 Top 6</h3>
          </div>
          <span class="card-badge">热度榜</span>
        </div>

        <div v-if="topContents.length" class="hot-list">
          <div v-for="(item, index) in topContents" :key="item.id || item.title" class="hot-row">
            <div class="rank" :class="{ top: index < 3 }">{{ index + 1 }}</div>
            <div class="hot-main">
              <div class="hot-title">{{ item.title || '未命名内容' }}</div>
              <div class="hot-meta">
                <span>{{ item.category || '未分类' }}</span>
                <span>{{ formatNumber(item.view_count || 0) }} 浏览</span>
                <span>热度 {{ Number(item.heat_score || 0).toFixed(1) }}</span>
              </div>
              <div class="heat-bar">
                <i :style="{ width: heatWidth(item) }"></i>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无热门内容数据" />
      </article>

      <article class="analytics-card insight-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Strategy Notes</span>
            <h3>运营洞察建议</h3>
          </div>
        </div>
        <div class="insight-list">
          <div v-for="item in insightCards" :key="item.title" class="insight-item">
            <div class="insight-icon">{{ item.icon }}</div>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import StatCard from '../components/StatCard.vue'
import { fetchDashboardSummary } from '../api/dashboard'

const summary = ref({})
const loading = ref(false)
const trendRef = ref()
const interestRef = ref()
const categoryRef = ref()
let charts = []

const topContents = computed(() => (summary.value.hot_contents || []).slice(0, 6))

const maxHeat = computed(() => {
  const values = topContents.value.map(item => Number(item.heat_score || 0))
  return Math.max(...values, 1)
})

const todayClickRate = computed(() => {
  const views = Number(summary.value.today_views || 0)
  const clicks = Number(summary.value.today_recommend_clicks || 0)
  if (!views) return '0%'
  return `${((clicks / views) * 100).toFixed(1)}%`
})

const todayViewSignal = computed(() => {
  const views = Number(summary.value.today_views || 0)
  if (views >= 1000) return '高活跃'
  if (views >= 100) return '稳定'
  return '待提升'
})

const insightCards = computed(() => {
  const topCategory = [...(summary.value.category_distribution || [])].sort((a, b) => b.value - a.value)[0]
  const topTag = [...(summary.value.interest_distribution || [])].sort((a, b) => b.value - a.value)[0]
  return [
    {
      icon: '01',
      title: topCategory ? `${topCategory.name} 是当前主要内容供给` : '内容分类数据不足',
      desc: topCategory ? `该分类已有 ${topCategory.value} 条内容，可继续观察阅读转化。` : '建议先补充内容分类，便于做结构分析。'
    },
    {
      icon: '02',
      title: topTag ? `${topTag.name} 兴趣标签更集中` : '用户兴趣画像不足',
      desc: topTag ? '可围绕该标签组织专题内容和推荐实验。' : '建议增加用户兴趣标签或行为数据。'
    },
    {
      icon: '03',
      title: `推荐点击率 ${todayClickRate.value}`,
      desc: '后续可以加入曝光去重、A/B 实验和推荐链路漏斗。'
    }
  ]
})

async function loadData() {
  loading.value = true
  try {
    const res = await fetchDashboardSummary()
    summary.value = res.data || {}
    await nextTick()
    renderCharts()
  } catch (error) {
    ElMessage.error('仪表盘数据加载失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function heatWidth(item) {
  const value = Number(item.heat_score || 0)
  return `${Math.max(8, Math.round((value / maxHeat.value) * 100))}%`
}

function getChart(el) {
  if (!el) return null
  const chart = echarts.getInstanceByDom(el) || echarts.init(el)
  if (!charts.includes(chart)) charts.push(chart)
  return chart
}

function renderCharts() {
  renderTrendChart()
  renderInterestChart()
  renderCategoryChart()
}

function renderTrendChart() {
  const trend = summary.value.behavior_trend || []
  const chart = getChart(trendRef.value)
  if (!chart) return
  chart.setOption({
    color: ['#2563eb'],
    grid: { left: 38, right: 18, top: 32, bottom: 30 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#fff' }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trend.map(item => item.date),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.16)' } },
      axisLabel: { color: '#64748b' }
    },
    series: [
      {
        name: '行为数',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 4 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37, 99, 235, 0.26)' },
            { offset: 1, color: 'rgba(37, 99, 235, 0.02)' }
          ])
        },
        data: trend.map(item => item.value)
      }
    ]
  })
}

function renderInterestChart() {
  const chart = getChart(interestRef.value)
  if (!chart) return
  chart.setOption({
    color: ['#2563eb', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#fff' }
    },
    legend: { bottom: 0, icon: 'circle', textStyle: { color: '#64748b' } },
    series: [
      {
        name: '兴趣标签',
        type: 'pie',
        radius: ['50%', '72%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        label: { color: '#475569', formatter: '{b}' },
        itemStyle: { borderColor: '#fff', borderWidth: 4 },
        data: summary.value.interest_distribution || []
      }
    ]
  })
}

function renderCategoryChart() {
  const categories = [...(summary.value.category_distribution || [])]
    .sort((a, b) => b.value - a.value)
    .slice(0, 8)
  const chart = getChart(categoryRef.value)
  if (!chart) return
  chart.setOption({
    color: ['#06b6d4'],
    grid: { left: 70, right: 18, top: 18, bottom: 24 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#fff' }
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.16)' } },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'category',
      inverse: true,
      data: categories.map(item => item.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#475569', fontWeight: 700 }
    },
    series: [
      {
        name: '内容数',
        type: 'bar',
        barWidth: 12,
        data: categories.map(item => item.value),
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#38bdf8' },
            { offset: 1, color: '#2563eb' }
          ])
        }
      }
    ]
  })
}

function resizeCharts() {
  charts.forEach(chart => chart.resize())
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  charts.forEach(chart => chart.dispose())
  charts = []
})
</script>

<style scoped>
.insight-page {
  display: grid;
  gap: 22px;
}

.dashboard-hero {
  position: relative;
  min-height: 280px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 26px;
  overflow: hidden;
  padding: 34px;
  color: white;
  border-radius: 32px;
  background:
    radial-gradient(circle at 18% 18%, rgba(34, 211, 238, 0.28), transparent 30%),
    radial-gradient(circle at 88% 16%, rgba(139, 92, 246, 0.32), transparent 32%),
    linear-gradient(135deg, #061224, #102a5c 56%, #1e1b4b);
  box-shadow: 0 30px 70px rgba(15, 23, 42, 0.2);
}

.dashboard-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.055) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: linear-gradient(90deg, #000, transparent 82%);
}

.hero-copy,
.hero-panel {
  position: relative;
  z-index: 1;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  color: #bfdbfe;
  border: 1px solid rgba(191, 219, 254, 0.18);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.36);
  font-size: 13px;
  font-weight: 800;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 7px rgba(34, 197, 94, 0.16);
}

.hero-copy h1 {
  max-width: 740px;
  margin: 26px 0 16px;
  font-size: 46px;
  line-height: 1.08;
  font-weight: 950;
  letter-spacing: -0.06em;
}

.hero-copy p {
  max-width: 760px;
  margin: 0;
  color: #cbd5e1;
  font-size: 16px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 28px;
}

.update-time {
  color: #93c5fd;
  font-size: 13px;
}

.hero-panel {
  align-self: stretch;
  min-height: 212px;
  padding: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
}

.panel-title {
  color: #dbeafe;
  font-size: 14px;
  font-weight: 820;
}

.signal-score {
  margin-top: 20px;
  font-size: 56px;
  line-height: 1;
  font-weight: 950;
  letter-spacing: -0.06em;
}

.panel-desc {
  margin-top: 8px;
  color: #93c5fd;
  font-size: 13px;
}

.score-ring {
  position: absolute;
  right: -70px;
  top: 28px;
  width: 210px;
  height: 210px;
  border-radius: 50%;
  border: 1px solid rgba(125, 211, 252, 0.18);
}

.score-ring span {
  position: absolute;
  inset: calc(var(--i) * 24px);
  border: 1px solid rgba(125, 211, 252, 0.16);
  border-radius: 50%;
}

.mini-metrics {
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 24px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.mini-metrics div {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.24);
}

.mini-metrics strong,
.mini-metrics small {
  display: block;
}

.mini-metrics strong {
  font-size: 20px;
  font-weight: 900;
}

.mini-metrics small {
  margin-top: 4px;
  color: #bfdbfe;
  font-size: 12px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(360px, 0.9fr);
  gap: 22px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.18fr) minmax(320px, 0.78fr);
  gap: 22px;
}

.analytics-card {
  min-width: 0;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.88)),
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.08), transparent 34%);
  box-shadow: var(--shadow-card);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}

.card-kicker {
  color: #2563eb;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.card-head h3 {
  margin: 6px 0 0;
  color: #0f172a;
  font-size: 19px;
  font-weight: 900;
  letter-spacing: -0.03em;
}

.card-badge {
  flex: 0 0 auto;
  padding: 6px 10px;
  color: #fff;
  border-radius: 999px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  font-size: 12px;
  font-weight: 850;
}

.card-badge.light {
  color: #2563eb;
  background: rgba(219, 234, 254, 0.86);
}

.chart {
  height: 318px;
}

.chart-large {
  height: 350px;
}

.hot-list {
  display: grid;
  gap: 13px;
}

.hot-row {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  gap: 13px;
  align-items: center;
  padding: 12px;
  border: 1px solid rgba(226, 232, 240, 0.86);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
}

.rank {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: #64748b;
  border-radius: 12px;
  background: #f1f5f9;
  font-weight: 900;
}

.rank.top {
  color: #fff;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
}

.hot-main {
  min-width: 0;
}

.hot-title {
  overflow: hidden;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 850;
}

.hot-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
}

.heat-bar {
  height: 7px;
  overflow: hidden;
  margin-top: 10px;
  border-radius: 999px;
  background: #e2e8f0;
}

.heat-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #38bdf8, #2563eb, #8b5cf6);
}

.insight-list {
  display: grid;
  gap: 14px;
}

.insight-item {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(226, 232, 240, 0.86);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.insight-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  color: #2563eb;
  border-radius: 16px;
  background: rgba(219, 234, 254, 0.8);
  font-weight: 950;
}

.insight-item strong {
  display: block;
  color: #0f172a;
  font-size: 14px;
  line-height: 1.45;
}

.insight-item p {
  margin: 5px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.65;
}

@media (max-width: 1280px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .analysis-grid,
  .bottom-grid,
  .dashboard-hero {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    min-height: 240px;
  }
}
</style>
