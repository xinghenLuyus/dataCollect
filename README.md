<div align="center">

[English](README.EN.md) | 中文

</div>

# 数据采集API服务

这是一个基于FastAPI的多组数据采集服务，可以定时采集外部API的JSON数据并提供循环播放功能。

## 功能特性

- 🚀 **多组数据采集**: 支持同时采集多组数据，每组独立管理
- 🔄 **循环播放**: 每组数据都有独立的播放索引，可以循环获取数据
- 💾 **数据持久化**: 使用SQLite数据库本地存储所有采集的数据
- ⚡ **异步处理**: 基于FastAPI和asyncio的高性能异步处理
- 🎛️ **灵活控制**: 支持手动开始/停止采集，实时状态监控
- 📊 **详细统计**: 提供完整的数据统计和状态信息
- 🔌 **RESTful API**: 完整的REST API接口，易于集成

## 系统要求

- **Python**: 3.7+ (推荐使用 Python 3.8 或更高版本)
- **依赖包**: 详见 `requirements.txt`

## 安装和设置

### 1. 克隆或下载项目文件

确保你有以下文件：
- `main.py` - 主程序文件
- `requirements.txt` - 依赖包列表
- `README.md` - 说明文档

### 2. 安装依赖包

```bash
pip install -r requirements.txt
```

或者手动安装：
```bash
pip install fastapi==0.104.1 uvicorn==0.24.0 aiohttp==3.9.1
```

### 3. 修改配置

- 找到 `main.py` 文件头部的配置行
- 确保修改 `API_URL` 为你的数据源API

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## API接口文档

### 基础信息

- **服务地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs (Swagger UI)
- **数据格式**: JSON
- **数据源**: https://www.example.com

### 核心接口

#### 1. 采集控制

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/start/{group_id}` | 开始指定组数据采集 |
| POST | `/start` | 开始组1数据采集（默认） |
| POST | `/stop/{group_id}` | 停止指定组数据采集 |
| POST | `/stop` | 停止组1数据采集（默认） |

#### 2. 数据播放

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/current/{group_id}` | 获取指定组当前数据（循环切换） |
| GET | `/current` | 获取组1当前数据（默认） |

#### 3. 数据查询

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/all/{group_id}` | 获取指定组的所有数据 |
| GET | `/all` | 获取所有组的数据 |

#### 4. 状态监控

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/status/{group_id}` | 获取指定组采集状态 |
| GET | `/status` | 获取所有组采集状态 |
| GET | `/groups` | 获取有数据的组列表 |
| GET | `/stats` | 获取全局统计信息 |

#### 5. 其他功能

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/collect` | 手动触发一次数据采集（测试用） |
| GET | `/` | 获取API接口列表 |

## 使用示例

### 基本操作流程

1. **启动服务**
   ```bash
   python main.py
   ```

2. **开始数据采集**
   ```bash
   # 开始组1数据采集
   curl -X POST http://localhost:8000/start/1
   
   # 开始组2数据采集
   curl -X POST http://localhost:8000/start/2
   ```

3. **获取数据（循环播放）**
   ```bash
   # 获取组1当前数据
   curl http://localhost:8000/current/1
   
   # 再次调用，获取下一条数据
   curl http://localhost:8000/current/1
   ```

4. **查看状态**
   ```bash
   # 查看所有组状态
   curl http://localhost:8000/status
   
   # 查看组1状态
   curl http://localhost:8000/status/1
   ```

5. **停止采集**
   ```bash
   # 停止组1采集
   curl -X POST http://localhost:8000/stop/1
   ```

### 高级用例

#### 多组并行采集
```bash
# 同时启动多组采集
curl -X POST http://localhost:8000/start/1
curl -X POST http://localhost:8000/start/2
curl -X POST http://localhost:8000/start/3

# 并行获取不同组的数据
curl http://localhost:8000/current/1 &
curl http://localhost:8000/current/2 &
curl http://localhost:8000/current/3 &
```

#### 数据统计和监控
```bash
# 获取详细统计信息
curl http://localhost:8000/stats

# 获取组列表和详情
curl http://localhost:8000/groups

# 获取指定组的所有历史数据
curl http://localhost:8000/all/1
```

## 配置说明

### 可配置参数

在 `main.py` 文件顶部可以修改以下配置：

```python
# 配置
API_URL = "https://www.example.com"  # 数据源API地址
DB_PATH = "data_collection.db"                    # 数据库文件路径
COLLECT_INTERVAL = 1                              # 采集间隔（秒）
```

### 服务配置

```python
# 在 if __name__ == "__main__": 中修改
uvicorn.run(
    "main:app",
    host="0.0.0.0",    # 监听地址
    port=8000,         # 监听端口
    reload=False,      # 是否热重载
    log_level="info"   # 日志级别
)
```

## 数据存储

### 数据库结构

使用SQLite数据库存储采集的数据，表结构如下：

```sql
CREATE TABLE collected_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL DEFAULT 1,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    data TEXT NOT NULL
);
```

### 数据文件

- **数据库文件**: `data_collection.db`
- **位置**: 与主程序同目录
- **格式**: SQLite 3

## 响应格式

### 成功响应示例

#### 获取当前数据
```json
{
  "group_id": 1,
  "current_data": {
    "id": 1,
    "group_id": 1,
    "timestamp": "2025-09-02 10:30:00",
    "data": { /* 原始API数据 */ }
  },
  "next_update": "下次调用将返回下一条数据"
}
```

#### 状态信息
```json
{
  "group_id": 1,
  "is_collecting": true,
  "total_records": 150,
  "current_index": 5,
  "status": "collecting"
}
```

#### 组列表
```json
{
  "available_groups": [1, 2, 3],
  "group_details": [
    {
      "group_id": 1,
      "total_records": 150,
      "current_index": 5,
      "is_collecting": true,
      "latest_record": "2025-09-02 10:30:00"
    }
  ]
}
```

### 错误响应示例

```json
{
  "detail": "组1暂无采集数据"
}
```

## 常见问题

### Q: 如何修改采集间隔？
A: 修改 `main.py` 中的 `COLLECT_INTERVAL` 变量，单位为秒。

### Q: 数据会自动循环播放吗？
A: 是的，当播放到最后一条数据时，下次调用会自动从第一条开始。

### Q: 可以同时采集多少组数据？
A: 理论上没有限制，但建议根据系统性能和目标API的负载能力来决定。

### Q: 如何备份数据？
A: 直接复制 `data_collection.db` 文件即可。

### Q: 如何清空某组的数据？
A: 可以直接操作SQLite数据库：
```sql
DELETE FROM collected_data WHERE group_id = 1;
```

### Q: 服务异常退出后数据会丢失吗？
A: 不会，所有数据都保存在SQLite数据库中，重启服务后数据仍然可用。

## 开发和扩展

### 项目结构
```
dataCollect/
├── main.py              # 主程序文件
├── requirements.txt     # 依赖包列表
├── README.md           # 说明文档
└── data_collection.db  # 数据库文件（运行后生成）
```

## 许可证

MIT

---