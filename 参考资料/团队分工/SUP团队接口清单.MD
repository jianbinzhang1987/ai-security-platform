# SUP 团队接口清单

## 接口概述

SUP 团队需要向下游（AI 安全防护插件、智能体中心）提供的所有接口。

---

## 核心接口列表

| 序号        | 接口名称                         | 类型            | 优先级 | 说明                                     |
| ----------- | -------------------------------- | --------------- | ------ | ---------------------------------------- |
| **1** | **权限查询 API**           | REST            | P0     | 核心接口，用于权限决策                   |
| **2** | **HTTP Header 注入**       | Gateway Plugin  | P0     | 网关层自动写入，无需主动调用             |
| **3** | **Token 验证 API**         | Internal        | P0     | 可选，用于二次验证                       |
| **4** | **权限变更推送**           | WebSocket/Event | P1     | 可选，用于实时同步                       |
| **5** | **基础数据同步 API**       | REST            | P1     | 管理面：用于获取用户/组织/角色列表       |
| **6** | **资源列表查询 API**       | REST            | P1     | 管理面：用于查询用户可访问的资源池       |
| **7** | **账号/Token封禁处置 API** | REST            | P1     | 控制面：用于安全发现严重攻击后的联合阻断 |

---

## 接口详解

### 1. 权限查询 API（核心）

**接口路径**

```
POST /api/v1/authz/check
```

**作用**：根据用户身份和资源信息查询用户是否有权访问该资源。

**请求参数**

| 参数名            | 类型   | 必填 | 说明                                                           |
| ----------------- | ------ | ---- | -------------------------------------------------------------- |
| `token`         | string | 是   | 用户 Token（JWT 或 Session ID）                                |
| `resource_type` | string | 是   | 资源类型，可选值：`model`、`agent`、`mcp`、`skill`     |
| `resource_id`   | string | 是   | 资源唯一标识                                                   |
| `operation`     | string | 是   | 操作类型，可选值：`read`、`write`、`execute`、`delete` |
| `tenant_id`     | string | 否   | 租户 ID，用于多租户隔离；如果 token 中已包含则可省略           |

**请求示例**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "resource_type": "agent",
  "resource_id": "agent_123",
  "operation": "execute",
  "tenant_id": "tenant_001"
}
```

**响应参数**

| 参数名                    | 类型          | 说明                                    |
| ------------------------- | ------------- | --------------------------------------- |
| `code`                  | int           | 状态码，0 表示成功，其他表示失败        |
| `message`               | string        | 错误信息                                |
| `data.allow`            | bool          | 是否允许，`true` 允许，`false` 拒绝 |
| `data.user_id`          | string        | 用户 ID                                 |
| `data.org_id`           | string        | 组织 ID                                 |
| `data.roles`            | array[string] | 用户角色列表                            |
| `data.permission_level` | int           | 权限等级（1-10）                        |
| `data.resource_owner`   | string        | 资源所有者 ID                           |
| `data.resource_public`  | bool          | 资源是否公开                            |
| `data.deny_reason`      | string        | 拒绝原因（allow=false 时）              |

**响应示例（允许）**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "allow": true,
    "user_id": "user_456",
    "org_id": "org_789",
    "roles": ["admin", "developer"],
    "permission_level": 9,
    "resource_owner": "user_456",
    "resource_public": false
  }
}
```

**响应示例（拒绝）**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "allow": false,
    "user_id": "user_456",
    "org_id": "org_789",
    "roles": ["user"],
    "permission_level": 3,
    "resource_owner": "user_789",
    "resource_public": false,
    "deny_reason": "权限不足：需要 admin 角色"
  }
}
```

**性能要求**

- 响应时间：< 50ms（P95）
- 可用性：> 99.9%

**使用场景**

- 安全插件在 MCP Tool 执行前进行权限二次确认
- 智能体中心异步执行任务时进行权限校验
- AI 安全平台审计时查询用户权限快照

---

### 2. HTTP Header 注入（网关层）

**作用**：SUP 业务插件在鉴权通过后，将用户信息写入 HTTP Header，供下游插件和应用读取。

**注入时机**：在 SUP 业务控制插件执行完成后，继续将请求转发给下游插件/应用前。

**必须注入的 Header**

| Header 名              | 类型   | 说明                     | 示例                |
| ---------------------- | ------ | ------------------------ | ------------------- |
| `X-User-Id`          | string | 用户唯一标识             | `user_456`        |
| `X-Org-Id`           | string | 用户所属组织             | `org_789`         |
| `X-Tenant-Id`        | string | 租户标识                 | `tenant_001`      |
| `X-Roles`            | string | 用户角色，多个用逗号分隔 | `admin,developer` |
| `X-Permission-Level` | int    | 权限等级（1-10）         | `9`               |
| `X-Resource-Type`    | string | 当前请求的资源类型       | `agent`           |
| `X-Resource-Id`      | string | 当前请求的资源 ID        | `agent_123`       |
| `X-Request-Time`     | long   | 请求时间戳（毫秒）       | `1713607200000`   |
| `X-Token-Expiry`     | long   | Token 过期时间戳（毫秒） | `1713693600000`   |

**HTTP Header 注入示例**

```http
GET /api/v1/agents/agent_123 HTTP/1.1
Host: gateway.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-User-Id: user_456
X-Org-Id: org_789
X-Tenant-Id: tenant_001
X-Roles: admin,developer
X-Permission-Level: 9
X-Resource-Type: agent
X-Resource-Id: agent_123
X-Request-Time: 1713607200000
X-Token-Expiry: 1713693600000
```

**读取方式**（下游应用）

- **Go**: `r.Header.Get("X-User-Id")`
- **Java**: `request.getHeader("X-User-Id")`
- **Python**: `request.headers.get("X-User-Id")`

---

### 3. Token 验证 API（可选）

**接口路径**

```
POST /api/v1/token/verify
```

**作用**：验证单个 Token 的合法性和有效期。用于离线场景或安全插件的二次验证。

**请求参数**

| 参数名    | 类型   | 必填 | 说明           |
| --------- | ------ | ---- | -------------- |
| `token` | string | 是   | 待验证的 Token |

**请求示例**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应参数**

| 参数名              | 类型   | 说明                     |
| ------------------- | ------ | ------------------------ |
| `code`            | int    | 0 表示有效，其他表示失效 |
| `message`         | string | 验证结果描述             |
| `data.valid`      | bool   | Token 是否有效           |
| `data.user_id`    | string | 用户 ID                  |
| `data.expires_at` | long   | 过期时间戳（毫秒）       |
| `data.issued_at`  | long   | 签发时间戳（毫秒）       |

**响应示例（有效）**

```json
{
  "code": 0,
  "message": "token valid",
  "data": {
    "valid": true,
    "user_id": "user_456",
    "expires_at": 1713693600000,
    "issued_at": 1713607200000
  }
}
```

---

### 4. 基础数据同步与查询 API（管理面补充）

**作用**：AI 安全治理系统（控制台）在配置安全策略、展示审计日志时，需要从 SUP 获取基础数据。

- **获取组织/角色列表**：`GET /api/v1/orgs` 和 `GET /api/v1/roles`（用于安全平台基于角色/部门配置防护策略）
- **用户信息补全查询**：`POST /api/v1/users/batch`（审计日志中仅有 `user_id`，在 UI 展示时需批量请求 SUP 获取用户真实姓名、所属部门等）

---

### 5. 资源列表查询 API（管理面补充）

**接口路径**：`GET /api/v1/authz/resources`
**作用**：对应分工方案中的“资源授权”，支持查询某特定用户当前被授权可访问的所有大模型、智能体、MCP 工具清单，以便安全平台进行资产级安全统计与展示。

---

### 6. 安全联合处置/风控 API（控制面补充）

**接口路径**：`POST /api/v1/risk/action`
**作用**：当 AI 安全防护模块检测到极高危的安全事件（如连续越狱、核心数据窃取试图）时，除了在网关层实时阻断当前请求，还需要调用 SUP 团队提供的处置 API。
**请求操作**：

- `action: "suspend_token"` (吊销当前会话 Token)
- `action: "suspend_user"` (冻结此用户账号)
- `action: "downgrade_role"` (降低用户权限等级)
  **联动意义**：实现“安全检测（AI 团队） -> 业务管控执行（SUP 团队）”的完美解耦闭环。

---

## 接口调用时序图

```
请求方 → SUP 网关 → SUP 业务插件 → SUP Header注入 → 安全插件 → 业务应用
  ↓         ↓          ↓            ↓           ↓        ↓
  请求     Token验证   权限查询    写入Header   读取Header  处理请求
           (1)        (2)         (3)         (4)        (5)

Optional: 如果安全插件需要二次确认权限
  安全插件 → SUP Authz API → SUP 权限服务 → 返回权限决策
    ↓        ↓              ↓             ↓
   权限查询  POST /v1/authz/check  权限管理数据库  决策结果
```

---

## 接口 SLA 约定

| 接口           | 响应时间（P95） | 可用性  | 容量      | 备注                  |
| -------------- | --------------- | ------- | --------- | --------------------- |
| 权限查询 API   | < 50ms          | > 99.9% | > 10k QPS | 支持本地缓存          |
| Token 验证 API | < 20ms          | > 99.9% | > 50k QPS | JWT 快速验签          |
| 权限变更推送   | -               | > 99.5% | -         | 异步推送，可延迟1-2秒 |

---

## 错误码规范

| 错误码 | HTTP 状态码 | 说明             |
| ------ | ----------- | ---------------- |
| 0      | 200         | 成功             |
| 401    | 401         | Token 无效或过期 |
| 403    | 403         | 权限不足         |
| 404    | 404         | 资源不存在       |
| 429    | 429         | 请求频率过高     |
| 500    | 500         | 服务内部错误     |
| 503    | 503         | 服务暂时不可用   |
