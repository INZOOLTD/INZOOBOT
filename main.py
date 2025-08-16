from astrbot.star import Star, register, filter
from astrbot.star.event import MessageEvent, PrivateMessageEvent, GroupMessageEvent
from astrbot.star.context import Context
from astrbot.log import logger
from pathlib import Path
import json
import random
import psutil
import datetime
import platform
from typing import Dict, List, Tuple, Optional
import asyncio

# 配置文件路径
CONFIG_PATH = Path(__file__).parent / "data" / "config.json"
GLOBAL_CONFIG_PATH = Path(__file__).parent / "data" / "global_config.json"

# 确保数据目录存在
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class GroupConfig:
    """单个群组的配置类"""

    def __init__(self):
        self.enabled = False  # 是否启用群管功能
        self.punish_words = []  # 处罚词列表

    def to_dict(self) -> Dict:
        """转换为字典用于序列化"""
        return {
            "enabled": self.enabled,
            "punish_words": self.punish_words
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GroupConfig":
        """从字典创建对象"""
        config = cls()
        config.enabled = data.get("enabled", False)
        config.punish_words = data.get("punish_words", [])
        return config


class PluginConfig:
    """插件全局配置类"""

    def __init__(self):
        self.system_status_enabled = True  # 是否启用系统状态查询功能
        self.group_management_enabled = True  # 是否启用群管功能
        self.default_welcome_message = "欢迎加入本群！"  # 默认入群欢迎消息

    def to_dict(self) -> Dict:
        """转换为字典用于序列化"""
        return {
            "system_status_enabled": self.system_status_enabled,
            "group_management_enabled": self.group_management_enabled,
            "default_welcome_message": self.default_welcome_message
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PluginConfig":
        """从字典创建对象"""
        config = cls()
        config.system_status_enabled = data.get("system_status_enabled", True)
        config.group_management_enabled = data.get("group_management_enabled", True)
        config.default_welcome_message = data.get("default_welcome_message", "欢迎加入本群！")
        return config


class ConfigManager:
    """配置管理类，处理持久化存储"""

    def __init__(self):
        self.group_configs: Dict[str, GroupConfig] = {}  # {群号字符串: GroupConfig对象}
        self.global_config = PluginConfig()  # 全局配置
        self.load_group_configs()
        self.load_global_config()

    def load_global_config(self) -> None:
        """加载全局配置"""
        try:
            if GLOBAL_CONFIG_PATH.exists():
                with open(GLOBAL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.global_config = PluginConfig.from_dict(data)
                logger.info("全局配置加载成功")
        except Exception as e:
            logger.error(f"加载全局配置失败: {str(e)}")
            self.global_config = PluginConfig()

    def save_global_config(self) -> None:
        """保存全局配置"""
        try:
            with open(GLOBAL_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.global_config.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info("全局配置保存成功")
        except Exception as e:
            logger.error(f"保存全局配置失败: {str(e)}")

    def load_group_configs(self) -> None:
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

    def save_group_configs(self) -> None:
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

    def update_group_config(self, group_id: str, config: GroupConfig) -> None:
        """更新指定群组的配置"""
        self.group_configs[group_id] = config
        self.save_group_configs()


@register(
    name="inzoobot",
    display_name="inzoo",
    description="映筑视觉官方机器人",
    version="1.0.0",
    homepage="https://github.com/INZOOLTD/INZOOBOT"
)
class InzoobotPlugin(Star):
    """映筑视觉官方机器人插件"""

    def __init__(self, context: Context):
        super().__init__(context)
        self.config_manager = ConfigManager()
        logger.info("映筑视觉官方机器人插件已初始化")

    # 系统状态功能 - 仅私聊可用
    @filter.command("系统状态", aliases=["sysinfo"], description="查询系统状态信息")
    async def handle_system_status(self, event: MessageEvent):
        """处理系统状态查询命令"""
        # 检查功能是否启用
        if not self.config_manager.global_config.system_status_enabled:
            yield event.response("❌ 系统状态查询功能已被禁用")
            return

        # 检查是否为私聊
        if not isinstance(event, PrivateMessageEvent):
            yield event.response("请在私聊中使用该指令")
            return

        # 检查是否为管理员
        if not event.sender.is_admin:
            # 非管理员随机回复，按指定概率分布
            responses = [
                "切你是谁",  # 50% 概率
                "切你是谁",
                "切你是谁",
                "切你是谁",
                "切你是谁",
                "我不认识你",  # 20% 概率
                "我不认识你",
                "你不是主人",  # 20% 概率
                "你不是主人",
                "123起开"  # 10% 概率
            ]
            yield event.response(random.choice(responses))
            return

        # 管理员查询系统状态
        try:
            # 获取系统信息
            system = platform.system()
            node = platform.node()
            release = platform.release()
            machine = platform.machine()

            # CPU信息
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)

            # 内存信息
            mem = psutil.virtual_memory()
            mem_usage = mem.percent
            mem_total = round(mem.total / (1024 ** 3), 2)
            mem_available = round(mem.available / (1024 ** 3), 2)

            # 磁盘信息
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_total = round(disk.total / (1024 ** 3), 2)
            disk_free = round(disk.free / (1024 ** 3), 2)

            # 网络信息
            net_io = psutil.net_io_counters()
            bytes_sent = round(net_io.bytes_sent / (1024 ** 2), 2)
            bytes_recv = round(net_io.bytes_recv / (1024 ** 2), 2)

            # 系统时间信息
            boot_time = psutil.boot_time()
            boot_time_str = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
            uptime_seconds = int(datetime.datetime.now().timestamp() - boot_time)
            uptime_str = str(datetime.datetime.timedelta(seconds=uptime_seconds))

            # 用户信息
            users = psutil.users()
            user_count = len(users)

            # 构建状态消息
            status_msg = (
                f"📊 系统状态信息：\n\n"
                f"💻 系统信息：{system} {release} ({machine})\n"
                f"🏷️ 主机名：{node}\n\n"
                f"🔋 CPU状态：\n"
                f"  - 使用率：{cpu_usage}%\n"
                f"  - 物理核心：{cpu_count} 核\n"
                f"  - 线程数：{cpu_threads} 线程\n\n"
                f"🧠 内存状态：\n"
                f"  - 使用率：{mem_usage}%\n"
                f"  - 总容量：{mem_total} GB\n"
                f"  - 可用容量：{mem_available} GB\n\n"
                f"💽 磁盘状态 (/)：\n"
                f"  - 使用率：{disk_usage}%\n"
                f"  - 总容量：{disk_total} GB\n"
                f"  - 可用容量：{disk_free} GB\n\n"
                f"📡 网络流量：\n"
                f"  - 已发送：{bytes_sent} MB\n"
                f"  - 已接收：{bytes_recv} MB\n\n"
                f"⏱️ 系统时间：\n"
                f"  - 启动时间：{boot_time_str}\n"
                f"  - 运行时间：{uptime_str}\n\n"
                f"👥 当前用户数：{user_count}"
            )
            yield event.response(status_msg)
        except Exception as e:
            logger.error(f"获取系统状态失败：{str(e)}")
            yield event.response("❌ 获取系统状态失败，请稍后再试")

    # 群管功能辅助方法
    def is_group_management_enabled(self, group_id: str) -> bool:
        """检查指定群是否启用了群管功能"""
        if not self.config_manager.global_config.group_management_enabled:
            return False
        group_config = self.config_manager.get_group_config(group_id)
        return group_config.enabled

    def check_permissions(self, event: MessageEvent, require_group: bool = False) -> Tuple[bool, str]:
        """检查权限"""
        if not self.config_manager.global_config.group_management_enabled:
            return (False, "❌ 群管功能已被全局禁用")

        if not event.sender.is_admin:
            return (False, "❌ 你没有权限执行此操作，需要管理员权限")

        if require_group and not isinstance(event, GroupMessageEvent):
            return (False, "❌ 请在群聊中使用此指令")

        return (True, "")

    # 群管功能指令
    @filter.command("群管帮助", description="显示群管功能帮助信息")
    async def handle_group_management_help(self, event: MessageEvent):
        """处理群管帮助命令"""
        if not self.config_manager.global_config.group_management_enabled:
            yield event.response("❌ 群管功能已被全局禁用")
            return

        help_msg = (
            "📋 群管功能指令：\n"
            "1. 开启群管 - 启用当前群的群管功能\n"
            "2. 关闭群管 - 禁用当前群的群管功能\n"
            "3. 添加处罚词 [词语] - 添加需要处罚的关键词\n"
            "4. 删除处罚词 [词语] - 移除处罚关键词\n"
            "5. 查看处罚词 - 显示当前所有处罚关键词\n"
            "6. 群管状态 - 查看当前群管功能状态\n"
            "\n⚠️ 注意：所有群管指令仅管理员可使用"
        )
        yield event.response(help_msg)

    @filter.command("开启群管", description="开启当前群的群管功能")
    async def handle_enable_group_management(self, event: MessageEvent):
        """处理开启群管命令"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.response(msg)
            return

        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group.id)
            group_config = self.config_manager.get_group_config(group_id)

            if group_config.enabled:
                yield event.response("✅ 群管功能已经是开启状态")
                return

            group_config.enabled = True
            self.config_manager.update_group_config(group_id, group_config)
            yield event.response("✅ 群管功能已开启")
            return

        yield event.response("❌ 此命令只能在群聊中使用")

    @filter.command("关闭群管", description="关闭当前群的群管功能")
    async def handle_disable_group_management(self, event: MessageEvent):
        """处理关闭群管命令"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.response(msg)
            return

        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group.id)
            group_config = self.config_manager.get_group_config(group_id)

            if not group_config.enabled:
                yield event.response("❌ 群管功能已经是关闭状态")
                return

            group_config.enabled = False
            self.config_manager.update_group_config(group_id, group_config)
            yield event.response("❌ 群管功能已关闭")
            return

        yield event.response("❌ 此命令只能在群聊中使用")

    @filter.command("添加处罚词", description="添加需要处罚的关键词")
    async def handle_add_punish_word(self, event: MessageEvent):
        """处理添加处罚词命令"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.response(msg)
            return

        if isinstance(event, GroupMessageEvent):
            # 提取命令参数
            cmd_content = event.message.content.strip()
            parts = cmd_content.split(maxsplit=1)
            if len(parts) < 2:
                yield event.response("❌ 请指定要添加的处罚词，格式：添加处罚词 [词语]")
                return

            word = parts[1].strip()
            if not word:
                yield event.response("❌ 处罚词不能为空")
                return

            group_id = str(event.group.id)
            group_config = self.config_manager.get_group_config(group_id)

            if word in group_config.punish_words:
                yield event.response(f"❌ 处罚词「{word}」已存在")
                return

            group_config.punish_words.append(word)
            self.config_manager.update_group_config(group_id, group_config)
            yield event.response(f"✅ 已添加处罚词：「{word}」")
            return

        yield event.response("❌ 此命令只能在群聊中使用")

    @filter.command("删除处罚词", description="移除处罚关键词")
    async def handle_remove_punish_word(self, event: MessageEvent):
        """处理删除处罚词命令"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.response(msg)
            return

        if isinstance(event, GroupMessageEvent):
            # 提取命令参数
            cmd_content = event.message.content.strip()
            parts = cmd_content.split(maxsplit=1)
            if len(parts) < 2:
                yield event.response("❌ 请指定要删除的处罚词，格式：删除处罚词 [词语]")
                return

            word = parts[1].strip()
            group_id = str(event.group.id)
            group_config = self.config_manager.get_group_config(group_id)

            if word not in group_config.punish_words:
                yield event.response(f"❌ 处罚词「{word}」不存在")
                return

            group_config.punish_words.remove(word)
            self.config_manager.update_group_config(group_id, group_config)
            yield event.response(f"✅ 已删除处罚词：「{word}」")
            return

        yield event.response("❌ 此命令只能在群聊中使用")

    @filter.command("查看处罚词", description="显示当前所有处罚关键词")
    async def handle_list_punish_words(self, event: MessageEvent):
        """处理查看处罚词命令"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.response(msg)
            return

        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group.id)
            group_config = self.config_manager.get_group_config(group_id)

            if not group_config.punish_words:
                yield event.response("📋 当前没有设置处罚词")
                return

            words_list = "\n".join([f"- {word}" for word in group_config.punish_words])
            yield event.response(f"📋 当前处罚词列表：\n{words_list}")
            return

        yield event.response("❌ 此命令只能在群聊中使用")

    @filter.command("群管状态", description="查看当前群管功能状态")
    async def handle_group_management_status(self, event: MessageEvent):
        """处理群管状态查询命令"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.response(msg)
            return

        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group.id)
            group_config = self.config_manager.get_group_config(group_id)
            status = "开启" if group_config.enabled else "关闭"
            word_count = len(group_config.punish_words)

            status_msg = (
                f"📊 群管功能状态：\n"
                f"• 功能状态：{status}\n"
                f"• 处罚词数量：{word_count}个\n"
                f"• 群号：{group_id}"
            )
            yield event.response(status_msg)
            return

        yield event.response("❌ 此命令只能在群聊中使用")

    @filter.all()
    async def handle_message_monitoring(self, event: MessageEvent):
        """监控消息，检查是否包含处罚词"""
        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group.id)
            if not self.is_group_management_enabled(group_id):
                return

            group_config = self.config_manager.get_group_config(group_id)
            punish_words = group_config.punish_words

            if not punish_words:
                return

            content = event.message.content.lower()
            for word in punish_words:
                if word.lower() in content:
                    logger.info(f"检测到处罚词「{word}」，发送者：{event.sender.name}")
                    yield event.response(f"⚠️ 检测到敏感词「{word}」，请注意言行规范！")
                    return

    async def terminate(self):
        """插件卸载/停用时调用"""
        self.config_manager.save_group_configs()
        self.config_manager.save_global_config()
        logger.info("映筑视觉官方机器人插件已停用，配置已保存")


# 机器人启动入口
async def main():
    from astrbot.star import run
    # 运行机器人，加载当前文件中的插件
    await run(plugins=[InzoobotPlugin])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("机器人已手动停止")
    except Exception as e:
        logger.error(f"机器人运行出错: {str(e)}", exc_info=True)
