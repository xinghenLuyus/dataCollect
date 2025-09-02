import asyncio
import sqlite3
import json
import time
from datetime import datetime
from typing import Optional
import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

# 配置
API_URL = "https://www.example.com"  # 数据源API地址
DB_PATH = "data_collection.db"
COLLECT_INTERVAL = 1  # 秒

class DataCollector:
    def __init__(self):
        self.db_path = DB_PATH
        self.current_indexes = {} 
        self.collecting_groups = {} 
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collected_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data TEXT NOT NULL
            )
        ''')
        # 添加索引提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_group_id ON collected_data(group_id)
        ''')
        conn.commit()
        conn.close()
        
    async def collect_data(self, group_id=1):
        """采集数据的异步方法"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.save_to_database(data, group_id)
                        print(f"组{group_id}数据采集成功: {datetime.now()}")
                        return data
                    else:
                        print(f"API请求失败，状态码: {response.status}")
                        return None
            except Exception as e:
                print(f"组{group_id}数据采集错误: {e}")
                return None
                
    def save_to_database(self, data, group_id=1):
        """保存数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO collected_data (group_id, data) VALUES (?, ?)",
            (group_id, json.dumps(data, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        
    def get_all_data(self, group_id=None):
        """获取所有采集的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if group_id is not None:
            cursor.execute("SELECT id, group_id, timestamp, data FROM collected_data WHERE group_id = ? ORDER BY id", (group_id,))
        else:
            cursor.execute("SELECT id, group_id, timestamp, data FROM collected_data ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "group_id": row[1],
                "timestamp": row[2],
                "data": json.loads(row[3])
            })
        return result
        
    def get_current_data(self, group_id=1):
        """获取指定组当前索引的数据"""
        all_data = self.get_all_data(group_id)
        if not all_data:
            return None
            
        # 获取该组的当前索引
        if group_id not in self.current_indexes:
            self.current_indexes[group_id] = 0
            
        current_index = self.current_indexes[group_id]
        
        # 循环获取数据
        if current_index >= len(all_data):
            current_index = 0
            
        current_data = all_data[current_index]
        self.current_indexes[group_id] = current_index + 1
        return current_data
        
    def start_collecting(self, group_id=1):
        """开始数据采集"""
        if group_id not in self.collecting_groups:
            task = asyncio.create_task(self.collect_task_for_group(group_id))
            self.collecting_groups[group_id] = task
            return True
        return False
        
    def stop_collecting(self, group_id=1):
        """停止数据采集"""
        if group_id in self.collecting_groups:
            task = self.collecting_groups[group_id]
            if not task.done():
                task.cancel()
            del self.collecting_groups[group_id]
            return True
        return False
        
    def get_collecting_status(self, group_id=None):
        """获取采集状态"""
        if group_id is not None:
            return group_id in self.collecting_groups
        else:
            return {gid: gid in self.collecting_groups for gid in range(1, 10)}  # 返回1-9组的状态
            
    async def collect_task_for_group(self, group_id):
        """指定组的持续采集任务"""
        while group_id in self.collecting_groups:
            await self.collect_data(group_id)
            await asyncio.sleep(COLLECT_INTERVAL)
            
    def get_available_groups(self):
        """获取有数据的组列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT group_id FROM collected_data ORDER BY group_id")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

# 全局数据采集器实例
collector = DataCollector()

# FastAPI应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时不自动开始采集，等待手动开启
    print("服务已启动，等待手动开启数据采集...")
    yield
    # 关闭时停止所有采集
    for group_id in list(collector.collecting_groups.keys()):
        collector.stop_collecting(group_id)
    print("服务已停止...")

# 创建FastAPI应用
app = FastAPI(
    title="数据采集API",
    description="采集http://frp-pet.com:60176/api/v1/all的数据并提供API接口",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "数据采集API服务",
        "endpoints": {
            "/current/{group_id}": "获取指定组当前数据（每次调用切换到下一条）",
            "/all": "获取所有采集的数据",
            "/all/{group_id}": "获取指定组的所有数据",
            "/stats": "获取统计信息",
            "/start/{group_id}": "开始指定组数据采集",
            "/stop/{group_id}": "停止指定组数据采集",
            "/status": "获取所有组采集状态",
            "/status/{group_id}": "获取指定组采集状态",
            "/groups": "获取有数据的组列表"
        }
    }

@app.get("/current/{group_id}")
async def get_current_by_group(group_id: int):
    """获取指定组当前数据，每次调用会切换到下一条数据"""
    data = collector.get_current_data(group_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"组{group_id}暂无采集数据")
    return {
        "group_id": group_id,
        "current_data": data,
        "next_update": "下次调用将返回下一条数据"
    }

@app.get("/current")
async def get_current():
    """获取组1当前数据，每次调用会切换到下一条数据"""
    return await get_current_by_group(1)

@app.get("/all")
async def get_all():
    """获取所有采集的数据"""
    data = collector.get_all_data()
    return {
        "total_count": len(data),
        "data": data
    }

@app.get("/all/{group_id}")
async def get_all_by_group(group_id: int):
    """获取指定组的所有数据"""
    data = collector.get_all_data(group_id)
    return {
        "group_id": group_id,
        "total_count": len(data),
        "data": data
    }

@app.get("/stats")
async def get_stats():
    """获取统计信息"""
    all_data = collector.get_all_data()
    available_groups = collector.get_available_groups()
    
    if all_data:
        latest = all_data[-1]["timestamp"]
        earliest = all_data[0]["timestamp"]
    else:
        latest = earliest = None
        
    return {
        "total_records": len(all_data),
        "available_groups": available_groups,
        "current_indexes": collector.current_indexes,
        "latest_collection": latest,
        "earliest_collection": earliest,
        "collection_interval": f"{COLLECT_INTERVAL}秒"
    }

# 添加一个手动触发采集的接口（用于测试）
@app.post("/collect")
async def manual_collect():
    """手动触发一次数据采集"""
    data = await collector.collect_data()
    if data:
        return {"message": "数据采集成功", "data": data}
    else:
        raise HTTPException(status_code=500, detail="数据采集失败")

# 采集控制接口
@app.post("/start/{group_id}")
async def start_collecting_group(group_id: int):
    """开始指定组数据采集"""
    if collector.start_collecting(group_id):
        return {"message": f"组{group_id}数据采集已开始", "group_id": group_id, "status": "collecting"}
    else:
        return {"message": f"组{group_id}数据采集已在运行中", "group_id": group_id, "status": "already_collecting"}

@app.post("/start")
async def start_collecting_default():
    """开始组1数据采集"""
    return await start_collecting_group(1)

@app.post("/stop/{group_id}")
async def stop_collecting_group(group_id: int):
    """停止指定组数据采集"""
    if collector.stop_collecting(group_id):
        return {"message": f"组{group_id}数据采集已停止", "group_id": group_id, "status": "stopped"}
    else:
        return {"message": f"组{group_id}数据采集未在运行", "group_id": group_id, "status": "already_stopped"}

@app.post("/stop")
async def stop_collecting_default():
    """停止组1数据采集"""
    return await stop_collecting_group(1)

@app.get("/status/{group_id}")
async def get_collecting_status_group(group_id: int):
    """获取指定组采集状态"""
    is_collecting = collector.get_collecting_status(group_id)
    group_data = collector.get_all_data(group_id)
    current_index = collector.current_indexes.get(group_id, 0)
    
    return {
        "group_id": group_id,
        "is_collecting": is_collecting,
        "total_records": len(group_data),
        "current_index": current_index,
        "status": "collecting" if is_collecting else "stopped"
    }

@app.get("/status")
async def get_collecting_status_all():
    """获取所有组采集状态"""
    all_status = collector.get_collecting_status()
    available_groups = collector.get_available_groups()
    
    return {
        "collecting_groups": all_status,
        "available_groups": available_groups,
        "current_indexes": collector.current_indexes
    }

@app.get("/groups")
async def get_available_groups():
    """获取有数据的组列表"""
    groups = collector.get_available_groups()
    group_info = []
    
    for group_id in groups:
        group_data = collector.get_all_data(group_id)
        is_collecting = collector.get_collecting_status(group_id)
        current_index = collector.current_indexes.get(group_id, 0)
        
        group_info.append({
            "group_id": group_id,
            "total_records": len(group_data),
            "current_index": current_index,
            "is_collecting": is_collecting,
            "latest_record": group_data[-1]["timestamp"] if group_data else None
        })
    
    return {
        "available_groups": groups,
        "group_details": group_info
    }

if __name__ == "__main__":
    print("启动数据采集服务...")
    print(f"目标API: {API_URL}")
    print(f"采集间隔: {COLLECT_INTERVAL}秒")
    print("服务将在 http://localhost:8000 启动")
    print("API文档: http://localhost:8000/docs")
    print("\n可用的API接口:")
    print("- POST /start/{group_id} - 开始指定组数据采集")
    print("- POST /stop/{group_id} - 停止指定组数据采集")
    print("- GET /status/{group_id} - 获取指定组采集状态")
    print("- GET /status - 获取所有组采集状态")
    print("- GET /current/{group_id} - 获取指定组当前数据（循环切换）")
    print("- GET /current - 获取组1当前数据（循环切换）")
    print("- GET /all/{group_id} - 获取指定组所有数据")
    print("- GET /all - 获取所有数据")
    print("- GET /groups - 获取有数据的组列表")
    print("- GET /stats - 获取统计信息")
    print("- POST /collect - 手动采集一次数据")
    print("\n使用示例:")
    print("  开始组1采集: curl -X POST http://localhost:8000/start/1")
    print("  获取组1数据: curl http://localhost:8000/current/1")
    print("  停止组1采集: curl -X POST http://localhost:8000/stop/1")
    
    # 启动FastAPI服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
