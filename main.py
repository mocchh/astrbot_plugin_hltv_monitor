import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 导入 AstrBot 相关的库
from astrbot.api.event import MessageChain, filter, AstrMessageEvent
from astrbot.api.star import register, Star
from AstrBot.astrbot.core.star import Context

# 从我们拆分出的模块中导入功能
# 假设 storage.py 和 task.py 与此文件在同一目录下
from .storage import load_subscriptions, save_subscriptions
from .task import get_report_message_chain

logger = logging.getLogger(__name__)


@register(
    "HLTV_Monitor_Fixed",
    "HMF",
    "修正后的HLTV比赛监控插件",
    "3.1.0",
    "https://github.com/mocchh/hltv_-monitor"
)
class HLTV_Monitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 修正问题1：使用正确的属性名 self.subscribed_chats
        self.subscribed_chats = load_subscriptions()
        logger.info(f"[HLTV插件] 成功加载 {len(self.subscribed_chats)} 个订阅者。")

        # 解决方案3：在这里初始化并启动调度器，而不是通过命令
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.scheduler.add_job(
            self.send_scheduled_report,
            'cron',
            hour=8,
            minute=0,
            id="hltv_daily_report_job",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("[HLTV插件] 每日报告调度器已启动，将在每天早上8点推送。")

    # --- 定时任务的执行逻辑 ---
    # 解决方案2：确保此函数是类的方法，这样 self 才是正确的对象
    async def send_scheduled_report(self):
        """由调度器定时调用，向所有订阅者发送报告。"""
        logger.info(f"[HLTV插件] 开始向 {len(self.subscribed_chats)} 个订阅者发送每日报告...")
        if not self.subscribed_chats:
            logger.info("[HLTV插件] 没有订阅者，本次任务跳过。")
            return

        report_message = await get_report_message_chain()

        for origin in self.subscribed_chats:
            try:
                # 正确使用 self.context
                await self.context.send_message(origin, report_message)
                logger.info(f"[HLTV插件] 已成功向 {origin} 发送报告。")
            except Exception as e:
                logger.error(f"[HLTV插件] 向 {origin} 发送报告失败: {e}")
        logger.info("[HLTV插件] 每日HLTV报告全部发送完毕。")

    # --- 用户交互指令 ---
    # 解决方案2：确保所有命令处理函数都是类的方法（注意缩进）
    @filter.command("hltv")
    async def hltv_command(self, event: AstrMessageEvent):
        """处理用户的即时查询请求。"""
        # 正确使用 self.context
        await self.context.send_message(event.unified_msg_origin, MessageChain().message("正在为您生成最新的HLTV比赛信息，请稍候..."))
        report_message = await get_report_message_chain()
        await self.context.send_message(event.unified_msg_origin, report_message)

    @filter.command("订阅hltv")
    async def subscribe_command(self, event: AstrMessageEvent):
        """处理用户订阅每日HLTV报告的请求。"""
        umo = event.unified_msg_origin
        if umo in self.subscribed_chats:
            await self.context.send_message(umo, MessageChain().message("您已经订阅过HLTV每日报告啦！"))
        else:
            self.subscribed_chats.add(umo)
            save_subscriptions(self.subscribed_chats)
            logger.info(f"[HLTV插件] 新增订阅者: {umo}")
            await self.context.send_message(umo, MessageChain().message("✅ 订阅成功！从明天早上8点开始，您将收到HLTV每日报告。"))

    @filter.command("取消订阅hltv")
    async def unsubscribe_command(self, event: AstrMessageEvent):
        """处理用户取消订阅每日HLTV报告的请求。"""
        umo = event.unified_msg_origin
        if umo in self.subscribed_chats:
            self.subscribed_chats.remove(umo)
            save_subscriptions(self.subscribed_chats)
            logger.info(f"[HLTV插件] 订阅者已移除: {umo}")
            await self.context.send_message(umo, MessageChain().message("☑️ 已为您取消订阅HLTV每日报告。"))
        else:
            await self.context.send_message(umo, MessageChain().message("您还没有订阅过HLTV每日报告哦。"))
