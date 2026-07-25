from abc import ABC, abstractmethod


class AuctionNavigator(ABC):
    @abstractmethod
    async def has_next_page(self, page) -> bool:
        pass

    @abstractmethod
    async def goto_next_page(self, page):
        pass
