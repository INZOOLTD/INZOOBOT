from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star
from astrbot.api import logger


class GroupManagement(Star):
    """群管功能模块"""

    def __init__(self, context):
        super().__init__(context)

    def is_group_management_enabled(self, group_id: str) -> bool:
        """检查指定群是否启用了群管功能"""
        # 先检查全局是否启用群管功能
        if not self.config_manager.global_config.group_management_enabled:
            return False

        group_config = self.config_manager.get_group_config(group_id)
        return group_config.enabled

    def check_permissions(self, event: AstrMessageEvent, require_group: bool = False) -> tuple[bool, str]:
        """检查权限"""
        # 检查全局功能是否启用
        if not self.config_manager.global_config.group_management_enabled:
            return (False, "❌ 群管功能已被全局禁用")

        # 检查是否为管理员
        if not event.is_admin():
            return (False, "❌ 你没有权限执行此操作，需要管理员权限")

        # 检查是否在群聊中（如果需要）
        if require_group and not event.is_group_chat():
            return (False, "❌ 请在群聊中使用此指令")

        return (True, "")

    @filter.command("群管帮助")
    async def group_management_help(self, event: AstrMessageEvent):
        """群管功能帮助菜单"""
        if not self.config_manager.global_config.group_management_enabled:
            yield event.plain_result("❌ 群管功能已被全局禁用")
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
        yield event.plain_result(help_msg)

    @filter.command("开启群管")
    async def enable_group_management(self, event: AstrMessageEvent):
        """开启群管功能"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.plain_result(msg)
            return

        group_id = str(event.get_group_id())
        group_config = self.config_manager.get_group_config(group_id)

        if group_config.enabled:
            yield event.plain_result("✅ 群管功能已经是开启状态")
            return

        group_config.enabled = True
        self.config_manager.update_group_config(group_id, group_config)
        yield event.plain_result("✅ 群管功能已开启")

    @filter.command("关闭群管")
    async def disable_group_management(self, event: AstrMessageEvent):
        """关闭群管功能"""
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.plain_result(msg)
            return

        group_id = str(event.get_group_id())
        group_config = self.config_manager.get_group_config(group_id)

        if not group_config.enabled:
            yield event.plain_result("❌ 群管功能已经是关闭状态")
            return

        group_config.enabled = False
        self.config_manager.update_group_config(group_id, group_config)
        yield event.plain_result("❌ 群管功能已关闭")

    @filter.command("添加处罚词")
    async def add_punish_word(self, event: AstrMessageEvent):
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.plain_result(msg)
            return

        content = event.get_content().strip()
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            yield event.plain_result("❌ 请指定要添加的处罚词，格式：添加处罚词 [词语]")
            return

        word = parts[1].strip()
        if not word:
            yield event.plain_result("❌ 处罚词不能为空")
            return

        group_id = str(event.get_group_id())
        group_config = self.config_manager.get_group_config(group_id)

        if word in group_config.punish_words:
            yield event.plain_result(f"❌ 处罚词「{word}」已存在")
            return

        group_config.punish_words.append(word)
        self.config_manager.update_group_config(group_id, group_config)
        yield event.plain_result(f"✅ 已添加处罚词：「{word}」")

    @filter.command("删除处罚词")
    async def remove_punish_word(self, event: AstrMessageEvent):
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.plain_result(msg)
            return

        content = event.get_content().strip()
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            yield event.plain_result("❌ 请指定要删除的处罚词，格式：删除处罚词 [词语]")
            return

        word = parts[1].strip()
        group_id = str(event.get_group_id())
        group_config = self.config_manager.get_group_config(group_id)

        if word not in group_config.punish_words:
            yield event.plain_result(f"❌ 处罚词「{word}」不存在")
            return

        group_config.punish_words.remove(word)
        self.config_manager.update_group_config(group_id, group_config)
        yield event.plain_result(f"✅ 已删除处罚词：「{word}」")

    @filter.command("查看处罚词")
    async def list_punish_words(self, event: AstrMessageEvent):
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.plain_result(msg)
            return

        group_id = str(event.get_group_id())
        group_config = self.config_manager.get_group_config(group_id)

        if not group_config.punish_words:
            yield event.plain_result("📋 当前没有设置处罚词")
            return

        words_list = "\n".join([f"- {word}" for word in group_config.punish_words])
        yield event.plain_result(f"📋 当前处罚词列表：\n{words_list}")

    @filter.command("群管状态")
    async def group_management_status(self, event: AstrMessageEvent):
        has_perm, msg = self.check_permissions(event, require_group=True)
        if not has_perm:
            yield event.plain_result(msg)
            return

        group_id = str(event.get_group_id())
        group_config = self.config_manager.get_group_config(group_id)
        status = "开启" if group_config.enabled else "关闭"
        word_count = len(group_config.punish_words)

        status_msg = (
            f"📊 群管功能状态：\n"
            f"• 功能状态：{status}\n"
            f"• 处罚词数量：{word_count}个\n"
            f"• 群号：{group_id}"
        )
        yield event.plain_result(status_msg)

    @filter.all()
    async def check_messages(self, event: AstrMessageEvent):
        if not event.is_group_chat():
            return

        group_id = str(event.get_group_id())
        if not self.is_group_management_enabled(group_id):
            return

        group_config = self.config_manager.get_group_config(group_id)
        punish_words = group_config.punish_words

        if not punish_words:
            return

        content = event.get_content().lower()
        for word in punish_words:
            if word.lower() in content:
                logger.info(f"检测到处罚词「{word}」，发送者：{event.get_sender_name()}")
                yield event.plain_result(f"⚠️ 检测到敏感词「{word}」，请注意言行规范！")
                return
