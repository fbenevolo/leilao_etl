from interfaces import AuctionNavigator

class AlexandreCostaNavigator(AuctionNavigator):
    async def has_next_page(self, page) -> bool:
        next_button = page.locator(
        ".Anuncio1_seletor:has(.Anuncio1_seletorStr:text-is('>'))"
        )

        return await next_button.count() > 0

    async def goto_next_page(self, page):
        next_button = page.locator(
            ".Anuncio1_seletor:has(.Anuncio1_seletorStr:text-is('>'))"
        )
    
        await next_button.click()
        await page.wait_for_load_state("networkidle")


class AlexandreLeiloeiroNavigator(AuctionNavigator):
    async def has_next_page(self, page) -> bool:
        return False

    async def goto_next_page(self, page):
        return


class LeiloesJaNavigator(AuctionNavigator):
    async def has_next_page(self, page) -> bool:
            next_button = page.locator(".show-pagination li:last-child a")
            href = await next_button.get_attribute("href")
            return href is not None

    async def goto_next_page(self, page):
        next_button = page.locator(".show-pagination li:last-child a")
        await next_button.click()
        await page.wait_for_load_state("networkidle")


class JVLeiloesNavigator(AlexandreLeiloeiroNavigator):
    pass


class BrameLeiloesNavigator(AlexandreLeiloeiroNavigator):
    pass


class RicartNavigator(AlexandreLeiloeiroNavigator):
    pass


class MauricioKronembergNavigator(AlexandreCostaNavigator):
    pass