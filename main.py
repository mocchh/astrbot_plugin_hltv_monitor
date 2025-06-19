from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from astrbot.api import logger
from astrbot.api.event import MessageChain, filter, AstrMessageEvent
from astrbot.api.star import register, Star
from AstrBot.astrbot.core.star import Context

from .storage import load_subscriptions, save_subscriptions, load_schedule_time, save_schedule_time
from .task import get_report_message_chain


@register(
    "HLTV_Monitor",
    "MO",
    "HLTV比赛监控插件",
    "1.1.0",
    "https://github.com/mocchh/hltv_-monitor"
)
class HLTV_Monitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.subscribed_chats = load_subscriptions()
        logger.info(f"[HLTV插件] 成功加载 {len(self.subscribed_chats)} 个订阅者。")

        # 初始化调度器 设置时区
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        #从文件内加载定时时间
        schedule_time = load_schedule_time()
        hour = schedule_time.get('hour', 8)
        minute = schedule_time.get('minute', 0)

        self.scheduler.add_job(
            self.send_scheduled_report,
            'cron',
            hour=hour,
            minute=minute,
            id="hltv_daily_report_job",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"[HLTV插件] 每日报告调度器已启动，将在每天 {hour:02d}:{minute:02d} 推送。")

    async def send_scheduled_report(self):
        """由调度器定时调用，向所有订阅者发送报告。"""
        logger.info(f"[HLTV插件] 开始向 {len(self.subscribed_chats)} 个订阅者发送每日报告...")
        if not self.subscribed_chats:
            logger.info("[HLTV插件] 没有订阅者，本次任务跳过。")
            return

        report_message = await get_report_message_chain()

        for origin in self.subscribed_chats:
            try:
                await self.context.send_message(origin, report_message)
                logger.info(f"[HLTV插件] 已成功向 {origin} 发送报告。")
            except Exception as e:
                logger.error(f"[HLTV插件] 向 {origin} 发送报告失败: {e}")
        logger.info("[HLTV插件] 每日HLTV报告全部发送完毕。")

    @filter.command("hltv")
    async def hltv_command(self, event: AstrMessageEvent):
        """处理用户的即时查询请求。"""
        yield event.image_result("./matches.png")

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
            await self.context.send_message(umo, MessageChain().message("✅ 订阅成功"))

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

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command_group("sub")
    def sub(self):
        pass
    @sub.command("change")
    async def change_sub_time(self, event: AstrMessageEvent,h: int, m: int):
        """处理用户更改订阅发送时间的请求。"""
        try:
            # 直接修改任务和保存配置
            self.scheduler.reschedule_job("hltv_daily_report_job", trigger='cron', hour=h, minute=m)
            save_schedule_time({'hour': h, 'minute': m})

            # 发送成功反馈
            logger.info(f"定时推送时间已修改为 {h:02d}:{m:02d}")
            await self.context.send_message(
                event.unified_msg_origin,
                MessageChain().message(f"✅ 成功！每日推送时间已修改为 {h:02d}:{m:02d}。")
            )
        except Exception as e:
            logger.error(f"[HLTV插件] 修改定时任务时发生未知错误: {e}")
            await self.context.send_message(event.unified_msg_origin, MessageChain().message(f"修改失败，发生未知错误: {e}"))


