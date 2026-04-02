<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="报告名称" prop="reportName">
        <el-input v-model="queryParams.reportName" placeholder="请输入报告名称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="reportList">
      <el-table-column prop="reportName" label="报告名称" min-width="220" />
      <el-table-column prop="reportType" label="报告类型" width="120" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="fileUrl" label="文件地址" min-width="240" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecReports">
import { reactive, ref } from 'vue'
import { listSecurityReport } from '@/api/agentsec/report'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const reportList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  reportName: undefined
})

function getList() {
  loading.value = true
  listSecurityReport(queryParams).then(response => {
    reportList.value = response.rows || []
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
