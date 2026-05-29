<template>
  <div class="page stats-page">
    <section class="page-header stats-hero">
      <div>
        <div class="hero-kicker">DATA STATISTICS</div>
        <h2 class="page-title">数据统计</h2>
        <p class="header-desc">汇总内容分类、兴趣标签和平台核心数据，给运营策略提供基础判断。</p>
      </div>
      <el-button type="primary" size="large" :loading="loading" @click="loadData">刷新统计</el-button>
    </section>

    <section class="stats-strip">
      <div>
        <span>内容数</span>
        <strong>{{ formatNumber(summary.content_count || 0) }}</strong>
      </div>
      <div>
        <span>用户数</span>
        <strong>{{ formatNumber(summary.user_count || 0) }}</strong>
      </div>
      <div>
        <span>行为日志</span>
        <strong>{{ formatNumber(summary.behavior_count || 0) }}</strong>
      </div>
      <div>
        <span>今日浏览</span>
        <strong>{{ formatNumber(summary.today_views || 0) }}</strong>
      </div>
    </section>

    <section class="stats-grid">
      <article class="analytics-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Category Mix</span>
            <h3>分类分布</h3>
          </div>
          <span class="card-badge">内容结构</span>
        </div>
        <div ref="categoryRef" class="chart"></div>
      </article>

      <article class="analytics-card">
        <div class="card-head">
          <div>
            <span class="card-kicker">Interest Tags</span>
            <h3>兴趣标签 Top 10</h3>
          </div>
          <span class="card-badge light">用户画像</span>
        </div>
        <div ref="tagRef" class="chart"></div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { fetchDashboardSummary } from '../api/dashboard'

const loading = ref(false)
const summary = ref({})
const categoryRef = ref()
const tagRef = ref()
let charts = []

async function loadData() {
  loading.value = true
  try {
    const res = await fetchDashboardSummary()
    summary.value = res.data || {}
    await nextTick()
    render()
  } catch (error) {
    ElMessage.error('统计数据加载失败')
  } finally {
    loading.value = false
  }
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function getChart(el) {
  if (!el) return null
  const chart = echarts.getInstanceByDom(el) || echarts.init(el)
  if (!charts.includes(chart)) charts.push(chart)
  return chart
}

function render() {
  const categories = summary.value.category_distribution || []
  const tags = summary.value.interest_distribution || []
  const categoryChart = getChart(categoryRef.value)
  const tagChart = getChart(tagRef.value)

  categoryChart?.setOption({
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
        type: 'pie',
        radius: ['46%', '72%'],
        center: ['50%', '44%'],
        itemStyle: { borderColor: '#fff', borderWidth: 4 },
        label: { color: '#475569', formatter: '{b}' },
        data: categories
      }
    ]
  })

  tagChart?.setOption({
    color: ['#06b6d4'],
    grid: { left: 78, right: 24, top: 18, bottom: 28 },
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
      data: tags.map(item => item.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#475569', fontWeight: 700 }
    },
    series: [
      {
        type: 'bar',
        barWidth: 12,
        data: tags.map(item => item.value),
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
.stats-page {
  display: grid;
  gap: 20px;
}

.stats-hero {
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

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stats-strip div {
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.86)),
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.1), transparent 40%);
  box-shadow: var(--shadow-card);
}

.stats-strip span,
.stats-strip strong {
  display: block;
}

.stats-strip span {
  color: #64748b;
  font-size: 13px;
}

.stats-strip strong {
  margin-top: 10px;
  color: #0f172a;
  font-size: 31px;
  font-weight: 950;
  letter-spacing: -0.05em;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  height: 380px;
}

@media (max-width: 1280px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
