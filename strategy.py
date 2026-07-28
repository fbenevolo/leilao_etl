from models import WaitStrategy

class BrameLeiloesStrategy(WaitStrategy):
    async def wait(self, page):
        await page.wait_for_load_state("domcontentloaded")

        await page.locator(
            'a[href*="todos-eventos"]'
        ).wait_for(
            state="visible",
            timeout=60000
        )