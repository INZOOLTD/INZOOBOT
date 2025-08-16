from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star
from astrbot.api import logger
import random
import psutil
import datetime
import platform


class SystemStatus(Star):
    """系统状态功能模块"""

    def __init__(self, context):
        super().__init__(context)

    @filter.command("系统状态")
    async def system_status(self, event: AstrMessageEvent):
        '''私聊查询系统状态（仅管理员可用）'''
        # 检查功能是否启用（从全局配置获取）
        if not self.config_manager.global_config.system_status_enabled:
            yield event.plain_result("❌ 系统状态查询功能已被禁用")
            return

        # 检查是否为私聊
        if not event.is_private_chat():
            yield event.plain_result("请在私聊中使用该指令")
            return

        # 检查是否为管理员
        if not event.is_admin():
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
            yield event.plain_result(random.choice(responses))
            return

        # 管理员查询系统状态
        try:
            # 获取系统信息并构建消息
            system = platform.system()
            node = platform.node()
            release = platform.release()
            machine = platform.machine()

            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)

            mem = psutil.virtual_memory()
            mem_usage = mem.percent
            mem_total = round(mem.total / (1024 ** 3), 2)
            mem_available = round(mem.available / (1024 ** 3), 2)

            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_total = round(disk.total / (1024 ** 3), 2)
            disk_free = round(disk.free / (1024 ** 3), 2)

            net_io = psutil.net_io_counters()
            bytes_sent = round(net_io.bytes_sent / (1024 ** 2), 2)
            bytes_recv = round(net_io.bytes_recv / (1024 ** 2), 2)

            boot_time = psutil.boot_time()
            boot_time_str = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
            uptime_seconds = int(datetime.datetime.now().timestamp() - boot_time)
            uptime_str = str(datetime.timedelta(seconds=uptime_seconds))

            users = psutil.users()
            user_count = len(users)

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
            yield event.plain_result(status_msg)
        except Exception as e:
            logger.error(f"获取系统状态失败：{str(e)}")
            yield event.plain_result("❌ 获取系统状态失败，请稍后再试")
