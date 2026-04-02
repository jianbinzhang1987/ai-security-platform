<template>
  <div class="app-container">
    <el-row :gutter="16" class="mb16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover">
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card>
      <template #header>安全监测总览</template>
      <p>Dashboard 页面骨架已生成，后续可接入趋势图、风险热力图和实时告警流。</p>
    </el-card>
  </div>
</template>

<script setup name="AgentsecDashboard">
import { onMounted, ref } from 'vue'
import { getDashboardSummary } from '@/api/agentsec/dashboard'

const cards = ref([
  { label: 'Agent 应用', value: 0 },
  { label: '风险事件', value: 0 },
  { label: '高危告警', value: 0 },
  { label: '阻断次数', value: 0 }
])

onMounted(() => {
  getDashboardSummary().then((response) => {
    const data = response.data || {}
    cards.value = [
      { label: 'Agent 应用', value: data.appCount ?? 0 },
      { label: '风险事件', value: data.eventCount ?? 0 },
      { label: '高危告警', value: data.criticalCount ?? 0 },
      { label: '阻断次数', value: data.blockedCount ?? 0 }
    ]
  }).catch(() => {})
})
</script>

<style scoped>
.mb16 {
  margin-bottom: 16px;
}

.metric-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.metric-value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 600;
}
</style>
