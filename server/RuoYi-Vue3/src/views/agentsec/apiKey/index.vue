<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="Key名称" prop="apiKeyName">
        <el-input v-model="queryParams.apiKeyName" placeholder="请输入 Key 名称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="apiKeyList">
      <el-table-column prop="apiKeyName" label="Key名称" min-width="180" />
      <el-table-column prop="tenantId" label="租户ID" min-width="180" />
      <el-table-column prop="appId" label="应用ID" min-width="180" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="expireTimeText" label="过期时间" width="180" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecApiKey">
import { reactive, ref } from 'vue'
import { listApiKey } from '@/api/agentsec/apiKey'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const apiKeyList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  apiKeyName: undefined
})

function getList() {
  loading.value = true
  listApiKey(queryParams).then(response => {
    apiKeyList.value = response.rows || []
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
