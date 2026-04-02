<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" class="config-tabs">
      <el-tab-pane label="采样率配置" name="sampling">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>全局与特定链路采样率配置</span>
              <el-button type="primary" icon="Check" @click="saveSamplingConfig">保存配置</el-button>
            </div>
          </template>
          <el-form :model="samplingConfig" label-width="140px">
            <el-form-item label="全局采样率">
              <el-slider v-model="samplingConfig.global" :step="1" show-input />
              <div class="help-block">0% 为全部丢弃，100% 为全量采集。</div>
            </el-form-item>
            <el-form-item label="含安全异常的链路">
              <el-switch v-model="samplingConfig.forceSecurity" />
              <span class="ml-2 text-muted">开启后，带有安全风险标签的 Span 将被强制100%保留（尾部采样）。</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="工具黑白名单" name="tools">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>MCP 工具审计配置</span>
              <el-button type="primary" icon="Plus" @click="addToolRule">新增规则</el-button>
            </div>
          </template>
          <el-table :data="toolRules">
            <el-table-column prop="toolName" label="工具名称" />
            <el-table-column label="控制类型" width="150">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'whitelist' ? 'success' : 'danger'">
                  {{ scope.row.type === 'whitelist' ? '白名单允许' : '黑名单阻断' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述说明" min-width="200" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="text" icon="Delete" class="text-danger" @click="removeToolRule(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="PII 脱敏规则" name="pii">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>自定义敏感信息过滤正则</span>
              <el-button type="primary" icon="Plus" @click="addPiiRule">新增正则</el-button>
            </div>
          </template>
          <el-table :data="piiRules">
            <el-table-column prop="name" label="规则名称" width="180" />
            <el-table-column prop="pattern" label="正则表达式" />
            <el-table-column prop="replacement" label="替换内容" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-switch v-model="scope.row.enabled" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="text" icon="Delete" class="text-danger" @click="removePiiRule(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup name="AgentsecConfig">
import { ref, reactive } from 'vue'

const activeTab = ref('sampling')

const samplingConfig = reactive({
  global: 100,
  forceSecurity: true
})

const toolRules = ref([
  { toolName: 'execute_shell', type: 'blacklist', description: '禁止Agent执行系统Shell命令' },
  { toolName: 'read_db', type: 'whitelist', description: '允许访问指定的只读数据库' }
])

const piiRules = ref([
  { name: '员工工号识别', pattern: 'EMP\\d{6}', replacement: '[MASKED_EMP_ID]', enabled: true },
  { name: '内部IP地址', pattern: '10\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}', replacement: '[MASKED_IP]', enabled: false }
])

function saveSamplingConfig() {
  console.log('Saving sampling config', samplingConfig)
}

function addToolRule() {
  // Logic to add tool rule
}

function removeToolRule(index) {
  toolRules.value.splice(index, 1)
}

function addPiiRule() {
  // Logic to add PII rule
}

function removePiiRule(index) {
  piiRules.value.splice(index, 1)
}

</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.help-block {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
