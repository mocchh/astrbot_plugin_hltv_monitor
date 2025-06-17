import svgwrite
from typing import List, Dict
import cairosvg
import os
from datetime import datetime


def generate_match_image(matches_list: List[Dict], output_path: str = "matches.png") -> str:
    """
    将比赛信息列表绘制成一张包含日期分组的卡片式 PNG 图片。

    该函数整合了两种设计思路：
    1. 使用独立的、有背景的卡片来展示每场比赛，视觉更清晰。
    2. 按日期对比赛进行分组，并为每个日期添加标题头。
    3. 最终输出为 PNG 格式的图片文件。

    :param matches_list: 包含比赛信息的列表。
                         格式: [{'datetime': dt, 'event': str, 'stars': int, 'team1': str, 'team2': str}]
    :param output_path: 最终输出的 PNG 图片路径。
    :return: 生成的 PNG 图片的绝对路径。
    """
    # --- 1. 主题与布局常量 ---
    # 颜色
    BG_COLOR = '#f4f4f8'  # 轻微偏冷的灰色背景
    CARD_BG_COLOR = '#ffffff'  # 卡片背景
    TITLE_COLOR = '#1a1a1a'  # 主标题颜色
    DATE_COLOR = '#333333'  # 日期标题颜色
    TEXT_COLOR = '#4a4a4a'  # 主要文本颜色
    TIME_COLOR = '#6a6a6a'  # 时间文本颜色
    LINE_COLOR = '#e0e0e0'  # 分割线颜色
    STAR_COLOR = '#ff8c00'  # 星星颜色

    # 布局
    PADDING = 40
    WIDTH = 800
    LINE_HEIGHT_SMALL = 30
    TITLE_Y_SPACE = 100  # 顶部标题区域高度
    DATE_HEADER_Y_SPACE = 70  # 日期标题区域高度
    CARD_HEIGHT = (LINE_HEIGHT_SMALL * 3) + 20
    CARD_GAP = 20  # 卡片之间的垂直间距

    # 字体
    FONT_FAMILY = "'Noto Sans CJK SC', 'Helvetica', 'Arial', 'sans-serif'"

    # 星期映射
    CHINESE_WEEKDAYS = {
        'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
        'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
    }

    # --- 2. 预计算总高度 ---
    # 这是确保画布大小正确的关键一步
    total_height = PADDING + TITLE_Y_SPACE
    if not matches_list:
        total_height += 100  # 为"暂无比赛"信息留出空间
    else:
        last_processed_date = None
        for match in matches_list:
            current_date = match['datetime'].date()
            if current_date != last_processed_date:
                total_height += DATE_HEADER_Y_SPACE
                last_processed_date = current_date
            total_height += CARD_HEIGHT + CARD_GAP
    total_height += PADDING  # 底部留白

    # --- 3. 开始绘制 SVG ---
    temp_svg_path = "temp_matches.svg"
    dwg = svgwrite.Drawing(temp_svg_path, size=(f'{WIDTH}px', f'{total_height}px'))

    # 绘制背景
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG_COLOR))

    # --- 4. 绘制内容 ---
    y_pos = PADDING

    # 绘制主标题
    dwg.add(dwg.text(
        "近期赛事",
        insert=(WIDTH / 2, y_pos + 45),
        font_family=FONT_FAMILY, font_size='32px', font_weight="bold",
        fill=TITLE_COLOR, text_anchor="middle"
    ))
    y_pos += TITLE_Y_SPACE

    # 如果没有比赛数据
    if not matches_list:
        dwg.add(dwg.text(
            "暂无即将开始的比赛",
            insert=(WIDTH / 2, y_pos + 40),
            font_family=FONT_FAMILY, font_size='20px',
            fill=TEXT_COLOR, text_anchor="middle"
        ))

    # 绘制比赛列表
    last_processed_date = None
    for match_data in matches_list:
        current_date = match_data['datetime'].date()

        # 绘制新的日期标题
        if current_date != last_processed_date:
            # 分割线
            dwg.add(dwg.line(start=(PADDING, y_pos), end=(WIDTH - PADDING, y_pos), stroke=LINE_COLOR, stroke_width=1.5))

            english_day = match_data['datetime'].strftime('%A')
            chinese_day = CHINESE_WEEKDAYS.get(english_day, english_day)
            date_header_text = f"{chinese_day} - {current_date.strftime('%Y-%m-%d')}"

            dwg.add(dwg.text(
                date_header_text,
                insert=(PADDING, y_pos + 40),
                font_family=FONT_FAMILY, font_size='22px', font_weight="500", fill=DATE_COLOR
            ))
            y_pos += DATE_HEADER_Y_SPACE
            last_processed_date = current_date

        # vvvvvv 修改部分 vvvvvv
        # 准备卡片内文本 (移除了"赛事:"和"对阵:"前缀)
        stars_text = '★' * match_data.get('stars', 0)
        event_info = f"{match_data.get('event', '未知赛事')}"
        teams_info = f"{match_data.get('team1', 'TBA')} vs {match_data.get('team2', 'TBA')}"
        time_info = f"时间: {match_data['datetime'].strftime('%H:%M')}"
        # ^^^^^^ 修改部分 ^^^^^^

        # 绘制卡片背景
        dwg.add(dwg.rect(
            insert=(PADDING, y_pos),
            size=(WIDTH - 2 * PADDING, CARD_HEIGHT),
            rx=10, ry=10, fill=CARD_BG_COLOR
        ))

        card_content_y = y_pos + LINE_HEIGHT_SMALL  # 卡片内容起始 y

        # vvvvvv 修改部分 vvvvvv
        # 绘制卡片内容 (调整了布局)
        # 第一行: 赛事 和 星星
        dwg.add(dwg.text(event_info, insert=(PADDING + 20, card_content_y), font_family=FONT_FAMILY, font_size='18px',
                         font_weight="bold", fill=TEXT_COLOR))
        dwg.add(dwg.text(stars_text, insert=(WIDTH - PADDING - 20, card_content_y), font_family=FONT_FAMILY,
                         font_size='18px', fill=STAR_COLOR, text_anchor="end"))

        # 第二行: 对阵
        card_content_y += LINE_HEIGHT_SMALL
        dwg.add(dwg.text(teams_info, insert=(PADDING + 20, card_content_y), font_family=FONT_FAMILY, font_size='18px',
                         fill=TEXT_COLOR))

        # 第三行: 时间
        card_content_y += LINE_HEIGHT_SMALL
        dwg.add(dwg.text(time_info, insert=(PADDING + 20, card_content_y), font_family=FONT_FAMILY, font_size='16px',
                         fill=TIME_COLOR))
        # ^^^^^^ 修改部分 ^^^^^^

        y_pos += CARD_HEIGHT + CARD_GAP

    # --- 5. 保存并转换为 PNG ---
    try:
        dwg.save()
        cairosvg.svg2png(url=temp_svg_path, write_to=output_path)
    finally:
        # 确保临时 svg 文件被删除
        if os.path.exists(temp_svg_path):
            os.remove(temp_svg_path)

    return os.path.abspath(output_path)
