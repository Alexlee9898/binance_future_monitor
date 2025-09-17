#!/usr/bin/env python3
"""
日志管理模块 - 提供结构化日志和日志轮转功能
负责处理所有日志相关的配置和管理
"""

import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Optional, Any
import os
import sys
import pytz
from pythonjsonlogger import jsonlogger

# 时区设置
UTC8 = pytz.timezone('Asia/Shanghai')

def get_utc8_time():
    """获取UTC+8当前时间"""
    return datetime.now(UTC8)

class LoggerManager:
    """日志管理器 - 处理日志配置和轮转"""

    def __init__(self, name: str = "binance_monitor", log_dir: str = "logs",
                 max_bytes: int = 10*1024*1024, backup_count: int = 5,
                 console_level: str = "INFO", file_level: str = "DEBUG"):
        """
        初始化日志管理器

        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
            max_bytes: 每个日志文件的最大字节数（默认10MB）
            backup_count: 保留的日志文件数量
            console_level: 控制台日志级别
            file_level: 文件日志级别
        """
        self.name = name
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_level = getattr(logging, console_level.upper())
        self.file_level = getattr(logging, file_level.upper())

        self._ensure_log_directory()
        self.logger = self._setup_logger()

    def _ensure_log_directory(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            print(f"创建日志目录: {self.log_dir}")

    def _setup_logger(self) -> logging.Logger:
        """设置和配置日志记录器"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)  # 设置最低级别，由处理器控制实际输出

        # 清除现有的处理器，避免重复
        logger.handlers.clear()

        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)

        # 创建文件处理器（带日志轮转）
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.file_level)

        # 错误日志文件处理器
        error_log_file = os.path.join(self.log_dir, f"{self.name}_error.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)

        # 创建JSON格式器
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s %(funcName)s %(lineno)d'
        )

        # 创建人类可读的格式器
        readable_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )

        # 控制台使用人类可读格式
        console_handler.setFormatter(readable_formatter)

        # 文件使用JSON格式（便于程序解析）
        file_handler.setFormatter(json_formatter)
        error_handler.setFormatter(json_formatter)

        # 添加处理器到日志记录器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """获取配置好的日志记录器"""
        return self.logger

    def log_structured(self, level: str, message: str, **kwargs):
        """
        记录结构化日志

        Args:
            level: 日志级别
            message: 消息内容
            **kwargs: 额外的结构化数据
        """
        log_method = getattr(self.logger, level.lower())

        # 创建结构化日志数据
        log_data = {
            'message': message,
            'timestamp': get_utc8_time().isoformat(),
            'extra_data': kwargs
        }

        log_method(json.dumps(log_data, ensure_ascii=False))

    def log_monitor_event(self, event_type: str, symbol: str, data: Dict[str, Any], level: str = "INFO"):
        """
        记录监控事件

        Args:
            event_type: 事件类型（如：data_update, alert_triggered等）
            symbol: 交易对
            data: 事件数据
            level: 日志级别
        """
        log_data = {
            'event_type': event_type,
            'symbol': symbol,
            'data': data,
            'timestamp': get_utc8_time().isoformat()
        }

        self.log_structured(level, f"Monitor event: {event_type}", **log_data)

    def log_error_with_context(self, error_type: str, error_message: str,
                              symbol: Optional[str] = None, context: Optional[Dict] = None):
        """
        记录带上下文的错误

        Args:
            error_type: 错误类型
            error_message: 错误信息
            symbol: 相关交易对
            context: 错误上下文
        """
        error_data = {
            'error_type': error_type,
            'error_message': error_message,
            'symbol': symbol,
            'context': context or {},
            'timestamp': get_utc8_time().isoformat()
        }

        self.log_structured("ERROR", f"Error: {error_type}", **error_data)

    def log_performance_metric(self, metric_name: str, value: float, symbol: Optional[str] = None):
        """
        记录性能指标

        Args:
            metric_name: 指标名称
            value: 指标值
            symbol: 相关交易对
        """
        metric_data = {
            'metric_name': metric_name,
            'value': value,
            'symbol': symbol,
            'timestamp': get_utc8_time().isoformat()
        }

        self.log_structured("DEBUG", f"Performance metric: {metric_name}", **metric_data)

    def log_api_request(self, endpoint: str, symbol: str, response_time: float, status_code: int):
        """
        记录API请求

        Args:
            endpoint: API端点
            symbol: 交易对
            response_time: 响应时间（秒）
            status_code: HTTP状态码
        """
        api_data = {
            'endpoint': endpoint,
            'symbol': symbol,
            'response_time': response_time,
            'status_code': status_code,
            'timestamp': get_utc8_time().isoformat()
        }

        level = "INFO" if status_code == 200 else "WARNING"
        self.log_structured(level, f"API request: {endpoint}", **api_data)

    def log_cleanup_operation(self, operation_type: str, records_deleted: int, duration: float):
        """
        记录清理操作

        Args:
            operation_type: 清理操作类型
            records_deleted: 删除的记录数
            duration: 操作耗时（秒）
        """
        cleanup_data = {
            'operation_type': operation_type,
            'records_deleted': records_deleted,
            'duration_seconds': duration,
            'timestamp': get_utc8_time().isoformat()
        }

        self.log_structured("INFO", f"Cleanup operation: {operation_type}", **cleanup_data)

    def get_log_files_info(self) -> Dict[str, Any]:
        """
        获取日志文件信息

        Returns:
            日志文件信息
        """
        log_files = {}

        try:
            # 主日志文件
            main_log = os.path.join(self.log_dir, f"{self.name}.log")
            if os.path.exists(main_log):
                log_files['main_log'] = {
                    'path': main_log,
                    'size_bytes': os.path.getsize(main_log),
                    'size_mb': round(os.path.getsize(main_log) / (1024 * 1024), 2)
                }

            # 错误日志文件
            error_log = os.path.join(self.log_dir, f"{self.name}_error.log")
            if os.path.exists(error_log):
                log_files['error_log'] = {
                    'path': error_log,
                    'size_bytes': os.path.getsize(error_log),
                    'size_mb': round(os.path.getsize(error_log) / (1024 * 1024), 2)
                }

            # 轮转文件
            rotated_files = []
            for file in os.listdir(self.log_dir):
                if file.startswith(f"{self.name}.log.") or file.startswith(f"{self.name}_error.log."):
                    file_path = os.path.join(self.log_dir, file)
                    rotated_files.append({
                        'filename': file,
                        'size_bytes': os.path.getsize(file_path),
                        'size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                        'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })

            log_files['rotated_files'] = rotated_files
            log_files['total_rotated_files'] = len(rotated_files)

            return log_files

        except Exception as e:
            self.logger.error(f"获取日志文件信息失败: {e}")
            return {}

# 全局日志管理器实例
_logger_manager = None

def get_logger_manager(name: str = "binance_monitor", **kwargs) -> LoggerManager:
    """
    获取全局日志管理器实例

    Args:
        name: 日志记录器名称
        **kwargs: 其他配置参数

    Returns:
        LoggerManager实例
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager(name, **kwargs)
    return _logger_manager

def get_logger(name: str = "binance_monitor", **kwargs) -> logging.Logger:
    """
    获取配置好的日志记录器

    Args:
        name: 日志记录器名称
        **kwargs: 其他配置参数

    Returns:
        logging.Logger实例
    """
    return get_logger_manager(name, **kwargs).get_logger()