<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="Session ID" prop="sessionId">
        <el-input v-model="queryParams.sessionId" placeholder="请输入 Session ID" clearable style="width: 240px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="sessionList">
      <el-table-column prop="sessionId" label="Session ID" min-width="240" />
      <el-table-column prop="totalSpans" label="Span数" width="100" />
      <el-table-column prop="durationMs" label="耗时(ms)" width="120" />
    </el-table>
  </div>
</template>

<script setup name="AgentsecSessions">
import { reactive, ref } from 'vue'
import { getSession } from '@/api/agentsec/session'

const loading = ref(false)
const showSearch = ref(true)
const sessionList = ref([])
const queryRef = ref()

const queryParams = reactive({
  sessionId: ''
})

function getList() {
  if (!queryParams.sessionId) {
    sessionList.value = []
    return
  }
  loading.value = true
  getSession(queryParams.sessionId).then(response => {
    sessionList.value = response.data ? [response.data] : []
  }).finally(() => {
    loading.value = false
  })
}

function handleQuery() {
  getList()
}

function resetQuery() {
  queryRef.value?.resetFields()
  sessionList.value = []
}
</script>
