import platform

import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
import sys


async def request(url):

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f"Error status {response.status} for {url}")
        except aiohttp.ClientConnectionError as e:
            logging.error(f"Connection error {url}: {e}")
        return None


async def get_exchange(days):
    results = []
    for i in range(days):
        target_date = datetime.now() - timedelta(days=i)
        formatted_date = target_date.strftime("%d.%m.%Y")
        url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={formatted_date}"
        result = await request(url)
        if result:
            rates = {}
            for currency_data in result['exchangeRate']:
                currency = currency_data['currency']
                if currency in ['EUR', 'USD']:
                    rates[currency] = {
                        'sale': float(currency_data['saleRate']),
                        'purchase': float(currency_data['purchaseRate'])
                    }
            results.append({formatted_date: rates})

    return results


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        days = int(input("Please, put number of days (no more than 10): "))
    except ValueError:
        print("Invalid input format. Enter an integer.")
        sys.exit(1)

    if days > 10:
        print("The number of days must be lower than 10")
        sys.exit(1)

    if days <= 0:
        print("The number of days must be greater than 0")
        sys.exit(1)

    r = asyncio.run(get_exchange(days))
    print(r)
