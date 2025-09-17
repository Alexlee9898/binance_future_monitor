# 增强版Binance永续合约监控系统

## 🚀 功能特性

### 核心功能
- **SQLite数据库**: 高性能数据存储，支持历史数据查询和统计
- **日志轮转**: 自动日志文件管理，防止磁盘空间耗尽
- **自动清理**: 定期清理过期数据，保持系统性能
- **结构化日志**: JSON格式日志，便于程序解析和分析
- **多级警报**: 支持低、中、高、紧急四个警报级别
- **性能监控**: 实时监控API响应时间和系统性能

### 增强功能
- **批量API**: 优化的批量数据获取，减少API调用次数
- **速率限制**: 智能API速率限制，避免触发Binance限制
- **错误处理**: 完善的错误处理和重试机制
- **配置管理**: 灵活的环境变量配置
- **命令行工具**: 丰富的命令行参数支持
- **数据库优化**: 自动数据库性能优化

## 📦 安装依赖

```bash
# 安装Python依赖
pip install requests
pip install python-json-logger

# 可选依赖（用于WebSocket支持）
pip install websocket-client
```

## ⚙️ 配置环境变量

### 必需配置
```bash
# Telegram推送配置（可选）
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 数据库路径（可选）
export DATABASE_PATH="data/binance_monitor.db"

# 日志目录（可选）
export LOG_DIR="logs"
```

### 可选配置
```bash
# 监控阈值
export OI_CHANGE_THRESHOLD=0.08      # 持仓量变化阈值（8%）
export PRICE_CHANGE_THRESHOLD=0.02   # 价格变化阈值（2%）
export MONITOR_INTERVAL_MINUTES=15   # 监控间隔（分钟）

# 数据保留
export DATA_RETENTION_DAYS=30        # 监控数据保留天数
export ALERT_RETENTION_DAYS=90       # 警报记录保留天数

# 性能配置
export MAX_REQUESTS_PER_MINUTE=1200  # API请求限制
export BATCH_API_ENABLED=true        # 启用批量API

# 警报级别
export ALERT_LEVEL_LOW_THRESHOLD=0.08      # 低级警报阈值
export ALERT_LEVEL_MEDIUM_THRESHOLD=0.10   # 中级警报阈值
export ALERT_LEVEL_HIGH_THRESHOLD=0.12     # 高级警报阈值
export ALERT_LEVEL_CRITICAL_THRESHOLD=0.15 # 紧急警报阈值
```

## 🚀 快速开始

### 1. 基础运行
```bash
# 使用默认配置运行
python start_enhanced_monitor.py

# 自定义监控间隔
python start_enhanced_monitor.py --interval 10

# 自定义阈值
python start_enhanced_monitor.py --oi-threshold 0.1 --price-threshold 0.05
```

### 2. 数据库管理
```bash
# 查看数据库统计
python start_enhanced_monitor.py --db-stats

# 执行数据清理
python start_enhanced_monitor.py --cleanup

# 优化数据库性能
python start_enhanced_monitor.py --optimize-db
```

### 3. 测试和调试
```bash
# 测试警报功能
python start_enhanced_monitor.py --test-alert

# 试运行模式（不发送实际警报）
python start_enhanced_monitor.py --dry-run

# 调试模式
python start_enhanced_monitor.py --log-level DEBUG
```

## 📊 数据库结构

### 主要数据表

#### 1. oi_history - 持仓量历史数据
```sql
CREATE TABLE oi_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 交易对符号
    timestamp DATETIME NOT NULL,       -- 数据时间戳
    open_interest REAL NOT NULL,       -- 持仓量
    price REAL NOT NULL,               -- 当前价格
    value_usdt REAL,                   -- USDT价值
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. alerts - 警报记录
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 交易对符号
    oi_change_percent REAL NOT NULL,   -- 持仓量变化百分比
    price_change_percent REAL NOT NULL,-- 价格变化百分比
    current_oi REAL NOT NULL,          -- 当前持仓量
    old_oi REAL NOT NULL,              -- 历史持仓量
    current_price REAL NOT NULL,       -- 当前价格
    old_price REAL NOT NULL,           -- 历史价格
    total_value_usdt REAL,             -- 总价值
    alert_time DATETIME NOT NULL,      -- 警报时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. error_logs - 错误日志
```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,          -- 错误类型
    error_message TEXT NOT NULL,       -- 错误信息
    symbol TEXT,                       -- 相关交易对
    context TEXT,                      -- 错误上下文
    error_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. performance_metrics - 性能指标
```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,         -- 指标名称
    metric_value REAL NOT NULL,        -- 指标值
    symbol TEXT,                       -- 相关交易对
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. system_status - 系统状态
```sql
CREATE TABLE system_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_start_time DATETIME NOT NULL,    -- 监控开始时间
    last_monitor_time DATETIME,              -- 最后监控时间
    total_symbols_monitored INTEGER DEFAULT 0, -- 监控的交易对数量
    total_alerts_sent INTEGER DEFAULT 0,     -- 发送的警报数量
    status TEXT DEFAULT 'running',           -- 系统状态
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 📈 性能优化

### 数据库优化
- **WAL模式**: 启用Write-Ahead Logging提高并发性能
- **索引优化**: 自动创建复合索引提高查询速度
- **定期清理**: 自动清理过期数据释放磁盘空间
- **VACUUM**: 定期压缩数据库文件

### API优化
- **批量请求**: 一次性获取所有交易对价格数据
- **智能缓存**: 减少重复API调用
- **速率限制**: 动态调整请求频率避免触发限制
- **连接池**: 复用数据库连接减少开销

### 内存优化
- **数据流处理**: 逐条处理数据避免内存堆积
- **定期清理**: 自动清理内存中的缓存数据
- **对象池**: 复用对象减少垃圾回收压力

## 🛠️ 命令行参数

### 基本参数
```bash
--interval, -i              监控间隔时间（分钟，默认：15）
--oi-threshold, -o          持仓量变化阈值（默认：0.08 = 8%）
--price-threshold, -p       价格变化阈值（默认：0.02 = 2%）
```

### 数据保留参数
```bash
--data-retention-days       监控数据保留天数（默认：30）
--alert-retention-days      警报记录保留天数（默认：90）
--cleanup-interval-hours    数据清理间隔时间（小时，默认：24）
```

### 数据库操作
```bash
--db-stats                  显示数据库统计信息
--cleanup                   执行数据清理操作
--optimize-db               优化数据库性能
--db-path                   数据库文件路径
```

### 日志配置
```bash
--log-dir                   日志文件目录
--log-level                 日志级别（DEBUG, INFO, WARNING, ERROR）
--max-log-size              单个日志文件最大大小（MB）
--log-backup-count          日志文件备份数量
```

### 监控选项
```bash
--telegram-enabled          启用Telegram推送
--no-telegram               禁用Telegram推送
--max-requests-per-minute   每分钟最大API请求数
```

### 其他选项
```bash
--dry-run                   试运行模式（不发送实际警报）
--test-alert                测试警报功能
--version                   显示版本信息
```

## 🔧 系统架构

### 模块结构
```
binance_monitor/
├── database_manager.py      # 数据库管理模块
├── logger_manager.py        # 日志管理模块
├── enhanced_monitor.py      # 增强版监控器
├── config_enhanced.py       # 配置文件
├── start_enhanced_monitor.py # 启动脚本
└── README_ENHANCED.md       # 使用说明
```

### 数据流
```
Binance API → 数据获取 → 变化率计算 → 警报判断 → 数据存储 → 通知发送
     ↓           ↓           ↓           ↓           ↓           ↓
  原始数据    清洗数据    计算结果    警报记录    历史数据    Telegram
```

### 性能指标
- **API响应时间**: 平均 < 200ms
- **数据库查询**: 平均 < 50ms
- **内存使用**: < 500MB
- **CPU使用**: < 10%
- **磁盘I/O**: 优化后的WAL模式

## 🚨 故障排除

### 常见问题

#### 1. 数据库锁定错误
```bash
# 解决方案：执行数据库优化
python start_enhanced_monitor.py --optimize-db
```

#### 2. Telegram推送失败
```bash
# 检查配置
python start_enhanced_monitor.py --test-alert

# 验证环境变量
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

#### 3. API速率限制
```bash
# 降低请求频率
export MAX_REQUESTS_PER_MINUTE=600

# 或增加监控间隔
python start_enhanced_monitor.py --interval 30
```

#### 4. 内存使用过高
```bash
# 减少数据保留时间
export DATA_RETENTION_DAYS=7

# 增加清理频率
export CLEANUP_INTERVAL_HOURS=6
```

### 日志分析
```bash
# 查看实时日志
tail -f logs/binance_monitor.log

# 查看错误日志
tail -f logs/binance_monitor_error.log

# 搜索特定错误
grep "ERROR" logs/binance_monitor.log
```

## 📊 监控指标

### 业务指标
- **监控的交易对数量**: 所有Binance永续合约
- **平均监控间隔**: 15分钟
- **警报触发率**: 根据市场波动变化
- **数据存储量**: 约100MB/月（取决于市场活跃度）

### 技术指标
- **API成功率**: > 99%
- **数据库查询成功率**: > 99.9%
- **系统可用性**: > 99.5%
- **平均响应时间**: < 200ms

## 🔐 安全考虑

### 数据安全
- **本地存储**: 所有数据存储在本地SQLite数据库
- **无敏感信息**: 不存储API密钥等敏感信息
- **数据加密**: 支持数据库级加密（可选）

### 网络安全
- **HTTPS**: 所有API请求使用HTTPS
- **证书验证**: 验证Binance API证书
- **超时控制**: 防止网络请求挂起

### 系统安全
- **权限控制**: 文件系统权限控制
- **输入验证**: 所有输入参数验证
- **错误处理**: 完善的错误处理机制

## 🤝 贡献指南

### 开发环境
```bash
# 克隆项目
git clone https://github.com/your-repo/binance-monitor-enhanced.git

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/
```

### 代码规范
- 遵循PEP 8编码规范
- 使用类型提示
- 添加单元测试
- 编写文档字符串

### 提交规范
- 使用有意义的提交信息
- 关联相关Issue
- 添加变更说明

## 📄 许可证

本项目采用MIT许可证 - 详见LICENSE文件

## 🆘 支持

如有问题，请：
1. 查看本README文档
2. 检查日志文件
3. 提交Issue到GitHub
4. 联系维护者

## 🔄 更新日志

### v2.0.0 (当前版本)
- ✨ 新增SQLite数据库支持
- ✨ 新增日志轮转功能
- ✨ 新增自动数据清理
- ✨ 新增结构化日志
- ✨ 新增多级警报系统
- ✨ 新增性能监控
- ✨ 新增命令行工具
- 🚀 优化API调用性能
- 🚀 优化数据库查询性能
- 🔧 改进错误处理机制

### v1.0.0
- 🎉 初始版本发布
- ✨ 基础监控功能
- ✨ Telegram推送支持
- ✨ JSON数据存储
- ✨ WebSocket支持