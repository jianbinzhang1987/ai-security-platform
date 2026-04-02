<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="设备标识" prop="machineId">
        <el-input v-model="queryParams.machineId" placeholder="请输入设备标识或Hostname" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 160px">
          <el-option label="正常" value="0" />
          <el-option label="封禁 (黑名单)" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Lock" :disabled="multiple" @click="handleBlock" v-hasPermi="['agentsec:fingerprint:block']">批量封禁</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="fingerprintList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column prop="machineId" label="设备指纹 (Machine ID)" min-width="250" show-overflow-tooltip />
      <el-table-column prop="hostname" label="主机名" min-width="150" />
      <el-table-column prop="os" label="操作系统" width="120" />
      <el-table-column prop="ipAddress" label="最近来源 IP" width="140" />
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '正常' : '已拉黑' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastRegisterTime" label="最近注册时间" width="180" />
      <el-table-column label="操作" width="150" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button v-if="scope.row.status === '0'" type="text" icon="Lock" @click="handleBlock(scope.row)" v-hasPermi="['agentsec:fingerprint:block']">拉黑</el-button>
          <el-button v-else type="text" icon="Unlock" @click="handleUnblock(scope.row)" v-hasPermi="['agentsec:fingerprint:unblock']">解封</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecFingerprint">
import { reactive, ref } from 'vue'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const fingerprintList = ref([])
const multiple = ref(true)
const queryRef = ref()
const selectedIds = ref([])

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  machineId: undefined,
  status: undefined
})

function getList() {
  loading.value = true
  // Mock data for UI presentation
  setTimeout(() => {
    fingerprintList.value = [
      { id: 1, machineId: 'a1b2c3d4e5f6g7h8i9j0', hostname: 'server-prod-01', os: 'Linux', ipAddress: '192.168.1.10', status: '0', lastRegisterTime: '2026-03-31 10:00:00' },
      { id: 2, machineId: 'z0y9x8w7v6u5t4s3r2q1', hostname: 'desktop-dev-local', os: 'Windows', ipAddress: '10.0.0.5', status: '1', lastRegisterTime: '2026-03-30 15:30:00' }
    ]
    total.value = 2
    loading.value = false
  }, 500)
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryRef.value?.resetFields()
  handleQuery()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
  multiple.value = !selection.length
}

function handleBlock(row) {
  const ids = row.id || selectedIds.value;
  console.log('Blocking fingerprints:', ids);
  // Implementation of block logic goes here
}

function handleUnblock(row) {
  const id = row.id;
  console.log('Unblocking fingerprint:', id);
  // Implementation of unblock logic goes here
}

getList()
</script>
