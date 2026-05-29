<template>
  <div class="page reco-analysis-page">
    <section class="page-header reco-hero">
      <div>
        <div class="hero-kicker">RECOMMENDATION PERFORMANCE</div>
        <h2 class="page-title">推荐效果分析</h2>
        <p class="header-desc">用曝光、点击、CTR、场景效果和点击 Top 内容观察推荐策略表现。</p>
      </div>
      <el-button type="primary" size="large" :loading="loading" @click="loadData">刷新效果</el-button>
    </section>

    <section class="kpi-grid">
      <StatCard
        label="推荐曝光量"
        :value="formatNumber(summary.exposure_count || 0)"
        desc="推荐接口累计返回内容数"
        icon="曝"
        tone="blue"
        change="Exposure"
      />
      <StatCard
        label="推荐点击量"
        :value="formatNumber(summary.click_count || 0)"
        desc="用户从推荐位进入内容数"
        icon="点"
        tone="cyan"
        change="Click"
      />
      <StatCard
        label="点击率 CTR"
        :value="`${summary.ctr || 0}%`"
        desc="点击量 / 曝光量"
        icon="%"
        tone="purple"
        :change="ctrSignal"
      />
    </section>

    <section class="analysis-grid">
      <article class="analytics-card trend-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Trend</span>
            <h3>推荐曝光与点击趋势</h3>
          </div>
          <span class="card-badge">转化漏斗</span>
        </div>
        <div ref="trendRef" class="chart"></div>
      </article>

      <article class="analytics-card scene-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Scene</span>
            <h3>场景效果</h3>
          </div>
        </div>
        <div v-if="sceneStats.length" class="scene-list">
          <div v-for="item in sceneStats" :key="item.scene" class="scene-item">
            <div class="scene-top">
              <strong>{{ sceneLabel(item.scene) }}</strong>
              <span>{{ item.ctr || 0 }}%</span>
            </div>
            <el-progress :percentage="normalizeCtr(item.ctr)" :show-text="false" />
            <div class="scene-meta">
              <span>{{ formatNumber(item.exposure || 0) }} 曝光</span>
              <span>{{ formatNumber(item.click || 0) }} 点击</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无场景效果数据" />
      </article>
    </section>

    <article class="analytics-card top-card">
      <div class="card-head">
        <div>
          <span class="card-kicker">Top Clicked Contents</span>
          <h3>点击 Top 内容</h3>
        </div>
        <span class="card-badge light">内容转化</span>
      </div>

      <div v-if="topClicked.length" class="top-list">
        <div v-for="(item, index) in topClicked" :key="item.id || item.title" class="top-item">
          <div class="rank" :class="{ hot: index < 3 }">{{ index + 1 }}</div>
          <div class="top-main">
            <strong>{{ item.title || '未命名内容' }}</strong>
            <span>{{ item.category || '未分类' }}</span>
          </div>
          <div class="click-count">{{ formatNumber(item.clicks || 0) }} 点击</div>
        </div>
      </div>
      <el-empty v-else description="暂无点击数据" />
    </article>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import StatCard from '../components/StatCard.vue'
import { fetchRecommendationAnalytics } from '../api/recommendations'

const loading = ref(false)
const summary = ref({})
const trendRef = ref()
let trendChart = null

const sceneStats = computed(() => summary.value.scene_stats || [])
const topClicked = computed(() => summary.value.top_clicked_contents || [])
const ctrSignal = computed(() => {
  const ctr = Number(summary.value.ctr || 0)
  if (ctr >= 10) return '优秀'
  if (ctr >= 3) return '稳定'
  return '待优化'
})

async function loadData() {
  loading.value = true
  try {
    const res = await fetchRecommendationAnalytics()
    summary.value = res.data || {}
    await nextTick()
    renderTrend()
  } catch (error) {
    ElMessage.error('推荐效果数据加载失败')
  } finally {
    loading.value = false
  }
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function normalizeCtr(value) {
  return Math.max(0, Math.min(100, Number(value || 0)))
}

function sceneLabel(value) {
  return {
    user: '个性化推荐',
    hot: '热门推荐',
    mixed: '综合推荐',
    content: '相似内容'
  }[value] || value || '默认场景'
}

function renderTrend() {
  if (!trendRef.value) return
  const trend = summary.value.trend || []
  trendChart = echarts.getInstanceByDom(trendRef.value) || echarts.init(trendRef.value)
  trendChart.setOption({
    color: ['#2563eb', '#06b6d4'],
    grid: { left: 42, right: 22, top: 42, bottom: 30 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#fff' }
    },
    legend: {
      top: 0,
      right: 0,
      data: ['曝光', '点击'],
      icon: 'circle',
      textStyle: { color: '#64748b' }
    },
    xAxis: {
      type: 'category',
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
        name: '曝光',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 4 },
        areaStyle: { color: 'rgba(37, 99, 235, 0.1)' },
        data: trend.map(item => item.exposure)
      },
      {
        name: '点击',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 4 },
        areaStyle: { color: 'rgba(6, 182, 212, 0.1)' },
        data: trend.map(item => item.click)
      }
    ]
  })
}

function resizeChart() {
  trendChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  trendChart?.dispose()
})
</script>

<style scoped>
.reco-analysis-page {
  display: grid;
  gap: 20px;
}

.reco-hero {
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) 410px;
  gap: 20px;
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

.card-head h3 {
  margin: 6px 0 0;
  font-size: 19px;
  font-weight: 900;
}

.card-badge {
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
  height: 370px;
}

.scene-list {
  display: grid;
  gap: 15px;
}

.scene-item {
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.scene-top,
.scene-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.scene-top {
  margin-bottom: 12px;
}

.scene-top strong {
  color: #0f172a;
  font-size: 14px;
}

.scene-top span {
  color: #2563eb;
  font-size: 18px;
  font-weight: 950;
}

.scene-meta {
  margin-top: 10px;
  color: #94a3b8;
  font-size: 12px;
}

.top-list {
  display: grid;
  gap: 12px;
}

.top-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) 110px;
  gap: 14px;
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.rank {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  color: #64748b;
  border-radius: 14px;
  background: #f1f5f9;
  font-weight: 950;
}

.rank.hot {
  color: #fff;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
}

.top-main {
  min-width: 0;
}

.top-main strong,
.top-main span {
  display: block;
}

.top-main strong {
  overflow: hidden;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.top-main span {
  margin-top: 5px;
  color: #94a3b8;
  font-size: 12px;
}

.click-count {
  color: #2563eb;
  text-align: right;
  font-size: 14px;
  font-weight: 900;
}

@media (max-width: 1280px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
