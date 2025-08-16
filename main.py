from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random
import psutil  # 用于获取系统状态信息

@register("inzoobot", "inzoo", "映筑视觉官方机器人", "1.0.1", "https://github.com/INZOOLTD/INZOOBOT")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("天馁")
    async def helloworld(self, event: AstrMessageEvent):
        '''关键词回复'''
        user_name = event.get_sender_name()
        logger.info("触发hello world指令!")
        yield event.plain_result(f"Hello, {user_name}!")

    @filter.command("系统状态")
    async def system_status(self, event: AstrMessageEvent):
        '''私聊查询系统状态（仅管理员可用）'''
        # 检查是否为私聊
        if not event.is_private_chat():
            yield event.plain_result("请在私聊中使用该指令")
            return

        # 检查是否为管理员（假设is_admin()方法可判断管理员身份）
        if not event.is_admin():
            # 非管理员随机回复
            responses = [
                "切你是谁",    # 50% 概率
                "切你是谁",
                "切你是谁",
                "切你是谁",
                "切你是谁",
                "我不认识你",  # 20% 概率
                "我不认识你",
                "你不是主人",  # 20% 概率
                "你不是主人",
                "滚啊傻逼"      # 10% 概率
            ]
            yield event.plain_result(random.choice(responses))
            return

        # 管理员查询系统状态
        try:
            # 获取CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            # 获取内存信息
            mem = psutil.virtual_memory()
            mem_usage = mem.percent
            # 获取磁盘信息（根分区）
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            # 获取系统启动时间
            boot_time = psutil.boot_time()
            import datetime
            boot_time_str = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")

            status_msg = (
                f"系统状态信息：\n"
                f"CPU使用率：{cpu_usage}%\n"
                f"内存使用率：{mem_usage}%\n"
                f"磁盘使用率：{disk_usage}%\n"
                f"系统启动时间：{boot_time_str}"
            )
            yield event.plain_result(status_msg)
        except Exception as e:
            logger.error(f"获取系统状态失败：{str(e)}")
            yield event.plain_result("获取系统状态失败，请稍后再试")

    async def terminate(self):
        '''插件卸载/停用时调用'''
        pass