from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import socket
import platform
import os


# 确保注册信息完整且格式正确，这是平台识别插件的关键
@register(
    plugin_id="inzoobot",
    author="INZOO",
    name="映筑文化小助手",  # 确保name字段存在且不为空
    version="v1.0beat",
    repo_url="https://github.com/INZOOLTD/INZOOBOT"
)
class YingZhuHelper(Star):
    """映筑文化小助手插件，用于响应菜单指令并返回系统信息"""

    def __init__(self, context: Context):
        super().__init__(context)
        # 从元数据中获取名称和版本，避免直接使用可能为空的属性
        self.plugin_name = self.metadata.name
        self.version = self.metadata.version

    async def initialize(self):
        """插件初始化方法"""
        logger.info(f"{self.plugin_name} 插件已初始化，版本: {self.version}")

    @filter.message(keywords="菜单")
    async def handle_menu_request(self, event: AstrMessageEvent):
        """处理菜单请求"""
        try:
            # 安全获取发送者信息，增加多重判断
            sender = event.sender
            user_name = "用户"
            if sender is not None:
                user_name = getattr(sender, 'name', "用户")

            server_ip = self._get_server_ip()
            masked_ip = self._mask_ip(server_ip)
            system_status = self._get_system_status()

            reply = (
                f"你好{user_name}，我是{self.plugin_name}，目前正在测试中\n"
                f"版本：{self.version}\n"
                f"服务器IP：{masked_ip}\n"
                f"系统状态：{system_status}"
            )

            logger.info(f"{self.plugin_name} 处理菜单请求")
            yield event.plain_result(reply)

        except Exception as e:
            logger.error(f"处理菜单请求时发生错误: {str(e)}")
            yield event.plain_result("抱歉，处理您的请求时发生错误")

    def _get_server_ip(self):
        """获取服务器IP地址"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            logger.error(f"获取服务器IP失败: {str(e)}")
            return "未知"

    def _mask_ip(self, ip_address):
        """对IP地址进行打码处理"""
        if not ip_address or ip_address == "未知":
            return ip_address

        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return ip_address

    def _get_system_status(self):
        """获取系统状态信息"""
        try:
            system = platform.system() or "未知"
            release = platform.release() or "未知"
            python_version = platform.python_version() or "未知"
            cpu_count = os.cpu_count() or "未知"

            return (f"正常运行中 | 系统: {system} {release} | "
                    f"Python: {python_version} | CPU核心: {cpu_count}")
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return "正常运行中"

    async def terminate(self):
        """插件卸载/停用时的清理方法"""
        logger.info(f"{self.plugin_name} 插件已停用")
