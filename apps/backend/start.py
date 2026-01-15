#!/usr/bin/env python
"""启动脚本 - 启动 FastAPI 和 Celery Worker"""
import sys
import subprocess
import signal
import time
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 进程列表
processes = []


def signal_handler(sig, frame):
    """处理退出信号"""
    print("\n正在停止所有服务...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("所有服务已停止")
    sys.exit(0)


def start_api():
    """启动 FastAPI 服务"""
    print("正在启动 API 服务...")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    proc = subprocess.Popen(cmd, cwd=ROOT_DIR)
    processes.append(proc)
    return proc


def start_worker():
    """启动 Celery Worker"""
    print("正在启动 Celery Worker...")
    cmd = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "api.worker.celery_app",
        "worker",
        "--loglevel=info",
    ]
    proc = subprocess.Popen(cmd, cwd=ROOT_DIR)
    processes.append(proc)
    return proc


def start_beat():
    """启动 Celery Beat (定时任务)"""
    print("正在启动 Celery Beat...")
    cmd = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "api.worker.celery_app",
        "beat",
        "--loglevel=info",
    ]
    proc = subprocess.Popen(cmd, cwd=ROOT_DIR)
    processes.append(proc)
    return proc


def main():
    """主函数"""
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print("SafeSurface Backend - 启动所有服务")
    print("=" * 60)

    # 启动 API
    print("\n[1/3] 正在启动 API 服务...")
    start_api()
    time.sleep(3)

    # 启动 Worker
    print("[2/3] 正在启动 Celery Worker...")
    start_worker()
    time.sleep(2)

    # 启动 Beat
    print("[3/3] 正在启动 Celery Beat...")
    start_beat()

    print("\n" + "=" * 60)
    print("服务已启动")
    print("=" * 60)
    print("\nAPI 文档:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止所有服务")
    print("=" * 60 + "\n")

    # 等待进程
    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()
