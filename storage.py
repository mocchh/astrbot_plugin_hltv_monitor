from astrbot.api import logger
import json
import os

# 存储HLTV比赛订阅者信息的
SUBSCRIPTION_FILE = "data/hltv_monitor_subscriptions.json"
SCHEDULE_CONFIG_FILE = "data/hltv_schedule_config.json"


def load_subscriptions() -> set:
    """
    从JSON文件中加载订阅列表。
    如果文件不存在或加载失败，返回一个空集合。
    """
    # 确保数据文件夹存在
    os.makedirs(os.path.dirname(SUBSCRIPTION_FILE), exist_ok=True)
    try:
        if os.path.exists(SUBSCRIPTION_FILE):
            with open(SUBSCRIPTION_FILE, 'r', encoding='utf-8') as f:
                # 使用 set 可以自动处理重复的ID
                return set(json.load(f))
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"[HLTV存储] 加载订阅文件失败: {e}")
    return set()


def save_subscriptions(subscriptions: set):
    """
    将当前的订阅列表保存到JSON文件。
    """
    try:
        with open(SUBSCRIPTION_FILE, 'w', encoding='utf-8') as f:
            # json转为list
            json.dump(list(subscriptions), f, indent=4)
    except IOError as e:
        logger.error(f"[HLTV存储] 保存订阅文件失败: {e}")


def load_schedule_time() -> dict:
    """
    从JSON文件中加载定时任务的时间。
    如果文件不存在或加载失败，返回默认时间（早上8点）。
    """
    os.makedirs(os.path.dirname(SCHEDULE_CONFIG_FILE), exist_ok=True)
    default_time = {'hour': 8, 'minute': 0}
    try:
        if os.path.exists(SCHEDULE_CONFIG_FILE):
            with open(SCHEDULE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"[HLTV存储] 加载定时任务时间配置失败: {e}")
    return default_time


def save_schedule_time(time_config: dict):
    """将新的定时任务时间保存到JSON文件。"""
    try:
        with open(SCHEDULE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(time_config, f, indent=4)
    except IOError as e:
        logger.error(f"[HLTV存储] 保存定时任务时间配置失败: {e}")