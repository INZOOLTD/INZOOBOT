from pathlib import Path
import json
from astrbot.api import logger

# 配置文件路径
CONFIG_PATH = Path(__file__).parent / "data" / "config.json"

# 确保数据目录存在
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class GroupConfig:
    """单个群组的配置模型"""

    def __init__(self):
        self.enabled = False  # 是否启用群管功能
        self.punish_words = []  # 处罚词列表

    def to_dict(self):
        """转换为字典用于序列化"""
        return {
            "enabled": self.enabled,
            "punish_words": self.punish_words
        }

    @staticmethod
    def from_dict(data):
        """从字典创建对象"""
        config = GroupConfig()
        config.enabled = data.get("enabled", False)
        config.punish_words = data.get("punish_words", [])
        return config


class PluginConfig:
    """插件全局配置"""

    def __init__(self):
        self.system_status_enabled = True  # 是否启用系统状态查询功能
        self.group_management_enabled = True  # 是否启用群管功能
        self.default_welcome_message = "欢迎加入本群！"  # 默认入群欢迎消息


class ConfigManager:
    """配置管理类，处理持久化存储"""

    def __init__(self):
        self.group_configs = {}  # {群号字符串: 群配置}
        self.global_config = PluginConfig()  # 全局配置
        self.load_group_configs()

    def load_group_configs(self):
        """从文件加载群组配置"""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 转换为GroupConfig对象
                for group_id, config_data in data.items():
                    self.group_configs[group_id] = GroupConfig.from_dict(config_data)

                logger.info(f"已加载 {len(self.group_configs)} 个群组的配置")
        except Exception as e:
            logger.error(f"加载群组配置失败: {str(e)}")
            self.group_configs = {}

    def save_group_configs(self):
        """保存群组配置到文件"""
        try:
            # 转换为可序列化的字典
            data = {
                group_id: config.to_dict()
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
