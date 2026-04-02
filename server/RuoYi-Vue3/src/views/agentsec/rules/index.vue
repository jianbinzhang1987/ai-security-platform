<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="规则名称" prop="ruleName">
        <el-input v-model="queryParams.ruleName" placeholder="请输入规则名称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" clearable style="width: 160px">
          <el-option label="启用" value="0" />
          <el-option label="停用" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>

    <el-table v-loading="loading" :data="ruleList">
      <el-table-column prop="ruleName" label="规则名称" min-width="220" />
      <el-table-column prop="riskLevel" label="风险等级" width="120" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="createTime" label="创建时间" width="180" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecRules">
import { reactive, ref } from 'vue'
import { listAlertRule } from '@/api/agentsec/rule'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const ruleList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  ruleName: undefined,
  status: undefined
})

function getList() {
  loading.value = true
  listAlertRule(queryParams).then(response => {
    ruleList.value = response.rows || []
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
