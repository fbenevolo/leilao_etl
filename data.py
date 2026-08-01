import pandas as pd

from models import SiteConfig, Selector
from parsers import *
from navigators import *
from strategy import *


df = pd.read_excel("leiloeiros_associados.xlsx")
df["Site"] = df["Site"].str.replace(r"^http://", "https://", regex=True)

sites_list = df["Site"].to_list()
sites_list[:7]

site_template_dict = {
    "https://www.alexandrecostaleiloes.com.br/": SiteConfig(
        AlexandreCostaParser(),
        AlexandreCostaNavigator(),
        auction_navbar_selector=Selector("css", "div[class='Topo1_mnu_PrincL']"),
        show_more_selector=Selector("css", ".Anuncio1_seletores")
    ),
    "https://www.alexandroleiloeiro.com.br": SiteConfig(
        AlexandreLeiloeiroParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.analucialeiloeira.com.br": SiteConfig(
        AlexandreCostaParser(),
        AlexandreCostaNavigator()
    ),
    "https://www.andersonleiloeiro.lel.br": SiteConfig(
        AlexandreCostaParser(),
        AlexandreCostaNavigator()
    ),
    "https://www.andrealeiloeira.lel.br": SiteConfig(
        AndresRosaCostaParser(),
        AlexandreCostaNavigator(),
        auction_navbar_selector=Selector("css", "a[class='Anuncio1_seletor_linknaveg']")
    ),
    "https://www.bspleiloes.com.br": SiteConfig(
        AlexandreCostaParser(),
        AlexandreCostaNavigator(),
        show_more_selector=Selector("css", ".Anuncio1_seletores")
    ),
    "https://www.depaulaonline.com.br": SiteConfig(
        DePaulaParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.edgarcarvalholeiloeiro.com.br/": SiteConfig(
        EdgarCarvalhoParser(),
        AlexandreLeiloeiroNavigator(),
        auction_navbar_selector=Selector("css", "li.nav-leiloes a[href='/leiloes']")
    ),
    "https://fabianoayuppleiloeiro.com.br/": SiteConfig(
        DePaulaParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.portellaleiloes.com.br": SiteConfig(
        PortellaLeiloesParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.gpleilao.com.br/": SiteConfig(
        AlexandreCostaParser(),
        AlexandreCostaNavigator()
    ),
    "https://www.gustavoleiloeiro.lel.br": SiteConfig(
        GustavoLeiloeiroParser(),
        AlexandreLeiloeiroNavigator(),
    ),
    "https://www.leilaobrasil.com.br": SiteConfig(
        LeilaoBrasilParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.rymerleiloes.com.br": SiteConfig(
        RymerParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.monizdearagao.leilao.br/": SiteConfig(
        MonizDeAragaoParser(),
        AlexandreLeiloeiroNavigator()
    ),
    "https://www.leiloesja.com.br/": SiteConfig(
        LeiloesJaParser(),
        LeiloesJaNavigator(),
        auction_navbar_selector=Selector("css", "li.leiloes a[href='/agenda']")
    ),
    "https://www.jvleiloes.lel.br": SiteConfig(
        JVLeiloesParser(),
        JVLeiloesNavigator()
    ),
    "https://www.brameleiloes.com.br": SiteConfig(
        BrameLeiloesParser(),
        BrameLeiloesNavigator(),
        wait_strategy=BrameLeiloesStrategy(),
        auction_navbar_selector=Selector("css", 'a[href*="todos-eventos"]')
    ),
    "https://www.schulmannleiloes.com.br": ...,
    "https://www.maiconleiloeiro.com.br": ...,
    "https://www.marioricart.lel.br": SiteConfig(
        RicartParser(),
        RicartNavigator()
    ),
    "https://www.mklance.com.br/": SiteConfig(
        MauricioKronembergParser(),
        MauricioKronembergNavigator()
    ),
    "https://mauriciomarizleiloes.com.br/": SiteConfig(
        MauricioMunizParser(),
        MauricioMunizNavigator()
    ),
    "https://www.mauromarcello.lel.br": SiteConfig(
        MauricioMarcelloParser(),
        MauricioMarcelloNavigator()
    )
}