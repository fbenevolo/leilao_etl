from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass(frozen=True)
class Selector:
    strategy: str
    value: str

class AuctionType(Enum):
    AUCTION = "auction"
    DIRECT_SALE = "direct_sale"

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
            if navbar_selector.strategy == "css":
                await page.locator(navbar_selector.value).click()
            elif navbar_selector.strategy == "text":
                await page.get_by_text(navbar_selector.value).click()

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
            image_url=await self._image_url(card)
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


@dataclass
class SiteConfig:
    auction_parser: AuctionParser
    auction_navigator: AuctionNavigator
    auction_navbar_selector: Selector | None = None
    show_more_selector: Selector | None = None