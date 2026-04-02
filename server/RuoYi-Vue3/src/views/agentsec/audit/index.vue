<template>
  <div class="app-container">
    <el-card class="mb8">
      <template #header>平台审计日志</template>
      <p>当前后端审计列表接口已预留，后续可直接切换到 `sys_oper_log` 或独立审计表实现。</p>
    </el-card>

    <el-button type="primary" icon="Refresh" @click="getList">刷新</el-button>

    <el-table v-loading="loading" :data="auditList" style="margin-top: 16px">
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="operName" label="操作人" width="120" />
      <el-table-column prop="businessType" label="类型" width="100" />
      <el-table-column prop="operTime" label="时间" width="180" />
    </el-table>
  </div>
</template>

<script setup name="AgentsecAudit">
import { ref } from 'vue'
import { listAudit } from '@/api/agentsec/audit'

const loading = ref(false)
const auditList = ref([])

function getList() {
  loading.value = true
  listAudit({ pageNum: 1, pageSize: 10 }).then(response => {
    auditList.value = response.rows || []
  }).finally(() => {
    loading.value = false
  })
}

getList()
</script>

<style scoped>
.mb8 {
  margin-bottom: 16px;
}
</style>
