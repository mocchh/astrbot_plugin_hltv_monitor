import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict


async def get_high_star_matches_from_url(url: str) -> List[Dict]:
    all_matches = []

    try:
        async with httpx.AsyncClient(http2=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }) as client:
            response = await client.get(url, timeout=20)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        all_sections = soup.select('.matches-list-section')
        if not all_sections:
            return []

        for section in all_sections:
            date_headline = section.select_one('.matches-list-headline')
            date_part_str = date_headline.text.strip().split(' - ')[
                -1] if date_headline and ' - ' in date_headline.text else None
            if not date_part_str:
                continue

            matches_in_section = section.select('.match-wrapper')

            for match in matches_in_section:
                if len(match.select('i.fa-star')) != 5:
                    continue
                lit_stars = len(match.select('i.fa-star:not(.faded)'))
                if lit_stars < 3:
                    continue

                event_tag = match.select_one('.match-event')
                event_name = event_tag.get('data-event-headline', "未知赛事").strip()

                if event_name == "未知赛事":
                    continue

                teams = match.select('.match-teamname')
                time_tag = match.select_one('.match-time')
                team1 = teams[0].text.strip() if len(teams) > 0 else "待定"
                team2 = teams[1].text.strip() if len(teams) > 1 else "待定"
                match_time_str = time_tag.text.strip() if time_tag else "00:00"

                try:
                    match_datetime = datetime.strptime(f"{date_part_str} {match_time_str}", "%Y-%m-%d %H:%M")
                except ValueError:
                    continue

                meta_tag = match.select_one('.match-meta')
                best_of = meta_tag.text.strip() if meta_tag else "未知"

                all_matches.append({
                    'datetime': match_datetime,
                    'event': event_name,
                    'stars': lit_stars,
                    'team1': team1,
                    'team2': team2,
                    'best_of' : best_of
                })

        if not all_matches:
            return []

        all_matches.sort(key=lambda x: x['datetime'])

        return all_matches[:5]

    except httpx.HTTPStatusError as e:
        return []
    except httpx.RequestError as e:
        return []
    except Exception as e:
        return []
