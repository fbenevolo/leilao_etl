import asyncio

from playwright.async_api import async_playwright
from data import sites_list, site_template_dict

async def main():
    p = await async_playwright().start()
    browser = None

    try:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        num_auctions_for_site = 0
        total_auctions = 0
        for site in sites_list[20:21]:
            url = site.strip()

            site_config = site_template_dict.get(url, None)
            if site_config is None:
                print(f"Site template for {url} is None. Continuing...")
                continue

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            strategy = site_config.wait_strategy
            parser = site_config.auction_parser
            navigator = site_config.auction_navigator

            if strategy:
                await strategy.wait(page)
            await parser.select_section_in_navbar(page, site_config.auction_navbar_selector)

            while True:
                cards = await parser.get_auction_cards(page)
                if cards:
                    await cards[0].wait_for(
                        state="visible",
                        timeout=60000
                    )

                for i, card in enumerate(cards):
                    # if i == 3:
                    # print(await card.evaluate("el => el.outerHTML"))
                    # break

                    auction = await parser.parse_auction(card)
                    print(auction)
                    # break
                    num_auctions_for_site += 1

                if not await navigator.has_next_page(page):
                    break

                await navigator.goto_next_page(page)

            print(f"Num auction for site {site}: {num_auctions_for_site}")
            total_auctions += num_auctions_for_site
            num_auctions_for_site = 0

            # break

            print("\n\n\n")

        print(total_auctions)
    except Exception as e:
        print(type(e))
        print(e)
        await page.wait_for_timeout(10000)
    finally:
        if browser is not None:
            await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(main())