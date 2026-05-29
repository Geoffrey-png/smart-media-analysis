<template>
  <div class="page audit-page">
    <section class="page-header audit-hero">
      <div>
        <div class="hero-kicker">CONTENT SAFETY REVIEW</div>
        <h2 class="page-title">内容审核</h2>
        <p class="header-desc">集中处理待审核、敏感词命中和需要人工确认的内容，保障内容安全与发布质量。</p>
      </div>
      <el-button type="primary" size="large" :loading="loading" @click="loadData">刷新审核池</el-button>
    </section>

    <section class="audit-card card">
      <el-alert
        title="待审核内容通常来自新增内容、智能分析发现敏感词或运营手动提交。"
        type="info"
        show-icon
        :closable="false"
        class="audit-alert"
      />

      <div class="audit-summary">
        <div>
          <span>待处理</span>
          <strong>{{ total }}</strong>
        </div>
        <div>
          <span>敏感命中</span>
          <strong>{{ sensitiveCount }}</strong>
        </div>
        <div>
          <span>平均质量</span>
          <strong>{{ avgQuality }}</strong>
        </div>
      </div>

      <div class="table-head">
        <div>
          <span class="card-kicker">Review Queue</span>
          <h3>审核队列</h3>
        </div>
        <span class="muted">建议优先处理敏感词命中的内容</span>
      </div>

      <el-table v-loading="loading" :data="tableData">
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="110" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="敏感词" min-width="160">
          <template #default="{ row }">
            <el-tag
              v-for="word in row.sensitive_words"
              :key="word"
              type="danger"
              size="small"
              style="margin-right: 4px"
            >
              {{ word }}
            </el-tag>
            <span v-if="!row.sensitive_words?.length" class="muted">无</span>
          </template>
        </el-table-column>
        <el-table-column label="质量 / 热度" width="150">
          <template #default="{ row }">
            <div class="score-line">
              <span>质量 {{ Number(row.quality_score || 0).toFixed(1) }}</span>
              <span>热度 {{ Number(row.heat_score || 0).toFixed(1) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/contents/${row.id}`)">详情</el-button>
            <el-button text type="success" @click="openAudit(row, 'published')">通过</el-button>
            <el-button text type="danger" @click="openAudit(row, 'rejected')">拒绝</el-button>
            <el-button text @click="openAudit(row, 'offline')">下架</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        class="audit-pagination"
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        @current-change="loadData"
        @size-change="loadData"
      />
    </section>

    <el-dialog v-model="dialogVisible" title="审核操作" width="540px">
      <el-form :model="auditForm" label-width="92px">
        <el-form-item label="内容">
          <span>{{ currentRow?.title }}</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="auditForm.status">
            <el-option label="已发布" value="published" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已下架" value="offline" />
            <el-option label="待审核" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="auditForm.audit_comment" type="textarea" :rows="4" placeholder="请输入审核意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAudit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { auditContent, fetchPendingContents } from '../api/content'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const currentRow = ref(null)
const query = reactive({ page: 1, page_size: 10 })
const auditForm = reactive({
  status: 'published',
  audit_comment: ''
})

const sensitiveCount = computed(() => tableData.value.filter(item => item.sensitive_words?.length).length)
const avgQuality = computed(() => {
  if (!tableData.value.length) return '0.0'
  const value = tableData.value.reduce((sum, item) => sum + Number(item.quality_score || 0), 0) / tableData.value.length
  return value.toFixed(1)
})

async function loadData() {
  loading.value = true
  try {
    const res = await fetchPendingContents(query)
    tableData.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

function openAudit(row, status) {
  currentRow.value = row
  auditForm.status = status
  auditForm.audit_comment = status === 'published' ? '审核通过' : ''
  dialogVisible.value = true
}

async function submitAudit() {
  await auditContent(currentRow.value.id, auditForm)
  ElMessage.success('审核完成')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.audit-page {
  display: grid;
  gap: 20px;
}

.audit-hero {
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

.audit-card {
  padding: 22px;
}

.audit-alert {
  margin-bottom: 18px;
  border-radius: 16px;
}

.audit-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.audit-summary div {
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(255, 251, 235, 0.66)),
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.14), transparent 42%);
}

.audit-summary span,
.audit-summary strong {
  display: block;
}

.audit-summary span {
  color: #64748b;
  font-size: 13px;
}

.audit-summary strong {
  margin-top: 8px;
  color: #0f172a;
  font-size: 30px;
  font-weight: 950;
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

.score-line {
  display: grid;
  gap: 3px;
}

.score-line span {
  color: #475569;
  font-size: 12px;
  font-weight: 800;
}

.audit-pagination {
  margin-top: 18px;
}
</style>
