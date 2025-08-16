from astrbot.api.star import register
from .system_status import SystemStatus
from .group_management import GroupManagement
from .config import ConfigManager


# 统一注册为一个插件
@register(
    "inzoobot_combined",
    "inzoobot",
    "系统状态与群管综合插件",
    "1.0.0",
    "https://github.com/INZOOLTD/INZOOBOT"
)
class InzoobotPlugin(SystemStatus, GroupManagement):
    """综合插件类，继承所有功能模块"""

    def __init__(self, context):
        super().__init__(context)
        # 初始化配置管理器，供所有功能模块使用
        self.config_manager = ConfigManager()

    async def terminate(self):
        """插件卸载/停用时调用"""
        # 保存配置
        self.config_manager.save_group_configs()
        await super().terminate()
