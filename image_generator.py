import svgwrite
from typing import List, Dict
import cairosvg
import os
from datetime import datetime, timedelta


def generate_match_image(matches_list: List[Dict], output_path: str = "matches.png") -> str:
    """
    将比赛信息列表绘制成一张包含日期分组的卡片式 PNG 图片。
    此版本采用全新的居中对阵布局，突出队伍信息。

    :param matches_list: 包含比赛信息的列表。
                         格式: [{'datetime': dt, 'event': str, 'stars': int, 'team1': str, 'team2': str, 'best_of': int}]
    :param output_path: 最终输出的 PNG 图片路径。
    :return: 生成的 PNG 图片的绝对路径。
    """
    BG_COLOR = '#f4f4f8'
    TITLE_COLOR = '#1a1a1a'
    DATE_COLOR = '#333333'
    TEXT_COLOR = '#4a4a4a'
    TIME_COLOR = '#6a6a6a'
    STAR_COLOR = '#ff8c00'
    CARD_BG_COLOR = '#ffffff'
    LINE_GRADIENT_CENTER_COLOR = '#dcdcdc'
    LINE_GRADIENT_EDGE_COLOR = BG_COLOR
    GOLD_COLOR_LIGHT = '#FCE570'
    GOLD_COLOR_DARK = '#D9A441'

    PADDING = 40
    WIDTH = 800
    TITLE_Y_SPACE = 100
    DATE_HEADER_Y_SPACE = 70
    CARD_HEIGHT = 140
    CARD_GAP = 20

    FONT_FAMILY = "'Noto Sans CJK SC', 'Helvetica', 'Arial', 'sans-serif'"

    CHINESE_WEEKDAYS = {
        'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
        'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
    }

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

    temp_svg_path = "temp_matches.svg"
    dwg = svgwrite.Drawing(temp_svg_path, size=(f'{WIDTH}px', f'{total_height}px'))

    defs = dwg.defs
    line_gradient = defs.add(svgwrite.gradients.LinearGradient(id='lineGradient', start=('0%', 0), end=('100%', 0)))
    line_gradient.add_stop_color(offset='0%', color=LINE_GRADIENT_EDGE_COLOR, opacity=0)
    line_gradient.add_stop_color(offset='50%', color=LINE_GRADIENT_CENTER_COLOR)
    line_gradient.add_stop_color(offset='100%', color=LINE_GRADIENT_EDGE_COLOR, opacity=0)
    gold_gradient = defs.add(
        svgwrite.gradients.LinearGradient(id='goldBorderGradient', start=('0%', '0%'), end=('100%', '100%')))
    gold_gradient.add_stop_color(offset='0%', color=GOLD_COLOR_LIGHT)
    gold_gradient.add_stop_color(offset='50%', color=GOLD_COLOR_DARK)
    gold_gradient.add_stop_color(offset='100%', color=GOLD_COLOR_LIGHT)

    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=BG_COLOR))

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

        stars_text = '★' * match_data.get('stars', 0)
        event_info = match_data.get('event', '未知赛事')
        team1_name = match_data.get('team1', 'TBA')
        team2_name = match_data.get('team2', 'TBA')
        time_info = match_data['datetime'].strftime('%H:%M')
        best_of_info = f"BO{match_data.get('best_of', 1)}"

        card_stroke = "none"
        card_stroke_width = "0"
        if match_data.get('stars', 0) == 5:
            card_stroke = "url(#goldBorderGradient)"
            card_stroke_width = "2"

        dwg.add(dwg.rect(
            insert=(PADDING, y_pos),
            size=(WIDTH - 2 * PADDING, CARD_HEIGHT),
            rx=10, ry=10,
            fill=CARD_BG_COLOR,
            stroke=card_stroke,
            stroke_width=card_stroke_width
        ))

        card_center_x = WIDTH / 2
        card_top_y = y_pos

        dwg.add(dwg.text(
            event_info,
            insert=(card_center_x, card_top_y + 35),
            font_family=FONT_FAMILY, font_size='18px', fill=TEXT_COLOR, text_anchor="middle"
        ))

        dwg.add(dwg.text(
            team1_name,
            insert=(PADDING + 50, card_top_y + 95),
            font_family=FONT_FAMILY, font_size='24px', font_weight="bold", fill=TEXT_COLOR, text_anchor="start"
        ))

        dwg.add(dwg.text(
            team2_name,
            insert=(WIDTH - PADDING - 50, card_top_y + 95),
            font_family=FONT_FAMILY, font_size='24px', font_weight="bold", fill=TEXT_COLOR, text_anchor="end"
        ))

        dwg.add(dwg.text(
            time_info,
            insert=(card_center_x, card_top_y + 80),
            font_family=FONT_FAMILY, font_size='22px', font_weight="bold", fill=TITLE_COLOR, text_anchor="middle"
        ))

        dwg.add(dwg.text(
            best_of_info,
            insert=(card_center_x, card_top_y + 105),
            font_family=FONT_FAMILY, font_size='16px', fill=TIME_COLOR, text_anchor="middle"
        ))

        dwg.add(dwg.text(
            stars_text,
            insert=(card_center_x, card_top_y + 125),
            font_family=FONT_FAMILY, font_size='14px', fill=STAR_COLOR, text_anchor="middle"
        ))

        y_pos += CARD_HEIGHT + CARD_GAP

    try:
        dwg.save()
        cairosvg.svg2png(url=temp_svg_path, write_to=output_path)
    finally:
        if os.path.exists(temp_svg_path):
            os.remove(temp_svg_path)

    return os.path.abspath(output_path)
