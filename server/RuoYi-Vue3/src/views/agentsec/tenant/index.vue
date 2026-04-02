<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="租户名称" prop="tenantName">
        <el-input v-model="queryParams.tenantName" placeholder="请输入租户名称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="tenantList">
      <el-table-column prop="tenantName" label="租户名称" min-width="180" />
      <el-table-column prop="planCode" label="套餐" width="120" />
      <el-table-column prop="maxAgents" label="最大Agent数" width="120" />
      <el-table-column prop="dataRetentionDays" label="保留天数" width="120" />
      <el-table-column prop="status" label="状态" width="100" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecTenant">
import { reactive, ref } from 'vue'
import { listTenant } from '@/api/agentsec/tenant'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const tenantList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  tenantName: undefined
})

function getList() {
  loading.value = true
  listTenant(queryParams).then(response => {
    tenantList.value = response.rows || []
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
