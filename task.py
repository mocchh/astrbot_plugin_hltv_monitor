import logging
import os
from astrbot.api.event import MessageChain

# 从您的项目导入任务相关的模块
# 请确保这些文件与您的插件在正确的路径下，以便导入
from .HLTV_Match_Client import get_high_star_matches_from_url
from .image_generator import generate_match_image

# --- 全局配置 ---
logger = logging.getLogger(__name__)
# 比赛信息源 URL
MATCHES_URL = "http://49.4.115.149:8080/latest_matches.html"


async def get_report_message_chain() -> MessageChain:
    """
    一个独立的函数，负责获取数据、生成图片并返回一个完整的MessageChain。
    这避免了代码重复。
    """
    try:
        logger.info("[HLTV任务] 开始获取比赛数据...")
        all_matches = await get_high_star_matches_from_url(MATCHES_URL)
        image_path = generate_match_image(all_matches)
        logger.info(f"[HLTV任务] 比赛图片生成成功，路径: {image_path}")

        # 使用 file:/// 协议来指定本地文件的绝对路径
        absolute_image_path = os.path.abspath(image_path)
        return MessageChain().message("这是为您生成的HLTV比赛预告：").image(f"file:///{absolute_image_path}")

    except Exception as e:
        logger.error(f"[HLTV任务] 在获取数据或生成图片时发生错误: {e}")
        return MessageChain().message(f"抱歉，获取HLTV比赛数据时出错了。详情: {e}")

