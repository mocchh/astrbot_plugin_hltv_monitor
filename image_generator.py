import svgwrite
from typing import List, Dict
import cairosvg
import os


def generate_match_image(matches_list: List[Dict]) -> str:
    """
    将排序后的比赛信息绘制成一张矢量图 (SVG)，并返回图片路径。
    """
    # --- 主题颜色 (CSS 格式) ---
    BG_COLOR = '#fafaf0'  # 米白色背景
    TITLE_COLOR = '#1e1e1e'  # 深黑色标题
    DATE_COLOR = '#505050'  # 深灰色日期
    TEXT_COLOR = '#323232'  # 深灰色正文
    LINE_COLOR = '#c8c8be'  # 分割线颜色
    STAR_COLOR = '#ff8c00'  # 深橙色星星

    # --- 布局参数 ---
    padding = 40
    width = 800
    line_height_small = 38
    line_height_large = 55
    date_header_height = 60

    # --- 字体设置 ---
    # 使用通用的中英文无衬线字体，提高跨平台兼容性
    font_family = "'Noto Sans CJK SC', 'Noto Sans CJK', sans-serif"

    # --- 星期英中映射 ---
    chinese_weekdays = {
        'Monday': '周一',
        'Tuesday': '周二',
        'Wednesday': '周三',
        'Thursday': '周四',
        'Friday': '周五',
        'Saturday': '周六',
        'Sunday': '周日'
    }

    # --- 动态计算图片总高度 ---
    y_pos = padding
    y_pos += line_height_large  # 标题空间

    # 预计算总高度
    last_processed_date = ""
    for match in matches_list:
        current_date = match['datetime'].strftime('%Y-%m-%d')
        if current_date != last_processed_date:
            y_pos += 40  # 日期标题的上下间距
            y_pos += date_header_height
            last_processed_date = current_date

        y_pos += (line_height_small * 3) + 15  # 每个比赛块的高度和下边距

    final_height = y_pos

    # --- 开始绘制 ---
    output_filename = "hltv_matches.svg"
    dwg = svgwrite.Drawing(output_filename, size=(f'{width}px', f'{final_height}px'))

    # 直接使用计算出的精确像素值，而不是'100%'，以确保所有查看器都能正确渲染背景。
    dwg.add(dwg.rect(insert=(0, 0), size=(width, final_height), fill=BG_COLOR))

    # --- 绘制内容 ---
    y_pos = padding
    # 绘制标题
    dwg.add(dwg.text(
        "近期赛事",
        insert=(padding, y_pos + 32),  # 调整y坐标以使其基线正确
        font_family=font_family, font_size='32px', font_weight="bold", fill=TITLE_COLOR
    ))
    y_pos += line_height_large

    last_processed_date = ""
    for match_data in matches_list:
        current_date_str = match_data['datetime'].strftime('%Y-%m-%d')

        if current_date_str != last_processed_date:
            y_pos += 20
            dwg.add(dwg.line(start=(padding, y_pos), end=(width - padding, y_pos), stroke=LINE_COLOR, stroke_width=1))
            y_pos += 20

            english_day = match_data['datetime'].strftime('%A')
            chinese_day = chinese_weekdays.get(english_day, english_day)  # 如果找不到则用回英文
            date_header_text = f"{chinese_day} - {current_date_str}"

            dwg.add(dwg.text(
                date_header_text,
                insert=(padding, y_pos + 24),
                font_family=font_family, font_size='24px', fill=DATE_COLOR
            ))
            y_pos += date_header_height
            last_processed_date = current_date_str

        y_pos_block_start = y_pos

        stars_text = '★' * match_data['stars']
        event_info = f"赛事: {match_data['event']}"
        teams_info = f"对阵: {match_data['team1']} vs {match_data['team2']}"
        time_info = f"时间: {match_data['datetime'].strftime('%H:%M')}"

        dwg.add(
            dwg.text(event_info, insert=(padding, y_pos_block_start + 20), font_family=font_family, font_size='20px',
                     fill=TEXT_COLOR))
        dwg.add(dwg.text(stars_text, insert=(width - padding, y_pos_block_start + 20), font_family=font_family,
                         font_size='20px', fill=STAR_COLOR, text_anchor="end"))
        y_pos_block_start += line_height_small

        dwg.add(
            dwg.text(teams_info, insert=(padding, y_pos_block_start + 20), font_family=font_family, font_size='20px',
                     fill=TEXT_COLOR))
        y_pos_block_start += line_height_small

        dwg.add(dwg.text(time_info, insert=(padding, y_pos_block_start + 20), font_family=font_family, font_size='20px',
                         fill=TEXT_COLOR))

        y_pos += (line_height_small * 3) + 15

    dwg.save()
    cairosvg.svg2png(
        url = output_filename,
        write_to = './matches.png'
    )


    return output_filename
