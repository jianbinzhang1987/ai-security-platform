<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="应用名称" prop="appName">
        <el-input v-model="queryParams.appName" placeholder="请输入应用名称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 160px">
          <el-option label="正常" value="0" />
          <el-option label="停用" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" v-hasPermi="['agentsec:app:add']">新增</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="appList">
      <el-table-column prop="appName" label="应用名称" min-width="180" />
      <el-table-column prop="tenantId" label="租户ID" min-width="180" />
      <el-table-column prop="sdkVersion" label="SDK版本" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'info'">{{ scope.row.status === '0' ? '正常' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Token状态" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.tokenStatus === '0' ? 'success' : 'danger'">{{ scope.row.tokenStatus === '0' ? '有效' : '失效' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" width="180" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecAgents">
import { reactive, ref } from 'vue'
import { listAgentApp } from '@/api/agentsec/app'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const appList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  appName: undefined,
  status: undefined
})

function getList() {
  loading.value = true
  listAgentApp(queryParams).then(response => {
    appList.value = response.rows || []
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
