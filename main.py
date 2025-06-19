from apscheduler.schedulers.asyncio import AsyncIOScheduler

from astrbot import logger
from astrbot.api.event import MessageChain, filter, AstrMessageEvent
from astrbot.api.star import register, Star
from AstrBot.astrbot.core.star import Context

from .storage import load_subscriptions, save_subscriptions
from .task import get_report_message_chain


@register(
    "HLTV_Monitor",
    "MO",
    "hltv比赛监控插件",
    "1.1.2",
    "https://github.com/mocchh/hltv_-monitor"
)
class HLTV_Monitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        #从storage模块加载订阅列表
        self.subscribed.chats = load_subscriptions()
        logger.info(f"[HLTV插件] 成功加载 {len(self.subscribed_chats)} 个订阅者。")
        #初始化并配置异步调度器
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

        # 3. 添加每日定时推送任务
        self.scheduler.add_job(
            self.send_scheduled_report,
            'cron',
            hour=8,
            minute=0,
            id="hltv_daily_report_job",
            replace_existing=True
        )

        # 4. 启动调度器
        self.scheduler.start()
        logger.info("[HLTV插件] 每日报告调度器已启动，将在每天早上8点推送。")

        # --- 定时任务的执行逻辑 ---
    async def send_scheduled_report(self):
        """由调度器定时调用，向所有订阅者发送报告。"""
        logger.info(f"[HLTV插件] 开始向 {len(self.subscribed_chats)} 个订阅者发送每日报告...")
        if not self.subscribed_chats:
            logger.info("[HLTV插件] 没有订阅者，本次任务跳过。")
            return

        # 调用 task 模块获取消息内容
        report_message = await get_report_message_chain()

        for origin in self.subscribed_chats:
            try:
                await self.context.send_message(origin, report_message)
                logger.info(f"[HLTV插件] 已成功向 {origin} 发送报告。")
            except Exception as e:
                logger.error(f"[HLTV插件] 向 {origin} 发送报告失败: {e}")
        logger.info("[HLTV插件] 每日HLTV报告全部发送完毕。")

    # --- 用户交互指令 ---
    @filter.command("hltv")
    async def hltv_command(self, event: AstrMessageEvent):
        """处理用户的即时查询请求。"""
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
            # 调用 storage 模块保存订阅列表
            save_subscriptions(self.subscribed_chats)
            logger.info(f"[HLTV插件] 新增订阅者: {umo}")
            await self.context.send_message(umo, MessageChain().message("✅ 订阅成功！从明天早上8点开始，您将收到HLTV每日报告。"))

    @filter.command("取消订阅hltv")
    async def unsubscribe_command(self, event: AstrMessageEvent):
        """处理用户取消订阅每日HLTV报告的请求。"""
        umo = event.unified_msg_origin
        if umo in self.subscribed_chats:
            self.subscribed_chats.remove(umo)
            # 调用 storage 模块保存订阅列表
            save_subscriptions(self.subscribed_chats)
            logger.info(f"[HLTV插件] 订阅者已移除: {umo}")
            await self.context.send_message(umo, MessageChain().message("☑️ 已为您取消订阅HLTV每日报告。"))
        else:
            await self.context.send_message(umo, MessageChain().message("您还没有订阅过HLTV每日报告哦。"))












    @filter.command("hltv")
    async def create_new_schedule(self, event: AstrMessageEvent):
        """
        创建一个新的调度任务来监控 HLTV 比赛
        """
        try:
            logger.info("开始创建新的 HLTV 比赛监控任务...")
            run_scheduler()
            await self.context.send_message(event.unified_msg_origin, MessageChain().message("HLTV 比赛监控任务已启动。"))
            logger.info("HLTV 比赛监控任务已成功启动。")
        except Exception as e:
            logger.error(f"创建 HLTV 比赛监控任务时发生错误: {e}")
            await self.context.send_message(event.unified_msg_origin, MessageChain().message(f"创建 HLTV 比赛监控任务失败: {e}"))

