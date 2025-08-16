from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import socket
import platform
import os


@register("yingzhu_helper", "YourName", "映筑文化小助手插件", "1.0.0")
class YingZhuHelper(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 插件版本号
        self.version = "1.0.0"

    async def initialize(self):
        """初始化插件"""
        logger.info("映筑文化小助手插件已初始化")

    @filter.message(keywords="菜单")
    async def handle_menu(self, event: AstrMessageEvent):
        """处理菜单消息，返回系统信息"""
        try:
            # 获取服务器IP并打码处理
            server_ip = self.get_server_ip()
            masked_ip = self.mask_ip(server_ip)

            # 获取系统状态
            system_status = self.get_system_status()

            # 构建回复消息
            reply = (
                f"你好，我是映筑文化小助手，目前正在测试中\n"
                f"版本：{self.version}\n"
                f"服务器IP：{masked_ip}\n"
                f"系统状态：{system_status}"
            )

            yield event.plain_result(reply)
        except Exception as e:
            logger.error(f"处理菜单请求时出错: {str(e)}")
            yield event.plain_result("抱歉，处理请求时发生错误")

    def get_server_ip(self):
        """获取服务器IP地址"""
        try:
            # 创建一个临时socket连接来获取本机IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            logger.error(f"获取服务器IP失败: {str(e)}")
            return "未知"

    def mask_ip(self, ip):
        """对IP地址进行打码处理，保留前两段，隐藏后两段"""
        if not ip or ip == "未知":
            return ip

        parts = ip.split('.')
        if len(parts) == 4:
            # 例如：192.168.xxx.xxx
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return ip

    def get_system_status(self):
        """获取系统状态信息"""
        try:
            # 获取系统类型
            system = platform.system()
            # 获取系统版本
            release = platform.release()
            # 获取Python版本
            python_version = platform.python_version()

            return f"运行中 | 系统: {system} {release} | Python: {python_version}"
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return "正常运行中"

    async def terminate(self):
        """销毁插件"""
        logger.info("映筑文化小助手插件已停用")
