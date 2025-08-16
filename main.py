from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import socket
import platform
import os


@register(
    plugin_id="yingzhu-helper",
    author="YourName",
    name="INZOOBOT",
    version="1.0.0",
    repo_url="https://your-repo-url.com"
)
class YingZhuHelper(Star):
    """映筑文化小助手插件，用于响应菜单指令并返回系统信息"""

    def __init__(self, context: Context):
        """
        插件初始化方法

        Args:
            context: AstrBot上下文对象，包含大多数组件
        """
        super().__init__(context)
        # 从注册信息中获取版本号
        self.version = self.metadata.version

    async def initialize(self):
        """插件初始化方法，插件加载时调用"""
        logger.info("映筑文化小助手插件已初始化")

    @filter.message(keywords="菜单")
    async def handle_menu_request(self, event: AstrMessageEvent):
        """
        处理菜单请求的函数

        当用户发送包含"菜单"关键词的消息时触发，
        回复包含版本、服务器IP(打码)和系统状态的信息

        Args:
            event: 消息事件对象，包含消息相关信息
        """
        try:
            # 获取服务器IP并进行打码处理
            server_ip = self._get_server_ip()
            masked_ip = self._mask_ip(server_ip)

            # 获取系统状态信息
            system_status = self._get_system_status()

            # 构建回复消息
            reply = (
                f"你好，我是映筑文化小助手，目前正在测试中\n"
                f"版本：{self.version}\n"
                f"服务器IP：{masked_ip}\n"
                f"系统状态：{system_status}"
            )

            logger.info(f"处理菜单请求，回复系统信息")
            yield event.plain_result(reply)

        except Exception as e:
            # 错误处理，确保插件不会崩溃
            logger.error(f"处理菜单请求时发生错误: {str(e)}")
            yield event.plain_result("抱歉，处理您的请求时发生错误")

    def _get_server_ip(self):
        """
        获取服务器IP地址

        Returns:
            str: 服务器IP地址，获取失败则返回"未知"
        """
        try:
            # 创建临时socket连接以获取本机IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 连接到公共DNS服务器以确定出口IP
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            logger.error(f"获取服务器IP失败: {str(e)}")
            return "未知"

    def _mask_ip(self, ip_address):
        """
        对IP地址进行打码处理，保护服务器安全

        Args:
            ip_address: 原始IP地址

        Returns:
            str: 打码后的IP地址
        """
        if not ip_address or ip_address == "未知":
            return ip_address

        # 分割IP地址为四段
        parts = ip_address.split('.')
        if len(parts) == 4:
            # 保留前两段，后两段打码，例如 192.168.xxx.xxx
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return ip_address

    def _get_system_status(self):
        """
        获取系统状态信息

        Returns:
            str: 系统状态描述
        """
        try:
            # 获取系统类型和版本
            system = platform.system() or "未知"
            release = platform.release() or "未知"

            # 获取Python版本
            python_version = platform.python_version() or "未知"

            # 获取CPU核心数
            cpu_count = os.cpu_count() or "未知"

            return (f"正常运行中 | 系统: {system} {release} | "
                    f"Python: {python_version} | CPU核心: {cpu_count}")
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return "正常运行中"

    async def terminate(self):
        """插件卸载/停用时的清理方法"""
        logger.info("映筑文化小助手插件已停用")
