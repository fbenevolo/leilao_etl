from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

@dataclass(frozen=True)
class Selector:
    strategy: str
    value: str


class AuctionType(Enum):
    AUCTION = "auction"
    DIRECT_SALE = "direct_sale"


class RoundStatus(Enum):
    OPEN = "em aberto"
    CLOSED = "encerrado"
    SOON = "em breve"


class ItemNegociated(Enum):
    IMOVEL = "imovel"
    CARRO = "carro"
    DIVERSOS = "diversos"

@dataclass
class AuctionRound:
    name: str
    end: datetime | None
    start: datetime | None = None
    initial_bid: float | None = None
    status: str | None = None


@dataclass
class ProposalPhase:
    name: str
    deadline: datetime | None


@dataclass
class AuctionModel:
    title: str
    description: str
    status: str
    auction_type: str
    proposal_deadline: list[ProposalPhase] | None = None
    minimum_bid: float | None = None

    rounds: list[AuctionRound] | None =  None
    image_url: str | None = None

    item_negociated: str | None = ItemNegociated.IMOVEL.value


class AuctionNavigator(ABC):
    @abstractmethod
    async def has_next_page(self, page) -> bool:
        pass

    @abstractmethod
    async def goto_next_page(self, page):
        pass


class AuctionParser(ABC):
    async def select_section_in_navbar(self, page, navbar_selector):
        if navbar_selector is not None:
            locator = None
            if navbar_selector.strategy == "css":
                locator = page.locator(navbar_selector.value)
            elif navbar_selector.strategy == "text":
                locator = page.get_by_text(navbar_selector.value)

            count = await locator.count()
            if count > 1:
                for i in range(count):
                    candidate = locator.nth(i)
                    if await candidate.is_visible():
                        locator = candidate
                        break
            else:
                locator = locator.first

            await locator.wait_for(state="visible", timeout=30000)
            await locator.click(trial=True)
            await locator.click(force=True)
            await page.wait_for_timeout(5000)

    async def parse_auction(self, card):
        auction_type = await self._detect_auction_type(card)
        if auction_type == AuctionType.AUCTION:
            rounds = await self._rounds(card)
            proposal_deadline = None
            minimum_bid = None
        else:
            rounds = None
            proposal_deadline = await self._proposal_deadline(card)
            minimum_bid = await self._minimum_bid(card)

        return AuctionModel(
            title=await self._title(card),
            description=await self._description(card),
            status=await self._status(card),
            auction_type=auction_type.value,
            rounds=rounds,
            proposal_deadline=proposal_deadline,
            minimum_bid=minimum_bid,
            image_url=await self._image_url(card),
            item_negociated=await self._item_negociated(card)
        )

    async def _detect_auction_type(self, card):
        if await self._has_direct_sale(card):
            return AuctionType.DIRECT_SALE
        return AuctionType.AUCTION

    async def _has_direct_sale(self, card):
        return False

    async def _proposal_deadline(self, card):
        return None

    async def _minimum_bid(self, card):
        return None

    async def _item_negociated(self, card) -> str | None:
            return ItemNegociated.IMOVEL.value
    
    
    @abstractmethod
    async def get_auction_cards(self, page):
        pass

    @abstractmethod
    async def _title(self, card):
        pass
        
    @abstractmethod
    async def _description(self, card):
        pass

    @abstractmethod
    async def _status(self, card):
        pass

    @abstractmethod
    async def _rounds(self, card):
        pass

    @abstractmethod
    async def _image_url(self, card):
        pass


class WaitStrategy(ABC):
    @abstractmethod
    async def wait(self, page):
        pass


@dataclass
class SiteConfig:
    auction_parser: AuctionParser
    auction_navigator: AuctionNavigator
    wait_strategy: WaitStrategy | None = None
    auction_navbar_selector: List[Selector] | None = None
    show_more_selector: Selector | None = None

    @property
    def has_navbar_sections(self) -> bool:
        return bool(self.auction_navbar_selector)