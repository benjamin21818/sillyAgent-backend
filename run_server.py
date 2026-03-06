import uvicorn
import argparse
import sys
import signal





# 自动和手动结束时
def signal_hander(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_hander)
signal.signal(signal.SIGTERM, signal_hander)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",type=str,default="127.0.0.1",help="host")# 监听地址
    parser.add_argument("--port",type=int,default=8000,help="port")       # 监听端口
    parser.add_argument("--reload",action="store_true",default=True,help="reload")     # 自动重载模块
    parser.add_argument("--log_level",type=str,default="info",choices=["debug", "info", "warning", "error", "critical"], help="Log level (default: info)")
    args = parser.parse_args()
    
    try:
        uvicorn.run("src.backend.app:app", host=args.host, port=args.port, reload=args.reload, log_level=args.log_level)
    except Exception as e:
        print(f"启动服务器失败：{e}")
        sys.exit(1)



