import re
from datetime import datetime
from models import AuctionRound, AuctionParser, ProposalPhase, RoundStatus
from formatters import *

class AlexandreCostaParser(AuctionParser):
    async def get_auction_cards(self, page):
        cards = page.locator(
            "div[id^='divAnuncio']"
        )

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]

    async def _title(self, card):
        return await card.locator(".Anuncio1_tit").text_content()
        
    async def _description(self, card):
        return await card.locator(".Anuncio1_descr").text_content()

    async def _status(self, card):
        return await card.locator("#btnCons").get_attribute("value")

    async def _rounds(self, card):
        rounds = []
    
        rounds_container = card.locator(":scope > div").nth(1)
    
        # Procurar todos os elementos que representam um round
        # Eles sempre contêm exatamente 2 elementos .Anuncio1_data
        candidates = rounds_container.locator("div:has(> .Anuncio1_data)")

        count = await candidates.count()
    
        for i in range(count):
            candidate = candidates.nth(i)
    
            data_fields = candidate.locator(".Anuncio1_data")
    
            # Um round válido tem 2 campos nome + data ou 3 campos
                # nome + data/hora
                # nome + data + hora
            data_fields_count = await data_fields.count()
            if data_fields_count < 2:
                continue
    
            name = (await data_fields.nth(0).text_content() or "").strip()
            date = (await data_fields.nth(1).text_content() or "").strip().replace("h", "") # remover o "h" da hora caso exista
            hour = None

            if data_fields_count >= 3:
                hour = (await data_fields.nth(2).text_content() or "").strip().replace("h", "")

            if hour:
                date = f"{date} {hour}"

            end = format_datetime(
                date,
                "%d/%m/%Y %H:%M"
            )

            rounds.append(
                AuctionRound(
                    name=name,
                    end=end
                )
            )
    
        return rounds

    async def _image_url(self, card):
        image = (
            card.locator("div[class^='Anuncio'][class$='_img']")
                .locator("img")
                .first
        )
        return await image.get_attribute("src")


class AlexandreLeiloeiroParser(AuctionParser):
    async def get_auction_cards(self, page):
        cards = page.locator(
            "article[class^='evento-index']"
        )

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]

    async def _title(self, card):
        return await card.locator("h3").text_content()

    async def _description(self, card):
        return None

    async def _status(self, card):
        return await card.locator(".strong-status").text_content()

    async def _rounds(self, card):
        rounds = []
    
        round_cards = card.locator("ul.cont-datas > li")
    
        for i in range(await round_cards.count()):
            round_card = round_cards.nth(i)
    
            if not await round_card.is_visible():
                continue
    
            name = await round_card.locator(".line-1 strong").text_content()
            start = await self._round_start(round_card)
            end = await self._round_end(round_card)
    
            rounds.append(
                AuctionRound(
                    name=(name or "").strip(),
                    start=start,
                    end=end,
                )
            )
    
        return rounds

    async def _round_start(self, round_card):
        value = await round_card.locator(
            ".col-line span"
        ).first.text_content()

        return format_datetime(
            value,
            "%d/%m/%Y %H:%M"
        )


    async def _round_end(self, round_card):
        value = await round_card.locator(
            ".col-line span"
        ).last.text_content()

        return format_datetime(
            value,
            "%d/%m/%Y %H:%M"
        )

    async def _image_url(self, card):
        image = card.locator(".cont-picture img")
        if await image.count() == 0:
            return None
    
        return await image.first.get_attribute("src")


class AndresRosaCostaParser(AlexandreCostaParser):
    async def _title(self, card):
        return await card.locator(".Anuncio2_faixa").text_content()

    async def _description(self, card):
        blocks = card.locator(":scope > div")
        return await blocks.nth(2).locator(
            "div"
        ).first.text_content()

    async def _status(self, card):
        return await card.locator("#btnCons").get_attribute("value")

    async def _rounds(self, card):
        rounds = []

        blocks = card.locator(":scope > div")
    
        for i in range(await blocks.count()):
            text = await blocks.nth(i).inner_text()
    
            if "leilão" not in text.lower():
                continue
    
            round_data = self._parse_round(text)
    
            if round_data:
                rounds.append(round_data)
    
        return rounds

    def _parse_round(self, text: str) -> AuctionRound | None:
        """
        Exemplo de entrada:
    
        1° LEILÃO: 24/06/2021 - 11:15H
        LANCE INICIAL: 208.429,64
        """
    
        name_match = re.search(
            r"(\d+°\s*LEILÃO)",
            text
        )
    
        end_match = re.search(
            r"LEILÃO:\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})H",
            text
        )
    
        if not name_match:
            return None
    
        end = None
        if end_match:
            date_str = end_match.group(1)
            time_str = end_match.group(2)
    
            end = datetime.strptime(
                f"{date_str} {time_str}",
                "%d/%m/%Y %H:%M"
            )
    
        return AuctionRound(
            name=(name_match.group(1) or "").strip(),
            end=end
        )


class FacanhaLeiloesParser(AlexandreLeiloeiroParser):
    async def _rounds(self, card):
        rounds = []
    
        round_cards = card.locator(
            ".cont-datas > li"
        )
    
        for i in range(await round_cards.count()):
            round_card = round_cards.nth(i)
    
            name = await round_card.locator(
                ".line-1 strong"
            ).text_content()
    
            date_text = await round_card.locator(
                ".col-line"
            ).nth(0).locator("span").text_content()
    
            bid_text = await round_card.locator(
                ".col-line"
            ).nth(1).locator("span").text_content()
    
            rounds.append(
                AuctionRound(
                    name=(name or "").strip(),
                    end=format_datetime(date_text, "%d/%m/%Y %H:%M"),
                    initial_bid=format_money(bid_text)
                )
            )
    
        return rounds

    def _parse_datetime(self, value: str):
        if not value:
            return None
    
        return datetime.strptime(
            value.strip(),
            "%d/%m/%Y %H:%M"
        )


class DePaulaParser(AuctionParser):
    async def get_auction_cards(self, page):
        cards = page.locator("div.flex-leiloes article")

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]

    async def _title(self, card):
        return await card.locator("h3").text_content()

    async def _description(self, card):

        description = card.locator(
            "p[style*='font-weight: 700']"
        )
        if await description.count() == 0:
            return None

        return await description.text_content()

    async def _status(self, card):
        return await card.locator(
            "span.leilao-online"
        ).text_content()

    async def _rounds(self, card):
        rounds = []

        items = card.locator("div.content-card li")

        for i in range(await items.count()):
            item = items.nth(i)

            strong = item.locator("strong")
            p = item.locator("p").first
            span = item.locator(":scope > span").first

            name = None
            end = None
            initial_bid = None

            if await strong.count():
                name = (await strong.text_content()).replace(":", "").strip()

            if await p.count():
                text = (await p.text_content()).strip()

                match = re.search(
                    r"(\d{2}/\d{2}/\d{4})\s*-\s*Encerramento às\s*(\d{2}:\d{2})",
                    text,
                )

                if match:
                    end = datetime.strptime(
                        f"{match.group(1)} {match.group(2)}",
                        "%d/%m/%Y %H:%M",
                    )

            if await span.count():
                text = await span.text_content()

                match = re.search(
                    r"R\$\s*([\d\.]+,\d{2})",
                    text,
                )

                if match:
                    initial_bid = float(
                        match.group(1)
                        .replace(".", "")
                        .replace(",", ".")
                    )

            rounds.append(
                AuctionRound(
                    name=name,
                    end=end,
                    initial_bid=initial_bid,
                )
            )

        return rounds

    async def _image_url(self, card):
        images = card.locator("div.cont-foto img")

        if await images.count() == 0:
            return None

        return await images.first.get_attribute("src")


class EdgarCarvalhoParser(AuctionParser):
    async def get_auction_cards(self, page):
        cards = page.locator(".flex-cards article")

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]

    async def _title(self, card):
        return await card.locator("h3").text_content()

    async def _description(self, card):
        return None

    async def _status(self, card):
        status = card.locator(".g2 .c-left span")
        if await status.count() == 0:
            return None
        
        return await status.text_content()

    async def _rounds(self, card):
        rounds = []

        items = card.locator("ul.list-datas > li")

        for i in range(await items.count()):
            item = items.nth(i)

            text = (await item.text_content()).strip()

            # Ignora placeholders ocultos
            if not text or await item.get_attribute("style") == "opacity: 0;":
                continue

            name = None
            end = None

            match = re.match(
                r"(.+?):\s*(\d{2}/\d{2}/\d{4})\s+às\s+(\d{2}:\d{2})",
                text,
            )

            if match:
                name = match.group(1).strip()
                end = datetime.strptime(
                    f"{match.group(2)} {match.group(3)}",
                    "%d/%m/%Y %H:%M",
                )
            else:
                name = text

            rounds.append(
                AuctionRound(
                    name=name,
                    end=end,
                )
            )

        return rounds

    async def _image_url(self, card):
        image = card.locator(".r2 img")

        if await image.count() == 0:
            return None

        return await image.first.get_attribute("src")


class PortellaLeiloesParser(DePaulaParser):
    async def _rounds(self, card):
        rounds = []

        items = card.locator("ul.content-card > li")

        for i in range(await items.count()):
            item = items.nth(i)

            name = (
                await item.locator("div.data strong").text_content()
            ).replace(":", "").strip()

            # Remove o texto do ícone caso apareça
            name = re.sub(r"^\s*", "", name)

            end = None
            date_text = await item.locator("div.data p").text_content()

            match = re.search(
                r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})",
                date_text,
            )

            if match:
                end = format_datetime(f"{match.group(1)} {match.group(2)}",
                                      "%d/%m/%Y %H:%M")

            # Lance inicial
            initial_bid = None
            bid_text = await item.locator("div.lance-card span").text_content()

            match = re.search(
                r"R\$\s*([\d\.]+,\d{2})",
                bid_text,
            )

            if match:
                initial_bid = format_money(match.group(1)) 

            # Status
            data_div = item.locator("div.data")
            classes = await data_div.get_attribute("class") or ""

            status = RoundStatus.CLOSED.value if "encerrado" in classes.split() else RoundStatus.OPEN.value

            rounds.append(
                AuctionRound(
                    name=name,
                    end=end,
                    initial_bid=initial_bid,
                    status=status,
                )
            )

        return rounds


class GustavoLeiloeiroParser(AlexandreLeiloeiroParser):
    async def get_auction_cards(self, page):
        cards = page.locator(
            "div.flex-cards article"
        )

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]


class LeilaoBrasilParser(AlexandreLeiloeiroParser):
    async def get_auction_cards(self, page):
        cards = page.locator("div.flex-cards article")

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]

    async def _rounds(self, card):
        rounds = []

        round_cards = card.locator("ul.cont-datas > li")

        for i in range(await round_cards.count()):
            round_card = round_cards.nth(i)

            if not await round_card.is_visible():
                continue

            classes = await round_card.get_attribute("class") or ""

            name = await round_card.locator(".line-1 strong").text_content()
            start = await self._round_start(round_card)
            end = await self._round_end(round_card)

            initial_bid = None
            bid = round_card.locator("small.valInit")

            if await bid.count() > 0:
                text = await bid.text_content()

                match = re.search(r"R\$\s*([\d\.,]+)", text)
                if match:
                    initial_bid = float(
                        match.group(1)
                        .replace(".", "")
                        .replace(",", ".")
                    )

            round_status = RoundStatus.OPEN.value
            auction_status = await self._status(card)
            if "data-off" in classes.split():
                round_status = RoundStatus.CLOSED.value
            elif auction_status.lower() == "em breve":
                round_status = RoundStatus.SOON.value

            rounds.append(
                AuctionRound(
                    name=(name or "").strip(),
                    start=(start or "").strip(),
                    end=(end or "").strip(),
                    initial_bid=initial_bid,
                    status=round_status,
                )
            )

        return rounds


class RymerParser(AuctionParser):
    async def get_auction_cards(self, page):
        flex_cards = page.locator(".flex-cards")

        selected_flex_cards = [
            flex_cards.nth(1),
            flex_cards.nth(2)
        ]

        articles = []

        for flex_card in selected_flex_cards:
            count = await flex_card.locator("article").count()
            for i in range(count):
                articles.append(
                    flex_card.locator("article").nth(i)
                )

        return articles

    async def _has_direct_sale(self, card):
        return await card.locator(
            ".vendadireta"
        ).count() > 0

    async def _title(self, card):
        return await card.locator(
            "h3"
        ).text_content()
        
    async def _description(self, card):
        return await card.locator("p").first.text_content()

    async def _status(self, card):
        return await card.locator(".status-leilao").first.text_content()

    async def _rounds(self, card):
        rounds = []

        items = card.locator(".list-datas li")
        count = await items.count()

        for i in range(count):
            item = items.nth(i)

            text = (await item.inner_text()).strip()
            if "Leilão" not in text:
                continue

            match = re.search(
                r"(.+?Leilão):?\s*(\d{1,2}/\d{1,2})\s*-\s*(\d{1,2})h(\d{2})",
                text
            )

            if not match:
                continue

            round_name = match.group(1).strip()
            day_month = match.group(2)
            hour = match.group(3)
            minute = match.group(4)

            end = datetime.strptime(
                f"{day_month}/2026 {hour}:{minute}",
                "%d/%m/%Y %H:%M"
            )

            initial_bid = None

            bid_match = re.search(
                r"Lance inicial:\s*R\$\s*([\d\.,]+)",
                text
            )

            if bid_match:
                initial_bid = format_money(bid_match.group(1))

            rounds.append(
                AuctionRound(
                    name=round_name,
                    end=end,
                    initial_bid=initial_bid
                )
            )

        return rounds

    async def _proposal_deadline(self, card):
        item = card.locator(".list-datas li").first
        text = (await item.inner_text()).strip()

        if "Em Breve" in text:
            return None

        phases = []

        matches = re.findall(
            r"(\d+[ªº] fase)\s+(\d{1,2}/\d{1,2}/\d{4})(?:\s+às\s+(\d{1,2})h)?",
            text
        )

        for name, date, hour in matches:
            if not hour:
                hour = "00"

            deadline = format_datetime(f"{date} {hour}:00", "%d/%m/%Y %H:%M")

            phases.append(
                ProposalPhase(
                    name=name,
                    deadline=deadline
                )
            )

        return phases or None

    async def _minimum_bid(self, card):
        items = card.locator(".list-datas li")
        for i in range(await items.count()):
            text = await items.nth(i).inner_text()

            if "Proposta mínima" in text:
                match = re.search(
                    r"R\$\s*([\d\.,]+)",
                    text
                )

                if match:
                    return format_money(match.group(1))

        return None

    async def _image_url(self, card):
        return await card.locator(
            ".cont-foto img"
        ).first.get_attribute("src")


class MonizDeAragaoParser(AlexandreCostaParser):
    pass


class LeiloesJaParser(AuctionParser):
    async def get_auction_cards(self, page):
        cards = page.locator(
            ".flex-leiloes article"
        )

        return [
            cards.nth(i)
            for i in range(await cards.count())
        ]

    async def _has_direct_sale(self, card):
        text = await card.locator(".absolute-tipo").inner_text()
        return "venda direta" in text.lower()

    async def _title(self, card):
        return await card.locator("h3").text_content()
        
    async def _description(self, card):
        # O card não possui um campo de descrição/endereço.
        return None

    async def _status(self, card):
        return None

    async def _rounds(self, card):
        rounds = []

        items = card.locator(".cont-datas li")
        count = await items.count()

        for i in range(count):
            item = items.nth(i)

            title = (
                await item.locator("strong")
                .inner_text()
            ).strip()

            if "leilão" not in title.lower():
                continue

            text = await item.inner_text()

            match = re.search(
                r"(\d{2}/\d{2}/\d{4}).*?(\d{2}):(\d{2})",
                text
            )

            if not match:
                continue

            end = format_datetime(
                f"{match.group(1)} {match.group(2)}:{match.group(3)}",
                "%d/%m/%Y %H:%M"
            )
            
            bid_match = re.search(
                r"R\$\s*([\d\.,]+)",
                text
            )
            initial_bid = format_money(bid_match.group(1)) if bid_match else None

            # Status
            classes = await item.get_attribute("class") or ""
            status = RoundStatus.CLOSED.value if "encerrado" in classes else RoundStatus.OPEN.value

            rounds.append(
                AuctionRound(
                    name=title,
                    end=end,
                    status=status,
                    initial_bid=initial_bid
                )
            )

        return rounds

    async def _proposal_deadline(self, card):
        item = card.locator(
            ".cont-datas li"
        ).first
        text = (await item.inner_text()).strip()


        if "breve" in text.lower():
            return None

        match = re.search(
            r"(\d{1,2})\s+de\s+([A-Za-zç]+)\s+de\s+(\d{4})",
            text,
            re.IGNORECASE
        )

        if not match:
            return None

        months = {
            "janeiro": 1,
            "fevereiro": 2,
            "março": 3,
            "marco": 3,
            "abril": 4,
            "maio": 5,
            "junho": 6,
            "julho": 7,
            "agosto": 8,
            "setembro": 9,
            "outubro": 10,
            "novembro": 11,
            "dezembro": 12,
        }

        day = int(match.group(1))
        month = months[match.group(2).lower()]
        year = int(match.group(3))

        return [
            ProposalPhase(
                name="Proposta",
                deadline=datetime(year, month, day)
            )
        ]

    async def _minimum_bid(self, card):
        # Não há valor mínimo no card de venda direta.
        return None

    async def _image_url(self, card):
        return await card.locator(
            ".cont-foto > img"
        ).get_attribute("src")


class JVLeiloesParser(AuctionParser):
    async def _has_direct_sale(self, card):
        return False

    async def _proposal_deadline(self, card):
        return None

    async def _minimum_bid(self, card):
        return None
    
    async def get_auction_cards(self, page):
        pass

    async def _title(self, card):
        pass
        
    async def _description(self, card):
        pass

    async def _status(self, card):
        pass

    async def _rounds(self, card):
        pass

    async def _image_url(self, card):
        pass


class BrameLeiloesParser(AuctionParser):
    async def get_auction_cards(self, page):
            cards = page.locator("div[id^='event-']")

            return [
                cards.nth(i)
                for i in range(await cards.count())
            ]

    async def _title(self, card):
        return (
            await card.locator(".MuiCardContent-root > div:first-child p")
            .text_content()
        ).strip()
        
    async def _description(self, card):
        return None

    async def _status(self, card):
        return None

    async def _rounds(self, card):
        rounds = []
        items = card.locator(".MuiTimeline-root li")

        for i in range(await items.count()):
            item = items.nth(i)

            text = (
                await item.locator(
                    ".MuiTimelineContent-root span"
                ).text_content()
            ).strip()

            match = re.search(
                r"(\d+ª)\s+praça:\s*encerra\s*"
                r"(\d{2}/\d{2}/\d{4})\s*-\s*"
                r"(\d{2}):(\d{2})",
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            round_name = f"{match.group(1)} Praça"

            end = format_datetime(
                f"{match.group(2)} {match.group(3)}:{match.group(4)}",
                "%d/%m/%Y %H:%M"
            )

            status = None
            dot = item.locator(".MuiTimelineDot-root")

            classes = await dot.get_attribute("class") or ""

            if "MuiTimelineDot-filled" in classes:
                status = RoundStatus.OPEN.value
            elif "MuiTimelineDot-outlined" in classes:
                status = RoundStatus.SOON.value

            rounds.append(
                AuctionRound(
                    name=round_name,
                    end=end,
                    status=status,
                )
            )

        return rounds

    async def _image_url(self, card):
        return await card.locator(
            ".MuiCardMedia-root"
        ).get_attribute("src")


class RicartParser(GustavoLeiloeiroParser):
    pass


class MauricioKronembergParser(AlexandreCostaParser):
    pass