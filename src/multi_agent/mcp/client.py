import asyncio
import logging
from typing import Any, Dict, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient  

logger = logging.getLogger(__name__)




class MCPClientManager:
    """
    管理多个MCP客户端的类。

    该类负责根据配置创建和管理多个MCP客户端实例。它使用异步锁确保在多线程环境中安全地创建客户端。

    属性:
        mcp_configs (Dict[str, Any]): MCP客户端的连接配置。
        _client (Optional[object]): 已创建的MCP客户端实例。
        _client_lock (asyncio.Lock): 用于同步客户端创建的异步锁。
    """

    def __init__(self, mcp_configs: Dict[str, Any]):
        self.mcp_configs = mcp_configs or {}
        self._client = None
        self._client_lock = asyncio.Lock()




    async def get_or_create_client(self) -> Optional[object]:
        """
        获取或创建一个MCP客户端实例。

        该方法使用异步锁确保在多线程环境中安全地创建客户端。如果客户端不存在，则根据配置创建一个新实例。

        返回:
            Optional[object]: 已创建的MCP客户端实例，或None（如果配置为空）。
        """
        async with self._client_lock:

            if self._client is not None:
                return self._client

            if not self.mcp_configs:
                logger.error("没有提供MCP配置。。。")
                return None

            try:
                self._client = MultiServerMCPClient(self.mcp_configs)
                return self._client

            except Exception as e:
                logger.error(f"创建MCP客户端实例时出错：{e}")
                return None
            


    async def close_client(self):
        """
        正确关闭 MCP 客户端并清理资源。
        """
        async with self._client_lock:
            if self._client is not None:
                try:
                    # 由于 MultiServerMCPClient 在 langchain-mcp-adapters 0.1.0 中
                    # 不支持上下文管理器或显式的 close 方法，
                    # 我们只需清除引用并让垃圾回收处理它
                    logger.debug("释放 MCP 客户端引用")
                except Exception as e:
                    logger.error(f"MCP 客户端清理期间出错: {e}")
                finally:
                    # 始终清除引用
                    self._client = None



    async def get_all_tools(self) -> list:
        """
        获取 MCP 服务器提供的所有可用工具。
        
        返回:
            List: 所有可用的 MCP 工具列表
        """
        client = await self.get_or_create_client()
        if not client:
            return []
            
        try:
            all_tools = await client.get_tools()
            
            if all_tools:
                logger.info(f"从 MCP 服务器加载了 {len(all_tools)} 个工具")
                return all_tools
            else:
                logger.warning("MCP 服务器没有提供可用工具")
                return []
                
        except Exception as e:
            logger.error(f"获取 MCP 工具时出错: {e}")
            return []                     

