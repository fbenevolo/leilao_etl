import asyncio
import traceback
from playwright.async_api import async_playwright
from data import sites_list, site_template_dict


async def page_loop(page, parser, navigator):
    num_auctions_for_site = 0


    while True:
        cards = await parser.get_auction_cards(page)
        if cards:
            await cards[0].wait_for(
                state="visible",
                timeout=60000
            )

        for i, card in enumerate(cards):
            # if i == 1:
            #     print(await card.evaluate("el => el.outerHTML"))
            #     break

            auction = await parser.parse_auction(card)
            print(auction)
            num_auctions_for_site += 1
            # break
        # break
        if not await navigator.has_next_page(page):
            break

        await navigator.goto_next_page(page)

    return num_auctions_for_site


async def main():
    p = await async_playwright().start()
    browser = None

    total_auctions = 0
    auctions_for_site = 0

    try:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for site in sites_list[34:35]:
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

            # wait for page elements to load (in case of React application etc)
            await page.wait_for_timeout(7500)

            if not site_config.has_navbar_sections:
                auctions_scraped = await page_loop(page, parser, navigator)
                auctions_for_site += auctions_scraped
            else:
                navbar_section_elements = site_config.auction_navbar_selector
                for section in navbar_section_elements:
                    await parser.select_section_in_navbar(page, section)
                    await page.wait_for_timeout(7500)
                    auctions_scraped = await page_loop(page, parser, navigator)
                    auctions_for_site += auctions_scraped

            print(f"Num auction for site {site}: {auctions_for_site}")

            # break

            print("\n\n\n")
            total_auctions += auctions_for_site
            auctions_for_site = 0

        print(total_auctions)
    except Exception as e:
        print(type(e))
        print(e)
        traceback.print_exc()
        await page.wait_for_timeout(10000)
    finally:
        if browser is not None:
            await browser.close()
        await p.stop()


if __name__ == "__main__":
    asyncio.run(main())