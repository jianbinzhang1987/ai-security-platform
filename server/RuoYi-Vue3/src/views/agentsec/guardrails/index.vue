<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="护栏名称" prop="name">
        <el-input v-model="queryParams.name" placeholder="请输入护栏名称" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="策略类型" prop="type">
        <el-select v-model="queryParams.type" placeholder="请选择类型" clearable style="width: 160px">
          <el-option label="正则匹配" value="regex" />
          <el-option label="LLM 评分" value="llm_eval" />
          <el-option label="语义相似度" value="semantic" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" v-hasPermi="['agentsec:guardrails:add']">新建护栏策略</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="guardrailsList">
      <el-table-column prop="name" label="护栏策略名称" min-width="150" />
      <el-table-column label="生效阶段" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.stage === 'input' ? 'warning' : 'success'">
            {{ scope.row.stage === 'input' ? 'Input(Prompt)' : 'Output(Response)' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="检测类型" width="120" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="动作" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.action === 'block' ? 'danger' : 'info'">
            {{ scope.row.action === 'block' ? '阻断' : '仅告警' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-switch v-model="scope.row.enabled" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button type="text" icon="Edit" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button type="text" icon="Delete" class="text-danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="AgentsecGuardrails">
import { reactive, ref } from 'vue'

const loading = ref(false)
const showSearch = ref(true)
const total = ref(0)
const guardrailsList = ref([])
const queryRef = ref()

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  name: undefined,
  type: undefined
})

function getList() {
  loading.value = true
  setTimeout(() => {
    guardrailsList.value = [
      { id: 1, name: '禁止政治敏感话题', stage: 'input', type: 'llm_eval', description: '调用判别模型检测Prompt是否包含敏感政治话题', action: 'block', enabled: true },
      { id: 2, name: '拦截竞品名称输出', stage: 'output', type: 'regex', description: '防止Response中推荐竞品(公司A, 公司B)', action: 'block', enabled: true },
      { id: 3, name: '内网IP探测行为模型', stage: 'input', type: 'semantic', description: '检测意图为探测内网边界的行为', action: 'alert', enabled: false }
    ]
    total.value = 3
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

function handleUpdate(row) {
  // Logic to update guardrail
}

function handleDelete(row) {
  // Logic to delete guardrail
}

getList()
</script>
