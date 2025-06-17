import svgwrite
from typing import List, Dict
import cairosvg
import os
from datetime import datetime


def generate_match_image(matches_list: List[Dict], output_path: str = "matches.png") -> str:
    # --- 1. 主题与布局常量 ---
    # 颜色
    BG_COLOR = '#f4f4f8'
    TITLE_COLOR = '#1a1a1a'
    DATE_COLOR = '#333333'
    TEXT_COLOR = '#4a4a4a'
    TIME_COLOR = '#6a6a6a'
    STAR_COLOR = '#ff8c00'
    CARD_BG_COLOR = '#ffffff'
    LINE_GRADIENT_CENTER_COLOR = '#dcdcdc'
    LINE_GRADIENT_EDGE_COLOR = BG_COLOR
    # 定义金色渐变色
    GOLD_COLOR_LIGHT = '#FCE570'
    GOLD_COLOR_DARK = '#D9A441'

    # 布局
    PADDING = 40
    WIDTH = 800
    LINE_HEIGHT_SMALL = 30
    TITLE_Y_SPACE = 100
    DATE_HEADER_Y_SPACE = 70
    CARD_HEIGHT = (LINE_HEIGHT_SMALL * 3) + 20
    CARD_GAP = 20
    CARD_CONTENT_PADDING = 25

    # 字体
    FONT_FAMILY = "'Noto Sans CJK SC', 'Helvetica', 'Arial', 'sans-serif'"

    # 星期映射
    CHINESE_WEEKDAYS = {
        'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
        'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
    }

    # --- 2. 预计算总高度 ---
    total_height = PADDING + TITLE_Y_SPACE
    if not matches_list:
        total_height += 100
    else:
        last_processed_date = None
        for match in matches_list:
            current_date = match['datetime'].date()
            if current_date != last_processed_date:
                total_height += DATE_HEADER_Y_SPACE
                last_processed_date = current_date
            total_height += CARD_HEIGHT + CARD_GAP
    total_height += PADDING

    # --- 3. 开始绘制 SVG ---
    temp_svg_path = "temp_matches.svg"
    dwg = svgwrite.Drawing(temp_svg_path, size=(f'{WIDTH}px', f'{total_height}px'))

    # 定义渐变
    defs = dwg.defs
    # 分割线渐变
    line_gradient = defs.add(svgwrite.gradients.LinearGradient(id='lineGradient', start=('0%', 0), end=('100%', 0)))
    line_gradient.add_stop_color(offset='0%', color=LINE_GRADIENT_EDGE_COLOR, opacity=0)
    line_gradient.add_stop_color(offset='50%', color=LINE_GRADIENT_CENTER_COLOR)
    line_gradient.add_stop_color(offset='100%', color=LINE_GRADIENT_EDGE_COLOR, opacity=0)

    # 定义金色边框渐变
    gold_gradient = defs.add(
        svgwrite.gradients.LinearGradient(id='goldBorderGradient', start=('0%', '0%'), end=('100%', '100%')))
    gold_gradient.add_stop_color(offset='0%', color=GOLD_COLOR_LIGHT)
    gold_gradient.add_stop_color(offset='50%', color=GOLD_COLOR_DARK)
    gold_gradient.add_stop_color(offset='100%', color=GOLD_COLOR_LIGHT)

    # 绘制背景
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG_COLOR))

    # --- 4. 绘制内容 ---
    y_pos = PADDING

    dwg.add(dwg.text("近期赛事", insert=(WIDTH / 2, y_pos + 45), font_family=FONT_FAMILY, font_size='32px',
                     font_weight="bold", fill=TITLE_COLOR, text_anchor="middle"))
    y_pos += TITLE_Y_SPACE

    if not matches_list:
        dwg.add(
            dwg.text("暂无即将开始的比赛", insert=(WIDTH / 2, y_pos + 40), font_family=FONT_FAMILY, font_size='20px',
                     fill=TEXT_COLOR, text_anchor="middle"))

    last_processed_date = None
    for match_data in matches_list:
        current_date = match_data['datetime'].date()

        if current_date != last_processed_date:
            dwg.add(dwg.rect(insert=(PADDING, y_pos), size=(WIDTH - 2 * PADDING, 1.5), fill="url(#lineGradient)"))
            english_day = match_data['datetime'].strftime('%A')
            chinese_day = CHINESE_WEEKDAYS.get(english_day, english_day)
            date_header_text = f"{chinese_day} - {current_date.strftime('%Y-%m-%d')}"
            dwg.add(dwg.text(date_header_text, insert=(PADDING, y_pos + 40), font_family=FONT_FAMILY, font_size='22px',
                             font_weight="500", fill=DATE_COLOR))
            y_pos += DATE_HEADER_Y_SPACE
            last_processed_date = current_date

        # 准备文本
        stars_text = '★' * match_data.get('stars', 0)
        event_info = match_data.get('event', '未知赛事')
        teams_info = f"{match_data.get('team1', 'TBA')} vs {match_data.get('team2', 'TBA')}"
        time_info = f"时间: {match_data['datetime'].strftime('%H:%M')}"

        best_of_info = str(match_data.get('best_of', '1')).upper()


        # 根据星级动态设置边框
        card_stroke = "none"
        card_stroke_width = "0"
        if match_data.get('stars', 0) == 5:
            card_stroke = "url(#goldBorderGradient)"
            card_stroke_width = "2"

        # 绘制卡片背景
        dwg.add(dwg.rect(
            insert=(PADDING, y_pos),
            size=(WIDTH - 2 * PADDING, CARD_HEIGHT),
            rx=10, ry=10,
            fill=CARD_BG_COLOR,
            stroke=card_stroke,
            stroke_width=card_stroke_width
        ))

        # 绘制三行布局
        card_content_y = y_pos + LINE_HEIGHT_SMALL
        card_left_margin = PADDING + CARD_CONTENT_PADDING
        card_right_margin = WIDTH - PADDING - CARD_CONTENT_PADDING

        # --- 绘制第一行 ---
        dwg.add(
            dwg.text(event_info, insert=(card_left_margin, card_content_y), font_family=FONT_FAMILY, font_size='18px',
                     font_weight="bold", fill=TEXT_COLOR))
        dwg.add(
            dwg.text(stars_text, insert=(card_right_margin, card_content_y), font_family=FONT_FAMILY, font_size='18px',
                     fill=STAR_COLOR, text_anchor="end"))

        # --- 绘制第二行 ---
        card_content_y += LINE_HEIGHT_SMALL
        dwg.add(
            dwg.text(teams_info, insert=(card_left_margin, card_content_y), font_family=FONT_FAMILY, font_size='18px',
                     fill=TEXT_COLOR))
        # vvvvvv 新增: 绘制 BO 信息 vvvvvv
        dwg.add(dwg.text(best_of_info, insert=(card_right_margin, card_content_y), font_family=FONT_FAMILY,
                         font_size='16px', fill=TIME_COLOR, text_anchor="end"))
        # ^^^^^^ 新增 ^^^^^^

        # --- 绘制第三行 ---
        card_content_y += LINE_HEIGHT_SMALL
        dwg.add(
            dwg.text(time_info, insert=(card_left_margin, card_content_y), font_family=FONT_FAMILY, font_size='16px',
                     fill=TIME_COLOR))

        y_pos += CARD_HEIGHT + CARD_GAP

    # --- 5. 保存并转换为 PNG ---
    try:
        dwg.save()
        cairosvg.svg2png(url=temp_svg_path, write_to=output_path)
    finally:
        if os.path.exists(temp_svg_path):
            os.remove(temp_svg_path)

    return os.path.abspath(output_path)
