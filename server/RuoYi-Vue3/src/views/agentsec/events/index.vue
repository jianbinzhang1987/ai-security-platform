<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="风险类型" prop="riskType">
        <el-input v-model="queryParams.riskType" placeholder="请输入风险类型" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" clearable style="width: 180px">
          <el-option label="new" value="new" />
          <el-option label="confirmed" value="confirmed" />
          <el-option label="closed" value="closed" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="eventList">
      <el-table-column prop="eventId" label="事件ID" min-width="220" />
      <el-table-column prop="riskType" label="风险类型" min-width="140" />
      <el-table-column prop="riskLevel" label="风险等级" width="120" />
      <el-table-column prop="sessionId" label="Session ID" min-width="180" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="createTime" label="发现时间" width="180" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecEvents">
import { reactive, ref } from 'vue'
import { listRiskEvent } from '@/api/agentsec/event'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const eventList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  riskType: undefined,
  status: undefined
})

function getList() {
  loading.value = true
  listRiskEvent(queryParams).then(response => {
    eventList.value = response.rows || []
    total.value = response.total || 0
  }).finally(() => {
    loading.value = false
  })
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryRef.value?.resetFields()
  handleQuery()
}

getList()
</script>
