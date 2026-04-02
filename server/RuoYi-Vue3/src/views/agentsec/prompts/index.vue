<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="关键词" prop="keyword">
        <el-input v-model="queryParams.keyword" placeholder="请输入 Prompt 关键词" clearable style="width: 240px" @keyup.enter="handleSearch" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleSearch">检索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="promptList">
      <el-table-column prop="sessionId" label="Session ID" min-width="180" />
      <el-table-column prop="riskType" label="风险类型" width="140" />
      <el-table-column prop="riskLevel" label="风险等级" width="120" />
      <el-table-column prop="createTime" label="时间" width="180" />
    </el-table>
  </div>
</template>

<script setup name="AgentsecPrompts">
import { reactive, ref } from 'vue'
import { listPrompt, searchPrompt } from '@/api/agentsec/prompt'

const loading = ref(false)
const showSearch = ref(true)
const promptList = ref([])
const queryRef = ref()

const queryParams = reactive({
  keyword: ''
})

function getList() {
  loading.value = true
  listPrompt({ pageNum: 1, pageSize: 10 }).then(response => {
    promptList.value = response.rows || []
  }).finally(() => {
    loading.value = false
  })
}

function handleSearch() {
  loading.value = true
  searchPrompt({ keyword: queryParams.keyword }).then(response => {
    promptList.value = response.data || []
  }).finally(() => {
    loading.value = false
  })
}

function resetQuery() {
  queryRef.value?.resetFields()
  getList()
}

getList()
</script>
