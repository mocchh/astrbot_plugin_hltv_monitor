import cloudscraper
from bs4 import BeautifulSoup
import asyncio


async def get_hltv_results():

    scraper = cloudscraper.create_scraper()
    url = "https://www.hltv.org/results?stars=3"

    print(f"正在从 {url} 获取数据...")

    try:
        response = await asyncio.to_thread(scraper.get, url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        matches = soup.find_all('div', class_='result-con')

        if not matches:
            print("未找到比赛记录。")
            return "未找到比赛记录。"

        print("\n--- 最近的比赛结果 (仅显示前 5 条) ---\n")
        results = []
        for match in matches[:5]:
            team1_tag = match.find('div', class_='team1').find('div', class_='team')
            team2_tag = match.find('div', class_='team2').find('div', class_='team')
            score = match.find('td', class_='result-score').text.strip()
            event = match.find('span', class_='event-name').text.strip()

            if team1_tag and team2_tag:
                team1 = team1_tag.text.strip()
                team2 = team2_tag.text.strip()
                result_string = f"{event}: {team1} [{score}] {team2}"
                print(result_string)
                results.append(result_string)
        return  "\n".join(results)

    except Exception as e:
        print(f"获取数据失败: {e}")
        return f"获取数据失败{e}"


if __name__ == "__main__":
    get_hltv_results()
