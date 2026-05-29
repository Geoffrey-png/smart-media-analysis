<template>
  <div class="page user-page">
    <section class="page-header user-hero">
      <div>
        <div class="hero-kicker">USER & ROLE ADMINISTRATION</div>
        <h2 class="page-title">用户管理</h2>
        <p class="header-desc">管理员可以维护用户资料、角色权限和账号状态。角色和状态会直接影响后端接口访问权限。</p>
      </div>
      <el-button type="primary" size="large" @click="openDialog()">新增用户</el-button>
    </section>

    <section class="user-card card">
      <div class="toolbar user-toolbar">
        <el-input v-model="filters.keyword" placeholder="搜索用户名 / 昵称" clearable style="width: 280px" @keyup.enter="loadData" />
        <el-select v-model="filters.role" placeholder="角色" clearable style="width: 140px">
          <el-option label="管理员" value="admin" />
          <el-option label="编辑" value="editor" />
          <el-option label="审核员" value="auditor" />
          <el-option label="观察者" value="viewer" />
        </el-select>
        <el-select v-model="filters.status" placeholder="账号状态" clearable style="width: 140px">
          <el-option label="正常" value="active" />
          <el-option label="已禁用" value="disabled" />
        </el-select>
        <el-button type="primary" @click="loadData">查询</el-button>
      </div>

      <div class="user-grid">
        <article v-for="user in tableData.slice(0, 6)" :key="user.id" class="profile-tile">
          <div class="profile-avatar">{{ avatarText(user) }}</div>
          <div class="profile-main">
            <h3>{{ user.nickname || user.username }}</h3>
            <p>{{ user.city || '未知城市' }} · {{ genderLabel(user.gender) }} · {{ user.age || '-' }} 岁</p>
            <div class="role-status">
              <el-tag size="small" type="primary">{{ roleLabel(user.role) }}</el-tag>
              <el-tag size="small" :type="statusType(user.status)">{{ statusLabel(user.status) }}</el-tag>
            </div>
          </div>
        </article>
      </div>

      <div class="table-head">
        <div>
          <span class="card-kicker">User Table</span>
          <h3>用户明细</h3>
        </div>
        <span class="muted">共 {{ tableData.length }} 个用户</span>
      </div>

      <el-table :data="tableData">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="画像信息" width="220">
          <template #default="{ row }">
            <div class="profile-line">
              <span>{{ genderLabel(row.gender) }} / {{ row.age || '-' }} 岁</span>
              <small>{{ row.city || '未知城市' }}</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="兴趣标签" min-width="260">
          <template #default="{ row }">
            <div class="tag-list">
              <el-tag v-for="tag in row.interests" :key="tag" size="small">{{ tag }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/users/${row.id}/profile`)">画像</el-button>
            <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button text :type="row.status === 'disabled' ? 'success' : 'warning'" @click="handleToggleStatus(row)">
              {{ row.status === 'disabled' ? '启用' : '禁用' }}
            </el-button>
            <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新增用户'" width="560px">
      <el-form :model="form" label-width="92px">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password :placeholder="editingId ? '不修改请留空' : '请输入登录密码'" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 220px">
            <el-option label="管理员" value="admin" />
            <el-option label="编辑" value="editor" />
            <el-option label="审核员" value="auditor" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 220px">
            <el-option label="正常" value="active" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="昵称"><el-input v-model="form.nickname" /></el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="form.age" :min="0" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市"><el-input v-model="form.city" /></el-form-item>
        <el-form-item label="兴趣">
          <el-input v-model="interestInput" placeholder="多个兴趣用逗号分隔，例如 科技,财经,体育" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUser, deleteUser, fetchUsers, updateUser } from '../api/users'

const router = useRouter()
const tableData = ref([])
const filters = reactive({ page: 1, page_size: 50, keyword: '', role: '', status: '' })
const dialogVisible = ref(false)
const editingId = ref(null)
const interestInput = ref('')
const form = reactive(defaultForm())

function defaultForm() {
  return {
    username: '',
    password: '',
    role: 'viewer',
    status: 'active',
    nickname: '',
    age: 0,
    gender: 'unknown',
    city: '',
    interests: []
  }
}

function splitTags(value) {
  return String(value || '')
    .replace(/[，、]/g, ',')
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
}

function avatarText(user) {
  return String(user.nickname || user.username || 'U').slice(0, 1).toUpperCase()
}

function genderLabel(value) {
  return {
    male: '男',
    female: '女',
    unknown: '未知'
  }[value] || value || '未知'
}

function roleLabel(value) {
  return {
    admin: '管理员',
    editor: '编辑',
    auditor: '审核员',
    viewer: '观察者'
  }[value || 'viewer'] || '观察者'
}

function roleType(value) {
  return {
    admin: 'danger',
    editor: 'primary',
    auditor: 'warning',
    viewer: 'info'
  }[value || 'viewer'] || 'info'
}

function statusLabel(value) {
  return {
    active: '正常',
    disabled: '已禁用'
  }[value || 'active'] || '正常'
}

function statusType(value) {
  return {
    active: 'success',
    disabled: 'danger'
  }[value || 'active'] || 'success'
}

async function loadData() {
  const res = await fetchUsers(filters)
  tableData.value = res.data?.items || []
}

function openDialog(row) {
  editingId.value = row?.id || null
  Object.assign(form, defaultForm(), row || {})
  form.role = row?.role || 'viewer'
  form.status = row?.status || 'active'
  form.password = ''
  interestInput.value = (row?.interests || []).join(',')
  dialogVisible.value = true
}

async function submit() {
  const payload = { ...form, interests: splitTags(interestInput.value) }
  if (!editingId.value && !payload.password) {
    ElMessage.warning('新增用户必须设置密码')
    return
  }
  if (editingId.value && !payload.password) {
    delete payload.password
  }
  if (editingId.value) {
    await updateUser(editingId.value, payload)
  } else {
    await createUser(payload)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用户「${row.nickname || row.username}」？`, '删除确认', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('删除成功')
  loadData()
}

async function handleToggleStatus(row) {
  const nextStatus = row.status === 'disabled' ? 'active' : 'disabled'
  const action = nextStatus === 'disabled' ? '禁用' : '启用'
  await ElMessageBox.confirm(`确认${action}用户「${row.nickname || row.username}」？`, `${action}确认`, { type: 'warning' })
  await updateUser(row.id, { status: nextStatus })
  ElMessage.success(`${action}成功`)
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.user-page {
  display: grid;
  gap: 20px;
}

.user-hero {
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

.user-card {
  padding: 22px;
}

.user-toolbar {
  margin: 0 0 18px;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.user-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.profile-tile {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr);
  gap: 14px;
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 255, 0.68)),
    radial-gradient(circle at right top, rgba(14, 165, 233, 0.1), transparent 42%);
}

.profile-avatar {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  color: #fff;
  border-radius: 20px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  font-weight: 950;
}

.profile-main {
  min-width: 0;
}

.profile-main h3 {
  margin: 0;
  overflow: hidden;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 16px;
}

.profile-main p {
  margin: 6px 0 10px;
  color: #64748b;
  font-size: 13px;
}

.role-status {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
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

.profile-line {
  display: grid;
  gap: 3px;
}

.profile-line span {
  color: #0f172a;
  font-weight: 800;
}

.profile-line small {
  color: #94a3b8;
}

@media (max-width: 1280px) {
  .user-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
