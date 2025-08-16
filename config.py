from astrbot.api.config import BaseModel, Field, register_config
from pathlib import Path
import json
from astrbot.api import logger

# 配置文件路径
CONFIG_PATH = Path(__file__).parent / "data" / "config.json"

# 确保数据目录存在
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class GroupConfig(BaseModel):
    """单个群组的配置模型"""
    enabled: bool = Field(default=False, description="是否启用群管功能")
    punish_words: list[str] = Field(default_factory=list, description="处罚词列表")


class PluginConfig(BaseModel):
    """插件全局配置模型，用于AstrBot后台配置界面"""
    system_status_enabled: bool = Field(default=True, description="是否启用系统状态查询功能")
    group_management_enabled: bool = Field(default=True, description="是否启用群管功能")
    default_welcome_message: str = Field(default="欢迎加入本群！", description="默认入群欢迎消息")


# 注册配置到AstrBot后台
register_config(
    "inzoobot_combined",
    PluginConfig,
    "映筑视觉机器人配置",
    description="配置系统状态查询和群管功能的相关参数"
)


class ConfigManager:
    """配置管理类，处理持久化存储"""

    def __init__(self):
        self.group_configs: dict[str, GroupConfig] = {}  # {群号字符串: 群配置}
        self.load_group_configs()

    def load_group_configs(self):
        """从文件加载群组配置"""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 转换为GroupConfig对象
                for group_id, config_data in data.items():
                    self.group_configs[group_id] = GroupConfig(**config_data)

                logger.info(f"已加载 {len(self.group_configs)} 个群组的配置")
        except Exception as e:
            logger.error(f"加载群组配置失败: {str(e)}")
            self.group_configs = {}

    def save_group_configs(self):
        """保存群组配置到文件"""
        try:
            # 转换为可序列化的字典
            data = {
                group_id: config.dict()
                for group_id, config in self.group_configs.items()
            }

            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"已保存 {len(self.group_configs)} 个群组的配置")
        except Exception as e:
            logger.error(f"保存群组配置失败: {str(e)}")

    def get_group_config(self, group_id: str) -> GroupConfig:
        """获取指定群组的配置，不存在则创建默认配置"""
        if group_id not in self.group_configs:
            self.group_configs[group_id] = GroupConfig()
            self.save_group_configs()
        return self.group_configs[group_id]

    def update_group_config(self, group_id: str, config: GroupConfig):
        """更新指定群组的配置"""
        self.group_configs[group_id] = config
        self.save_group_configs()
