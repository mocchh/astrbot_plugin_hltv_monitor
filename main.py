import logging
from astrbot.api.event import MessageChain, filter, AstrMessageEvent
from astrbot.api.star import register, Star
from AstrBot.astrbot.core.star import Context


from .HLTV_Match_Client import get_high_star_matches_from_url
from .HLTV_GetResult import get_hltv_results
from .image_generator import generate_match_image

logger = logging.getLogger(__name__)

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

    @filter.command("hltv")
    async def show_hltv_info(self, event: AstrMessageEvent):
        url = "http://49.4.115.149:8080/latest_matches.html"
        try:
            print("开始获取数据")

            all_matches = await get_high_star_matches_from_url(url)
            image_path = generate_match_image(all_matches)
            logger.info(f"图片生成成功，路径: {image_path}")

            print("获取完成")
        except Exception as e:
            print(f"获取 HLTV 比赛数据时发生错误: {e}")
            error_message = f"抱歉，获取 HLTV 比赛数据时出错了。错误详情: {e}"
            await self.context.send_message(event.unified_msg_origin, MessageChain().message(error_message))
            return

        yield event.image_result("./matches.png")
