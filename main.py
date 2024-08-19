import asyncio
import json
import requests
from urllib.parse import urlparse, parse_qs
from config import bot_token, chat_ids, urls
import vinted_scraper.vintedScraper

async def scrapQuery(url):
    scraper = vinted_scraper.VintedScraper("https://www.vinted.pl")
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    params = {
        "order": query_params.get("order", [""])[0],
        "status_ids": ",".join(query_params.get("status_ids[]", [])),
        "brand_ids": ",".join(query_params.get("brand_ids[]", [])),
        "price_to": query_params.get("price_to", [""])[0],
        "catalog_id": query_params.get("catalog[]", [""])[0],
        "size_ids": ",".join(query_params.get("size_ids[]", [])),
    }

    displayed_ids_list = []
    send_photo_url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'

    while True:
        items = scraper.search(params)
        for item in items:
            item_id = item.id
            if item_id not in displayed_ids_list and (not displayed_ids_list or item_id > max(displayed_ids_list)):
                displayed_ids_list.append(item_id)
                if len(displayed_ids_list) > 100:
                    displayed_ids_list.pop(0)

                caption = (
                    f"Title: *{item.title}*\n"
                    f"Brand: *{item.brand.title}*\n"
                    f"Size: *{item.size_title}*\n"
                    f"Price: *{item.price} PLN* ({round(int(item.price) * 1.05 + 2.90, 2)} PLN)\n"
                )

                inline_keyboard = {
                    'inline_keyboard': [
                        [{'text': 'Buy Now', 'url': item.url}]
                    ]
                }

                photo_data = requests.get(item.photos[0].full_size_url)
                post_image = {'photo': ('photo.jpg', photo_data.content)}

                for chat_id in chat_ids:
                    data = {
                        'chat_id': chat_id,
                        'caption': caption,
                        'parse_mode': 'markdown',
                        'reply_markup': json.dumps(inline_keyboard)
                    }
                    requests.post(send_photo_url, files=post_image, data=data)

        await asyncio.sleep(10)

async def main():
    tasks = [scrapQuery(url) for url in urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())