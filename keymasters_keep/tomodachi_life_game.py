"""
A Keymaster's Keep implementation of Tomodachi Life, created by Jack5. The following objective types are included:

- Feed specific Miis specific food
- Give specific Miis specific interiors
- Dress specific Miis in specific clothes
- Give specific Miis specific gifts
- Give specific Miis specific treasures
- Give Miis specific level up items
- Bonus objectives (time consuming)

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `tomodachi_life_weights` YAML option.

Tomodachi Life differs in various ways depending on the region it was purchased in. For this reason, it is important to set the values of `tomodachi_life_region` and `tomodachi_life_language` accurately before playing. Additionally, cheap items appear in objectives more frequently than expensive items.
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from Options import (  # pyright: ignore[reportMissingImports]
    DefaultOnToggle,
    Choice,
    OptionCounter,
    OptionList,
    Toggle,
)
from typing import Callable, Literal
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class TomodachiLifeWeights(OptionCounter):
    """
    The weights to use for Tomodachi Life objective types.
    """

    display_name: str = "Tomodachi Life Weights"
    default: dict[str, int] = {
        "any_mii_food": 1,
        "named_mii_food": 1,
        "any_mii_interior": 1,
        "named_mii_interior": 1,
        "any_mii_clothes": 1,
        "named_mii_clothes": 1,
        "any_mii_gift": 1,
        "named_mii_gift": 1,
        "any_mii_treasure": 1,
        "named_mii_treasure": 1,
        "any_mii_level_up_item": 2,
        "bonus": 12,
    }


class TomodachiLifeRegion(Choice):
    """
    The region of the copy of Tomodachi Life being played. `europe`, `united_kingdom` and `australia` are synonymous with each-other, but affect the appearance and weight of items due to differing languages and currencies.
    """

    display_name: str = "Tomodachi Life Region"
    option_north_america: int = 0
    option_europe: int = 1
    option_united_kingdom: int = 2
    option_australia: int = 3
    option_japan: int = 4
    option_korea: int = 5
    default: int = 0


class TomodachiLifeLanguage(Choice):
    """
    The preferred romanised language of Tomodachi Life objectives. Languages other than `north_america` will inherit `europe` where possible.
    """

    display_name: str = "Tomodachi Life Language"
    option_north_america: int = 0
    option_europe: int = 1
    option_japan: int = 2
    option_korea: int = 3
    default: int = 0


class TomodachiLifeSpecialCharacters(Toggle):
    """
    Whether to display the Japanese characters for Tomodachi Life items after their romanised names. Only applies if `tomodachi_life_region` is set to `japan`.
    """

    display_name: str = "Tomodachi Life Special Characters"


class TomodachiLifeSkipLockedItems(DefaultOnToggle):
    """
    Whether Tomodachi Life objectives involving items should include a notice that allows them to be skipped if their items are not unlocked or owned by the player, depending on the item type.
    """

    display_name: str = "Tomodachi Life Skip Locked Items"


class TomodachiLifeTrash(Toggle):
    """
    Whether to allow trash items (e.g. Mouldy bread) to appear as part of Tomodachi Life objectives.
    """

    display_name: str = "Tomodachi Life Trash"


class TomodachiLifeMaleMiis(OptionList):
    """
    The list of male Miis living in the given copy of Tomodachi Life, to use for objectives that require a specific male Mii. If empty, specific male Mii objectives will not appear. Defaults to ["a male Mii"].
    """

    display_name: str = "Tomodachi Life Male Miis"
    default: list[str] = ["a male Mii"]


class TomodachiLifeFemaleMiis(OptionList):
    """
    The list of female Miis living in the given copy of Tomodachi Life, to use for objectives that require a specific female Mii. If empty, specific female Mii objectives will not appear. Defaults to ["a female Mii"].
    """

    display_name: str = "Tomodachi Life Female Miis"
    default: list[str] = ["a female Mii"]


@dataclass
class TomodachiLifeArchipelagoOptions:
    tomodachi_life_weights: TomodachiLifeWeights
    tomodachi_life_region: TomodachiLifeRegion
    tomodachi_life_language: TomodachiLifeLanguage
    tomodachi_life_special_characters: TomodachiLifeSpecialCharacters
    tomodachi_life_skip_locked_items: TomodachiLifeSkipLockedItems
    tomodachi_life_trash: TomodachiLifeTrash
    tomodachi_life_male_miis: TomodachiLifeMaleMiis
    tomodachi_life_female_miis: TomodachiLifeFemaleMiis


@dataclass
class TLName:
    na: str
    other: dict[Literal["EU-en", "JP-en", "JP", "KR-en"], str]


@dataclass
class TLCost:
    """
    The cost of a Tomodachi Life item in each currency.

    Args:
        usd (float | None, optional): The cost in American dollars. Defaults to None.
        eur (float | None, optional): The cost in Euros. Defaults to None.
        gbp (float | None, optional): The cost in British pounds. Defaults to None.
        aud (float | None, optional): The cost in Australian dollars. Defaults to None.
        jpy (int | None, optional): The cost in Japanese yen. Defaults to None.
        krw (int | None, optional): The cost in South Korean won. Defaults to None.
        dollars (float | None, optional): The cost in dollars. This is shared between `usd`, `eur`, `gbp` and `aud` if they are not set. Defaults to None.
        scale (bool, optional): Whether `jpy` and `krw` should be 100 and 1000 times `dollars` respectively. Defaults to False.
    """

    usd: float | None = None
    eur: float | None = None
    gbp: float | None = None
    aud: float | None = None
    jpy: int | None = None
    krw: int | None = None
    dollars: float | None = None
    scale: bool = False


@dataclass
class TLItem:
    """
    An item from Tomodachi Life.

    Args:
        name (str | TLName): The name of the item.
        cost (float | int | TLCost, optional): The cost of the item, which can specify what regions the item is available in. Defaults to 0.
        region (Literal["NA", "EU", "JP", "KR"] | None, optional): The region in which the item is available, or None for all regions. Defaults to None.
        trash (bool, optional): Whether the item is trash. Defaults to False.
    """

    name: str | TLName
    cost: float | int | TLCost = 0
    region: Literal["NA", "EU", "JP", "KR"] | None = None
    trash: bool = False


class TomodachiLifeGame(Game):
    """
    Tomodachi Life is a social simulation game that centers on the everyday lives of Mii characters who live on a remote island. While constructing Miis, the player assigns them a distinct personality by selecting various temperament attributes. The game follows the day-to-day interactions of Mii characters residing on an island as they build relationships and solve problems, all of which is overseen by the player. By continuously adding Miis and completing miscellaneous objectives, additional buildings, shops, and attractions throughout the island become unlocked.

    Tomodachi Life is open-ended, having no clear end condition. Instead, the game's primary objective is for the player to continuously maintain each of their Miis' happiness, which is indicated by a personalised meter. At random intervals, Miis will notify the player of a particular problem they have. These issues range from requesting food or clothing, soliciting relationship guidance, and asking to compete in various short minigames. Appeasing a Mii increases their happiness gauge, which awards the player with in-game currency usable for purchasing items.
    """

    name: str = "Tomodachi Life"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms._3DS
    is_adult_only_or_unrated: bool = False
    options_cls: type[TomodachiLifeArchipelagoOptions] = TomodachiLifeArchipelagoOptions

    @cached_property
    def foods_mains(self) -> list[TLItem]:
        """
        The list of main foods in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Food/List_of_Main_Foods_in_Tomodachi_Life.

        Returns:
            list[TLItem]: The list of main foods.
        """
        return [
            TLItem("Barbecue", 15.00, "NA"),
            TLItem("Buffalo wings", 8.60, "NA"),
            TLItem("Cheeseburger", 6.50, "NA"),
            TLItem("Chicken pot pie", 7.80, "NA"),
            TLItem("Creamy stew", 6.80, "NA"),
            TLItem("Filet mignon", 50.00, "NA"),
            TLItem("Fish cakes", 7.80, "NA"),
            TLItem("Fish sticks", 8.20, "NA"),
            TLItem("Fried chicken", 4.50, "NA"),
            TLItem("Gratin", 9.80, "NA"),
            TLItem("Gyro", 5.90, "NA"),
            TLItem("Herring", 4.50, "NA"),
            TLItem("Lasagna", 6.50, "NA"),
            TLItem("Lobster", 16.00, "NA"),
            TLItem("Loco moco", 7.80, "NA"),
            TLItem("Meatballs", 5.00, "NA"),
            TLItem("Nachos", 7.50, "NA"),
            TLItem("Paella", 8.80, "NA"),
            TLItem("Panini", 5.50, "NA"),
            TLItem("Pasta pesto", 7.30, "NA"),
            TLItem("Peking duck", 30.00, "NA"),
            TLItem("Pork cutlet", 8.00, "NA"),
            TLItem("Pot-au-feu", 7.00, "NA"),
            TLItem("Ramen", 9.90, "NA"),
            TLItem("Roast beef", 15.00, "NA"),
            TLItem("Roast chicken", 20.00, "NA"),
            TLItem("Roast turkey", 33.00, "NA"),
            TLItem("Ruined meal", 0.20, "NA", trash=True),
            TLItem("Salisbury steak", 9.90, "NA"),
            TLItem("Salmon meunière", 11.00, "NA"),
            TLItem("Sashimi", 12.80, "NA"),
            TLItem("Schnitzel", 13.00, "NA"),
            TLItem("Space food", 20.00, "NA"),
            TLItem("Spaghetti", 7.80, "NA"),
            TLItem("Spaghetti pepperoncino", 7.80, "NA"),
            TLItem("Squid-ink spaghetti", 7.80, "NA"),
            TLItem("Steak", 15.90, "NA"),
            TLItem("Stewed beef", 8.80, "NA"),
            TLItem("Stuffed cabbage roll", 7.00, "NA"),
            TLItem("Sushi", 19.90, "NA"),
            TLItem("Sweet-and-sour pork", 7.80, "NA"),
            TLItem("Tempura", 8.80, "NA"),
            TLItem("Yakisoba", 6.90, "NA"),
            TLItem("Bacalao", TLCost(eur=10.90, gbp=9.90, aud=12.90), "EU"),
            TLItem("Barbecued meat", TLCost(eur=11.90, gbp=9.90, aud=30.00), "EU"),
            TLItem("Beef bourguignon", TLCost(eur=10.90, gbp=9.00, aud=13.40), "EU"),
            TLItem("Borscht", TLCost(eur=6.90, gbp=5.50, aud=11.00), "EU"),
            TLItem("Cheeseburger", TLCost(eur=7.50, gbp=6.00, aud=8.90), "EU"),
            TLItem(
                "Chicken tikka masala", TLCost(eur=11.90, gbp=9.90, aud=14.90), "EU"
            ),
            TLItem("Chilli con carne", TLCost(eur=8.90, gbp=7.00, aud=10.90), "EU"),
            TLItem("Couscous", TLCost(eur=11.90, gbp=9.90, aud=13.40), "EU"),
            TLItem("Creamy stew", TLCost(eur=9.00, gbp=8.00, aud=9.90), "EU"),
            TLItem("English breakfast", TLCost(eur=7.00, gbp=6.00, aud=8.90), "EU"),
            TLItem("Fish and chips", TLCost(eur=12.95, gbp=8.90, aud=10.10), "EU"),
            TLItem("Fishcakes", TLCost(eur=7.20, gbp=6.50, aud=8.90), "EU"),
            TLItem("Fried chicken", TLCost(eur=5.90, gbp=6.00, aud=6.90), "EU"),
            TLItem("Gratin", TLCost(eur=8.90, gbp=7.00, aud=9.90), "EU"),
            TLItem("Grilled mackerel", TLCost(eur=11.90, gbp=9.90, aud=9.70), "EU"),
            TLItem("Doner kebab", TLCost(eur=6.00, gbp=5.50, aud=5.70), "EU"),
            TLItem("Hake fillet", TLCost(eur=7.90, gbp=6.50, aud=10.90), "EU"),
            TLItem("Herring", TLCost(eur=6.10, gbp=5.50, aud=5.70), "EU"),
            TLItem("Lasagne", TLCost(eur=11.00, gbp=8.90, aud=8.90), "EU"),
            TLItem("Meatballs", TLCost(eur=10.90, gbp=8.90, aud=10.50), "EU"),
            TLItem(
                "Melanzane parmigiana", TLCost(eur=12.90, gbp=9.00, aud=13.90), "EU"
            ),
            TLItem("Paella", TLCost(eur=13.00, gbp=12.00, aud=12.20), "EU"),
            TLItem("Panini", TLCost(eur=6.20, gbp=5.50, aud=5.70), "EU"),
            TLItem("Pasta pesto", TLCost(eur=11.00, gbp=9.00, aud=12.90), "EU"),
            TLItem("Peking duck", TLCost(eur=13.90, gbp=12.00, aud=14.90), "EU"),
            TLItem("Pork cutlet", TLCost(eur=9.90, gbp=7.90, aud=10.90), "EU"),
            TLItem("Pork pie", TLCost(eur=4.90, gbp=4.50, aud=4.90), "EU"),
            TLItem("Pot-au-feu", TLCost(eur=13.90, gbp=11.90, aud=13.90), "EU"),
            TLItem("Ratatouille", TLCost(eur=8.90, gbp=6.90, aud=13.00), "EU"),
            TLItem("Roast beef", TLCost(eur=12.50, gbp=10.00, aud=13.90), "EU"),
            TLItem("Roast chicken", TLCost(eur=10.90, gbp=9.90, aud=13.90), "EU"),
            TLItem("Roast duck", TLCost(gbp=15.00, aud=35.00), "EU"),
            TLItem("Roast lamb", TLCost(eur=8.90, gbp=7.50, aud=40.00), "EU"),
            TLItem("Roast turkey", TLCost(eur=10.50, aud=13.00), "EU"),
            TLItem("Rollmop herrings", TLCost(eur=7.90, gbp=6.00, aud=8.90), "EU"),
            TLItem(
                "Ruined meal", TLCost(eur=0.20, gbp=0.10, aud=0.10), "EU", trash=True
            ),
            TLItem("Rissole", TLCost(eur=9.90, gbp=8.50, aud=10.90), "EU"),
            TLItem("Salmon meunière", TLCost(eur=13.00, gbp=11.00, aud=30.00), "EU"),
            TLItem("Saltimbocca", TLCost(eur=13.90, gbp=11.90, aud=20.40), "EU"),
            TLItem("Schnitzel", TLCost(eur=8.90, gbp=7.50, aud=9.90), "EU"),
            TLItem("Space food", TLCost(eur=20.00, gbp=20.00, aud=20.00), "EU"),
            TLItem("Spaghetti bolognese", TLCost(eur=13.90, gbp=9.90, aud=10.50), "EU"),
            TLItem("Spaghetti carbonara", TLCost(eur=11.00, gbp=8.90, aud=12.20), "EU"),
            TLItem(
                "Spaghetti peperoncino", TLCost(eur=13.50, gbp=8.90, aud=11.30), "EU"
            ),
            TLItem(
                "Squid-ink spaghetti", TLCost(eur=16.90, gbp=10.90, aud=13.00), "EU"
            ),
            TLItem("Steak", TLCost(eur=15.90, gbp=13.90, aud=30.00), "EU"),
            TLItem("Stewed beef", TLCost(eur=11.50, gbp=9.90, aud=13.40), "EU"),
            TLItem("Stuffed cabbage roll", TLCost(eur=9.90, gbp=8.00, aud=9.90), "EU"),
            TLItem(
                TLName(
                    "Salt-grilled sweetfish",
                    {"JP-en": "Ayu no shioyaki", "JP": "鮎の塩焼き"},
                ),
                450,
                "JP",
            ),
            TLItem(
                TLName("Barbecue", {"JP-en": "Yakiniku", "JP": "焼き肉"}), 1300, "JP"
            ),
            TLItem(
                TLName("Beef over rice", {"JP-en": "Gyuudon", "JP": "牛丼"}), 600, "JP"
            ),
            TLItem(
                TLName("Chanko hotpot", {"JP-en": "Chankonabe", "JP": "ちゃんこ鍋"}),
                1580,
                "JP",
            ),
            TLItem(
                TLName("Egg custard", {"JP-en": "Chawanmushi", "JP": "茶碗蒸し"}),
                500,
                "JP",
            ),
            TLItem("Hamburger", 280, "JP"),
            TLItem(
                TLName("Fish stick", {"JP-en": "Chikuwa", "JP": "ちくわ"}), 100, "JP"
            ),
            TLItem(
                TLName(
                    "Chirashi sushi", {"JP-en": "Chirashizushi", "JP": "ちらし寿司"}
                ),
                600,
                "JP",
            ),
            TLItem("Creamy stew", 680, "JP"),
            TLItem(
                TLName("Green soybeans", {"JP-en": "Edamame", "JP": "枝豆"}), 300, "JP"
            ),
            TLItem(
                TLName(
                    "Lucky direction sushi roll", {"JP-en": "Ehoumaki", "JP": "恵方巻"}
                ),
                700,
                "JP",
            ),
            TLItem("Fried chicken", 450, "JP"),
            TLItem(
                TLName("Blowfish sashimi", {"JP-en": "Fugusashi", "JP": "ふぐ刺し"}),
                2900,
                "JP",
            ),
            TLItem(
                TLName("Lucky beans", {"JP-en": "Fukumame", "JP": "福豆"}), 400, "JP"
            ),
            TLItem(
                TLName("School lunch", {"JP-en": "Gakkokyuushoku", "JP": "学校給食"}),
                400,
                "JP",
            ),
            TLItem(
                TLName("Bitter melon", {"JP-en": "Go-ya", "JP": "ゴーヤ"}), 150, "JP"
            ),
            TLItem("Gratin", 980, "JP"),
            TLItem(
                TLName(
                    "Salt-grilled saury",
                    {"JP-en": "Sanma no shioyaki", "JP": "秋刀魚の塩焼き"},
                ),
                480,
                "JP",
            ),
            TLItem(TLName("Salmon roe", {"JP-en": "Ikura", "JP": "いくら"}), 980, "JP"),
            TLItem(TLName("Inarizushi", {"JP": "いなり寿司"}), 150, "JP"),
            TLItem(
                TLName("Sake lees soup", {"JP-en": "Kasujiru", "JP": "かす汁"}),
                250,
                "JP",
            ),
            TLItem(
                TLName("Breaded pork over rice", {"JP-en": "Katsudon", "JP": "カツ丼"}),
                680,
                "JP",
            ),
            TLItem(TLName("Kitsuneudon", {"JP": "きつねうどん"}), 650, "JP"),
            TLItem(
                TLName(
                    "Convenience store meal",
                    {"JP-en": "Konbini bento", "JP": "コンビニ弁当"},
                ),
                500,
                "JP",
            ),
            TLItem(
                TLName("Konjac", {"JP-en": "Konnyaku", "JP": "こんにゃく"}), 100, "JP"
            ),
            TLItem("Lasagna", 650, "JP"),
            TLItem(TLName("Liver", {"JP-en": "Rebaa", "JP": "レバー"}), 480, "JP"),
            TLItem(TLName("Matsutake", {"JP": "まつたけ"}), 7800, "JP"),
            TLItem("Meatballs", 500, "JP"),
            TLItem(
                TLName("Cod roe", {"JP-en": "Mentaiko", "JP": "めんたいこ"}), 780, "JP"
            ),
            TLItem(
                TLName("Miso soup", {"JP-en": "Misoshiru", "JP": "味噌汁"}), 280, "JP"
            ),
            TLItem("Monjayaki", 620, "JP"),
            TLItem("Myouga", 100, "JP"),
            TLItem("Nattou", 100, "JP"),
            TLItem("Nekomanma", 170, "JP"),
            TLItem("Ochazuke", 480, "JP"),
            TLItem("Oden", 300, "JP"),
            TLItem("Okayu", 150, "JP"),
            TLItem("Okonomiyaki", 780, "JP"),
            TLItem("Omochi", 150, "JP"),
            TLItem("Onigiri", 110, "JP"),
            TLItem("Osechi", 10000, "JP"),
            TLItem("Oyakodon", 600, "JP"),
            TLItem("Ozouni", 330, "JP"),
            TLItem("Paella", 880, "JP"),
            TLItem("Peking Duck", 5000, "JP"),
            TLItem("Pot-au-fu", 700, "JP"),
            TLItem("Ramen", 680, "JP"),
            TLItem("Roast Beef", 1500, "JP"),
            TLItem("Roast Turkey", 3300, "JP"),
            TLItem("Ruined meal", 20, "JP", trash=True),
            TLItem("Salmon meunière", 750, "JP"),
            TLItem("Sashimi", 1280, "JP"),
            TLItem("Sekihan", 300, "JP"),
            TLItem("Shrimp Fried Rice", 700, "JP"),
            TLItem("Soumen", 670, "JP"),
            TLItem("Space food", 2000, "JP"),
            TLItem("Spaghetti", 780, "JP"),
            TLItem("Spaghetti carbonara", 880, "JP"),
            TLItem("Spaghetti peperoncino", 780, "JP"),
            TLItem("Squid-ink spaghetti", 780, "JP"),
            TLItem("Steak", 1980, "JP"),
            TLItem("Stewed beef", 880, "JP"),
            TLItem("Stuffed cabbage roll", 700, "JP"),
            TLItem("Sukiyaki", 1780, "JP"),
            TLItem("Surume", 200, "JP"),
            TLItem("Sushi", 1580, "JP"),
            TLItem("Sweet-and-sour pork", 780, "JP"),
            TLItem("Tai no Ikizukuri", 3800, "JP"),
            TLItem("Takoyaki", 300, "JP"),
            TLItem("Tamagoyaki", 150, "JP"),
            TLItem("Tempura", 880, "JP"),
            TLItem("Tendon", 850, "JP"),
            TLItem("Turban shell", 650, "JP"),
            TLItem("Umeboshi", 100, "JP"),
            TLItem("Unajyuu", 2800, "JP"),
            TLItem("Urchin", 1000, "JP"),
            TLItem("Yakisoba", 400, "JP"),
            TLItem("Zarusoba", 600, "JP"),
            TLItem("Aehobak", 4500, "KR"),
            TLItem("Barbecue", 13000, "KR"),
            TLItem("Beef Rice Bowl", 6000, "KR"),
            TLItem("Budae jjigae", 6500, "KR"),
            TLItem("Buffalo wings", 8000, "KR"),
            TLItem("Chankonabe", 15000, "KR"),
            TLItem("Cheeseburger", 3500, "KR"),
            TLItem("Cheonyang chili pepper", 500, "KR"),
            TLItem("Chikuwa", 1000, "KR"),
            TLItem("Cucumber Sobagi", 4000, "KR"),
            TLItem("Daechang", 13000, "KR"),
            TLItem("Doenjang-jjigae", 5000, "KR"),
            TLItem("Dubu kimchi", 12000, "KR"),
            TLItem("Ehoumaki", 2500, "KR"),
            TLItem("Flesh", 15000, "KR"),
            TLItem("Fried chicken", 11000, "KR"),
            TLItem("Gamja-tang", 22000, "KR"),
            TLItem("Gim gui", 2000, "KR"),
            TLItem("Ginseng", 50000, "KR"),
            TLItem("Gratin", 9000, "KR"),
            TLItem("Grilled Cutlassfish", 4000, "KR"),
            TLItem("Gun Mandu", 4000, "KR"),
            TLItem("Gyeran-jjim", 3000, "KR"),
            TLItem("Gyro", 6000, "KR"),
            TLItem("Inari Sushi", 1500, "KR"),
            TLItem("Jajangmyeon", 4500, "KR"),
            TLItem("Janchi-guksu", 3500, "KR"),
            TLItem("Japchae", 5000, "KR"),
            TLItem("Jeonbok-juk", 8000, "KR"),
            TLItem("Katsudon", 7000, "KR"),
            TLItem("Kimchi fried rice", 6000, "KR"),
            TLItem("Kimchi-buchimgae", 8000, "KR"),
            TLItem("Kimchi-jjigae", 5000, "KR"),
            TLItem("Kkakdugi", 2500, "KR"),
            TLItem("Kitsuneudon", 6500, "KR"),
            TLItem("Gochujang", 1500, "KR"),
            TLItem("Lasagna", 8000, "KR"),
            TLItem("Lobster", 30000, "KR"),
            TLItem("Matsutake", 35000, "KR"),
            TLItem("Mentaiko", 5000, "KR"),
            TLItem("Miyeok-guk", 5000, "KR"),
            TLItem("Nachos", 4500, "KR"),
            TLItem("Naengmyeon", 6000, "KR"),
            TLItem("Namul", 3000, "KR"),
            TLItem("Napa cabbage", 2000, "KR"),
            TLItem("Nattou", 2500, "KR"),
            TLItem("Oden Soup", 10000, "KR"),
            TLItem("Paella", 9000, "KR"),
            TLItem("Panini", 5500, "KR"),
            TLItem("Pasta pesto", 9000, "KR"),
            TLItem("Peking duck", 30000, "KR"),
            TLItem("Pickled perilla leaves", 3000, "KR"),
            TLItem("Pot-au-fu", 7000, "KR"),
            TLItem("Ramen", 9000, "KR"),
            TLItem("Roast beef", 15000, "KR"),
            TLItem("Roast chicken", 20000, "KR"),
            TLItem("Roast turkey", 33000, "KR"),
            TLItem("Ruined meal", 200, "KR", trash=True),
            TLItem(TLName("Salisbury steak", {"EU-en": "Rissole"}), 11000, "KR"),
            TLItem("Salmon meunière", 10000, "KR"),
            TLItem("Samgyeopsal", 8000, "KR"),
            TLItem("Samgye-tang", 9000, "KR"),
            TLItem("Sashimi", 20000, "KR"),
            TLItem("Sekihan", 3000, "KR"),
            TLItem("Seolleongtang", 6000, "KR"),
            TLItem("Shrimp Fried Rice", 7000, "KR"),
            TLItem("Soy crab", 19000, "KR"),
            TLItem("Space food", 20000, "KR"),
            TLItem("Spaghetti", 9000, "KR"),
            TLItem("Spaghetti carbonara", 9000, "KR"),
            TLItem("Spaghetti peperoncino", 9000, "KR"),
            TLItem("Squid-ink spaghetti", 10000, "KR"),
            TLItem("Steak", 23000, "KR"),
            TLItem("Sundae", 3000, "KR"),
            TLItem("Sundubu-jjigae", 6000, "KR"),
            TLItem("Surume", 2000, "KR"),
            TLItem("Sushi", 15000, "KR"),
            TLItem("Takoyaki", 3000, "KR"),
            TLItem("Tamagoyaki", 1500, "KR"),
            TLItem("Tangsuyuk", 11000, "KR"),
            TLItem("Tempura", 5000, "KR"),
            TLItem("Tendon", 8500, "KR"),
            TLItem("Tteok-bokki", 3000, "KR"),
            TLItem("Tteokguk", 6000, "KR"),
            TLItem("Turban shell", 6500, "KR"),
            TLItem("Unajyuu", 15000, "KR"),
            TLItem("Urchin", 10000, "KR"),
            TLItem("Yakisoba", 8000, "KR"),
            TLItem("Young Gye Baek Sook", 14000, "KR"),
            TLItem("Yukhoe", 11000, "KR"),
            TLItem("Zarusoba", 6000, "KR"),
        ]

    @cached_property
    def foods_sides(self) -> list[TLItem]:
        """
        The list of side foods in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Food/List_of_Side_Foods_in_Tomodachi_Life.

        Returns:
            list[TLItem]: The list of side foods.
        """
        return [
            TLItem("Avocado", 1.00, "NA"),
            TLItem("Bacon", 2.50, "NA"),
            TLItem("Baked beans", 3.50, "NA"),
            TLItem("Baked potato", 5.00, "NA"),
            TLItem("Blue cheese", 3.00, "NA"),
            TLItem("Broccoli", 1.00, "NA"),
            TLItem("Brussels sprouts", 1.00, "NA"),
            TLItem(TLName("Buttered potato", {"EU-en": "Baked potato"}), 3.80, "NA"),
            TLItem(TLName("Calamari", {"EU-en": "Squid rings"}), 4.80, "NA"),
            TLItem("Caviar", 65.00, "NA"),
            TLItem("Celery", 1.00, "NA"),
            TLItem("Cheese", 2.00, "NA"),
            TLItem("Chicken noodle soup", 4.50, "NA"),
            TLItem("Chili prawns", 6.40, "NA"),
            TLItem("Clam chowder", 6.00, "NA"),
            TLItem("Coleslaw", 1.20, "NA"),
            TLItem("Cooked eggplant", 3.50, "NA"),
            TLItem("Corn dog", 0.99),
            TLItem("Corn flakes", 3.00, "NA"),
            TLItem("Corn on the cob", 2.00, "NA"),
            TLItem("Crab", 60.00, "NA"),
            TLItem("Drumstick", 3.50, "NA"),
            TLItem("Escargot", 12.00, "NA"),
            TLItem("French fries", 2.80, "NA"),
            TLItem("Fresh spring rolls", 5.90, "NA"),
            TLItem("Fried egg", 1.70, "NA"),
            TLItem("Fried rice", 4.80, "NA"),
            TLItem("Fried spring rolls", 6.30, "NA"),
            TLItem("Fried tofu", 2.50, "NA"),
            TLItem("Garlic", 0.80, "NA"),
            TLItem("Green pepper", 0.80, "NA"),
            TLItem("Grilled cheese", 2.00, "NA"),
            TLItem("Grits", 5.00, "NA"),
            TLItem("Habanero", 1.00, "NA"),
            TLItem("Hard-boiled egg", 0.40, "NA"),
            TLItem("Hash browns", 1.50, "NA"),
            TLItem("Hot dog", 2.80, "NA"),
            TLItem("Instant noodles", 1.90, "NA"),
            TLItem("Kimchi", 2.80, "NA"),
            TLItem("Macaroni and cheese", 5.80, "NA"),
            TLItem("Mashed potatoes", 3.50, "NA"),
            TLItem("Meat-and-potato stew", 6.00, "NA"),
            TLItem("Moldy bread", 0.20, "NA", trash=True),
            TLItem("Mushroom", 1.30, "NA"),
            TLItem("Oatmeal", 2.50, "NA"),
            TLItem("Octopus", 8.80, "NA"),
            TLItem("Olives", 3.00, "NA"),
            TLItem("Onion gratin soup", 4.10, "NA"),
            TLItem("Onion rings", 3.50, "NA"),
            TLItem("PB&J", 2.00, "NA"),
            TLItem(TLName("Pickles", {"EU-en": "Gherkins"}), 3.00, "NA"),
            TLItem("Pizza", 0.99),
            TLItem("Polenta", 5.80, "NA"),
            TLItem("Popcorn shrimp", 4.00, "NA"),
            TLItem("Pork bun", 2.00, "NA"),
            TLItem("Porridge", 3.00, "NA"),
            TLItem("Pot stickers", 5.00, "NA"),
            TLItem("Prawn salad", 7.50, "NA"),
            TLItem("Pretzel", 1.30, "NA"),
            TLItem("Prosciutto", 6.90, "NA"),
            TLItem("Quiche", 5.50, "NA"),
            TLItem("Ravioli", 6.40, "NA"),
            TLItem("Raw oyster", 1.50, "NA"),
            TLItem("Red chili pepper", 0.50, "NA"),
            TLItem("Rice", 2.00, "NA"),
            TLItem("Risotto", 7.80, "NA"),
            TLItem("Salad", 5.60, "NA"),
            TLItem("Salami", 3.90, "NA"),
            TLItem("Sandwich", 5.50, "NA"),
            TLItem("Sardines", 1.40, "NA"),
            TLItem("Sausage", 2.00, "NA"),
            TLItem("Smoked salmon", 9.00, "NA"),
            TLItem("Spanish omelet", 4.60, "NA"),
            TLItem("Split-pea soup", 3.50, "NA"),
            TLItem("String cheese", 0.75),
            TLItem("Stuffing", 6.70, "NA"),
            TLItem("Tacos", 4.80, "NA"),
            TLItem("Tomato", 0.90, "NA"),
            TLItem("Tomato soup", 3.80, "NA"),
            TLItem("Truffle", 60.00, "NA"),
            TLItem("Veggie burger", 5.00, "NA"),
            TLItem("White bread", 0.30, "NA"),
            TLItem("Yakitori", 3.50, "NA"),
            TLItem("Avocado", TLCost(eur=1.30, gbp=1.00, aud=1.90), "EU"),
            TLItem("Bacon", TLCost(eur=1.10, gbp=0.80, aud=3.60), "EU"),
            TLItem("Baguette", TLCost(eur=0.80, gbp=0.50, aud=1.50), "EU"),
            TLItem("Beans on toast", TLCost(eur=1.50, gbp=1.20, aud=1.60), "EU"),
            TLItem("Blue cheese", TLCost(eur=3.90, gbp=3.90, aud=4.00), "EU"),
            TLItem("Broccoli", TLCost(eur=0.70, gbp=0.70, aud=0.60), "EU"),
            TLItem("Brussels sprouts", TLCost(eur=0.90, gbp=0.90, aud=1.60), "EU"),
            TLItem("Baked potato", TLCost(eur=4.00, gbp=4.00, aud=3.20), "EU"),
            TLItem("Squid rings", TLCost(eur=4.50, gbp=4.50, aud=5.70), "EU"),
            TLItem("Caviar", TLCost(eur=120.00, gbp=120.00, aud=150.00), "EU"),
            TLItem("Celery", TLCost(eur=0.90, gbp=0.90, aud=0.80), "EU"),
            TLItem("Cheese", TLCost(eur=3.00, gbp=3.00, aud=3.60), "EU"),
            TLItem("Chili prawns", TLCost(eur=12.00, gbp=12.00, aud=12.20), "EU"),
            TLItem("Cooked aubergine", TLCost(eur=5.90, gbp=5.90, aud=5.70), "EU"),
            TLItem("Corn flakes", TLCost(eur=1.70, gbp=1.50, aud=3.20), "EU"),
            TLItem("Cornish pasty", TLCost(eur=3.10, gbp=2.90, aud=3.90), "EU"),
            TLItem("Corn on the cob", TLCost(eur=0.80, gbp=0.80, aud=0.80), "EU"),
            TLItem("Courgette", TLCost(gbp=5.90, aud=10.50), "EU"),
            TLItem("Croquettes", TLCost(eur=6.90, gbp=5.50, aud=8.40), "EU"),
            TLItem("Drumstick", TLCost(eur=2.00, gbp=2.00, aud=3.20), "EU"),
            TLItem("Escargot", TLCost(eur=12.00, gbp=12.00, aud=12.20), "EU"),
            TLItem("French fries", TLCost(eur=2.50, gbp=2.50, aud=3.20), "EU"),
            TLItem("Fried egg", TLCost(eur=0.80, gbp=0.80, aud=4.10), "EU"),
            TLItem(
                TLName("Spring rolls", {"EU-en": "Fried spring rolls"}),
                TLCost(eur=5.90, gbp=3.90, aud=4.90),
                "EU",
            ),
            TLItem("Garlic", TLCost(eur=0.90, aud=1.20), "EU"),
            TLItem("Gazpacho", TLCost(eur=5.90, gbp=6.00, aud=7.30), "EU"),
            TLItem("Gnocchi", TLCost(gbp=6.50, aud=6.50), "EU"),
            TLItem("Grated carrot", TLCost(eur=1.00, gbp=1.50, aud=2.90), "EU"),
            TLItem("Greek Salad", TLCost(eur=6.50, gbp=5.50, aud=7.40), "EU"),
            TLItem("Green pepper", TLCost(eur=0.80, gbp=0.80, aud=0.80), "EU"),
            TLItem("Ham and asparagus", TLCost(eur=2.50, gbp=5.50, aud=7.40), "EU"),
            TLItem("Hard-boiled egg", TLCost(eur=0.20, gbp=0.20, aud=0.40), "EU"),
            TLItem("Hot dog", TLCost(eur=2.50, gbp=2.50, aud=3.40), "EU"),
            TLItem("Hummus", TLCost(eur=5.50, gbp=4.90, aud=5.70), "EU"),
            TLItem("Iberian ham", TLCost(eur=12.90, gbp=10.90, aud=12.90), "EU"),
            TLItem("Instant noodles", TLCost(eur=1.20, gbp=1.20, aud=1.60), "EU"),
            TLItem("Mashed potatoes", TLCost(eur=2.50, gbp=2.50, aud=4.40), "EU"),
            TLItem("Meat and potato stew", TLCost(eur=11.00, gbp=8.90, aud=9.70), "EU"),
            TLItem("Minestrone", TLCost(eur=8.00, gbp=6.50, aud=7.30), "EU"),
            TLItem("Mouldy bread", TLCost(eur=0.10, aud=0.10), "EU", trash=True),
            TLItem("Mozzarella", TLCost(eur=2.50, gbp=3.00, aud=3.70), "EU"),
            TLItem("Mozzarella salad", TLCost(eur=8.90, gbp=7.00, aud=9.90), "EU"),
            TLItem("Mushroom", TLCost(eur=0.20, gbp=0.20, aud=0.20), "EU"),
            TLItem("Mussels", TLCost(eur=5.00, gbp=7.50, aud=8.10), "EU"),
            TLItem("Octopus", TLCost(eur=6.90, gbp=6.90, aud=6.50), "EU"),
            TLItem("Olives", TLCost(eur=1.50, gbp=1.50, aud=2.90), "EU"),
            TLItem("Olivier salad", TLCost(eur=6.50, gbp=6.50, aud=8.90), "EU"),
            TLItem("Omelette", TLCost(gbp=7.00, aud=8.90), "EU"),
            TLItem("Onion gratin soup", TLCost(eur=1.50, gbp=5.90, aud=6.50), "EU"),
            TLItem("Gherkins", TLCost(eur=2.00, gbp=2.00, aud=3.70), "EU"),
            TLItem("Pizza", TLCost(eur=2.00, gbp=2.00, aud=3.20), "EU"),
            TLItem("Polenta", TLCost(eur=5.00, gbp=5.00, aud=6.90), "EU"),
            TLItem("Porridge", TLCost(eur=2.50, gbp=2.50, aud=4.40), "EU"),
            TLItem("Prawn pilaf", TLCost(eur=9.50, gbp=9.90, aud=11.90), "EU"),
            TLItem("Prawn salad", TLCost(eur=6.00, gbp=6.00, aud=8.90), "EU"),
            TLItem("Pretzel", TLCost(eur=1.80, gbp=1.80, aud=2.40), "EU"),
            TLItem("Parma ham", TLCost(eur=3.00, gbp=3.00, aud=5.90), "EU"),
            TLItem("Quiche", TLCost(eur=6.00, gbp=6.00, aud=6.50), "EU"),
            TLItem("Ravioli", TLCost(eur=5.90, gbp=5.90, aud=7.90), "EU"),
            TLItem("Raw oyster", TLCost(eur=2.00, gbp=2.00, aud=2.40), "EU"),
            TLItem("Red chilli pepper", TLCost(gbp=0.40, aud=0.40), "EU"),
            TLItem("Rice", TLCost(eur=2.00, gbp=2.00, aud=3.20), "EU"),
            TLItem("Risotto", TLCost(eur=8.00, gbp=8.00, aud=12.20), "EU"),
            TLItem("Salad", TLCost(eur=5.00, gbp=6.50, aud=6.50), "EU"),
            TLItem("Salami", TLCost(eur=3.00, aud=4.10), "EU"),
            TLItem("Sandwich", TLCost(eur=2.50, gbp=2.50, aud=4.10), "EU"),
            TLItem(
                TLName("Sardines", {"EU-en": "Fried sardines"}),
                TLCost(eur=5.90, aud=5.70),
                "EU",
            ),
            TLItem("Sauerkraut", TLCost(eur=4.90, gbp=3.50, aud=4.90), "EU"),
            TLItem("Sausage", TLCost(eur=2.30, aud=1.60), "EU"),
            TLItem("Smoked salmon", TLCost(eur=6.50, gbp=6.50, aud=8.90), "EU"),
            TLItem("Souffle", TLCost(eur=6.90, gbp=5.50, aud=7.40), "EU"),
            TLItem("Tortilla", TLCost(eur=5.50, aud=6.50), "EU"),
            TLItem("Spinach", TLCost(eur=2.50, gbp=2.00, aud=4.50), "EU"),
            TLItem("Tacos", TLCost(eur=5.00, gbp=5.00, aud=7.90), "EU"),
            TLItem("Tapas", TLCost(eur=5.00, gbp=4.50, aud=6.10), "EU"),
            TLItem("Tofu", TLCost(eur=4.00, gbp=2.90, aud=2.40), "EU"),
            TLItem("Tomato", TLCost(gbp=0.20, aud=0.20), "EU"),
            TLItem("Truffle", TLCost(eur=70.00, gbp=60.00, aud=100.00), "EU"),
            TLItem("White bread", TLCost(eur=0.30, gbp=0.20, aud=0.40), "EU"),
            TLItem("Yakitori", TLCost(eur=4.90, gbp=4.90, aud=4.90), "EU"),
            TLItem("Avocado", 100, "JP"),
            TLItem("Bacon", 380, "JP"),
            TLItem("Blue cheese", 400, "JP"),
            TLItem("Broccoli", 190, "JP"),
            TLItem("Buttered potato", 380, "JP"),
            TLItem("Calamari", 480, "JP"),
            TLItem("Caviar", 6500, "JP"),
            TLItem("Celery", 130, "JP"),
            TLItem("Cheese", 200, "JP"),
            TLItem("Chili prawns", 640, "JP"),
            TLItem("Chizimi", 550, "JP"),
            TLItem("Cooked eggplant", 480, "JP"),
            TLItem("Cornflakes", 400, "JP"),
            TLItem("Corn on the cob", 350, "JP"),
            TLItem("Corn soup", 380, "JP"),
            TLItem("Crab", 6000, "JP"),
            TLItem("Croquettes", 680, "JP"),
            TLItem("Curry-pan", 120, "JP"),
            TLItem("Curry Rice", 700, "JP"),
            TLItem("Drumstick", 1000, "JP"),
            TLItem("Ebi-fry", 370, "JP"),
            TLItem("Escargot", 1200, "JP"),
            TLItem("Foie Gras", 9000, "JP"),
            TLItem("French fries", 280, "JP"),
            TLItem("Fresh spring rolls", 590, "JP"),
            TLItem("Fried egg", 380, "JP"),
            TLItem("Fried rice", 480, "JP"),
            TLItem("Fried spring rolls", 630, "JP"),
            TLItem("Garlic", 110, "JP"),
            TLItem("Green pepper", 110, "JP"),
            TLItem("Hard-boiled egg", 100, "JP"),
            TLItem("Hayashi Rice", 780, "JP"),
            TLItem("Hiyashi Chuka", 600, "JP"),
            TLItem("Hot dog", 280, "JP"),
            TLItem("Instant noodles", 190, "JP"),
            TLItem("Ishiyaki bibimbap", 600, "JP"),
            TLItem("Kankoku Reimen", 670, "JP"),
            TLItem("Kimchi", 280, "JP"),
            TLItem("Mabo Doufu", 670, "JP"),
            TLItem("Meat-and-potato stew", 600, "JP"),
            TLItem("Moldy bread", 20, "JP", trash=True),
            TLItem("Mushroom", 130, "JP"),
            TLItem("Octopus", 300, "JP"),
            TLItem("Okosama lunch", 700, "JP"),
            TLItem("Omelet", 650, "JP"),
            TLItem("Omurice", 680, "JP"),
            TLItem("Onion gratin soup", 410, "JP"),
            TLItem("Pizza", 390, "JP"),
            TLItem("Pork bun", 120, "JP"),
            TLItem("Gyoza", 280, "JP"),
            TLItem("Pretzel", 130, "JP"),
            TLItem("Prosciutto", 690, "JP"),
            TLItem("Quiche", 550, "JP"),
            TLItem("Raw oyster", 680, "JP"),
            TLItem("Red chili pepper", 50, "JP"),
            TLItem("Rice", 200, "JP"),
            TLItem("Risotto", 780, "JP"),
            TLItem("Salad", 560, "JP"),
            TLItem("Salami", 390, "JP"),
            TLItem("Sandwich", 400, "JP"),
            TLItem("Sausage", 200, "JP"),
            TLItem("Shumai", 120, "JP"),
            TLItem("Tacos", 480, "JP"),
            TLItem("Tofu", 150, "JP"),
            TLItem("Tomato", 140, "JP"),
            TLItem("Tonkatsu", 600, "JP"),
            TLItem("Truffle", 6000, "JP"),
            TLItem("White bread", 100, "JP"),
            TLItem("Yakitori", 350, "JP"),
            TLItem("Avocado", 3000, "KR"),
            TLItem("Bacon", 2500, "KR"),
            TLItem("Baguette", 1500, "KR"),
            TLItem("Blue cheese", 2000, "KR"),
            TLItem("Broccoli", 1000, "KR"),
            TLItem("Buttered potato", 3800, "KR"),
            TLItem("Calamari", 3000, "KR"),
            TLItem("Caviar", 65000, "KR"),
            TLItem("Celery", 1000, "KR"),
            TLItem("Cheese", 3500, "KR"),
            TLItem("Chili prawns", 7000, "KR"),
            TLItem("Buchimgae", 8000, "KR"),
            TLItem("Coleslaw", 2500, "KR"),
            TLItem("Corn dog", 2500, "KR"),
            TLItem("Corn on the cob", 2000, "KR"),
            TLItem("Corn soup", 3800, "KR"),
            TLItem("Crab", 30000, "KR"),
            TLItem("Curry Rice", 7000, "KR"),
            TLItem("Drumstick", 3500, "KR"),
            TLItem("Ebi-fry", 1500, "KR"),
            TLItem("Escargot", 12000, "KR"),
            TLItem("French fries", 2800, "KR"),
            TLItem("Fresh spring rolls", 7000, "KR"),
            TLItem("Fried egg", 1700, "KR"),
            TLItem("Fried rice", 5000, "KR"),
            TLItem("Fried spring rolls", 5000, "KR"),
            TLItem("Garlic", 800, "KR"),
            TLItem("Greek Salad", 8000, "KR"),
            TLItem("Green pepper", 800, "KR"),
            TLItem("Hard-boiled egg", 400, "KR"),
            TLItem("Hash browns", 1500, "KR"),
            TLItem("Hot dog", 3000, "KR"),
            TLItem("Instant noodles", 1000, "KR"),
            TLItem("Ishiyaki bibimbap", 8000, "KR"),
            TLItem("Naengmyeon", 6000, "KR"),
            TLItem("Kimchi", 2800, "KR"),
            TLItem("Mabo Doufu", 7000, "KR"),
            TLItem("Moldy bread", 200, trash=True),
            TLItem("Mozzarella salad", 6000, "KR"),
            TLItem("Mushroom", 1300, "KR"),
            TLItem("Mussels", 7000, "KR"),
            TLItem("Oatmeal", 2000, "KR"),
            TLItem("Octopus", 4000, "KR"),
            TLItem("Okosama lunch", 7000, "KR"),
            TLItem("Olives", 3000, "KR"),
            TLItem("Omelet", 5000, "KR"),
            TLItem("Omurice", 7000, "KR"),
            TLItem("Onion rings", 4000, "KR"),
            TLItem("Pizza", 3000, "KR"),
            TLItem("Pork bun", 2000, "KR"),
            TLItem("Prawn salad", 7500, "KR"),
            TLItem("Pretzel", 2500, "KR"),
            TLItem("Prosciutto", 6900, "KR"),
            TLItem("Raw oyster", 1000, "KR"),
            TLItem("Red chili pepper", 500, "KR"),
            TLItem("Rice", 2000, "KR"),
            TLItem("Salad", 5600, "KR"),
            TLItem("Salami", 3900, "KR"),
            TLItem("Sandwich", 5500, "KR"),
            TLItem("Sausage", 2000, "KR"),
            TLItem("Shumai", 2000, "KR"),
            TLItem("Smoked salmon", 9000, "KR"),
            TLItem("Tacos", 8000, "KR"),
            TLItem("Tofu", 1500, "KR"),
            TLItem("Tomato", 900, "KR"),
            TLItem("Tonkatsu", 8000, "KR"),
            TLItem("White bread", 700, "KR"),
            TLItem("Yakitori", 3500, "KR"),
        ]

    @cached_property
    def foods_desserts(self) -> list[TLItem]:
        """
        The list of desserts in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Food/List_of_Desserts_in_Tomodachi_Life.

        Returns:
            list[TLItem]: The list of desserts.
        """
        return [
            TLItem("Anpan", TLCost(jpy=150, krw=1500)),
            TLItem("Apple", TLCost(0.90, 0.50, 0.50, 0.60, 150, 900)),
            TLItem("Apple pie", TLCost(4.30, 3.20, 2.90, 4.10, 480)),
            TLItem("Banana", TLCost(0.80, 0.20, 0.20, 0.30, 100, 800)),
            TLItem(
                TLName("Banana peel", {"EU-en": "Banana skin"}),
                TLCost(0.20, 0.20, aud=0.10, jpy=20, krw=200),
                trash=True,
            ),
            TLItem("Banana split", TLCost(6.50, krw=7500)),
            TLItem("Beef jerky", TLCost(3.00, krw=3000)),
            # Birthday cake is not for sale
            TLItem(
                TLName("Biscuit", {"EU-en": "Scone"}),
                TLCost(1.50, 2.00, 1.50, 2.80, krw=1500),
            ),
            TLItem("Black forest gateau", TLCost(4.50, 4.10, 3.50, 3.60, krw=4500)),
            TLItem("Box of chocolates", TLCost(eur=5.00, aud=9.90, jpy=300, krw=5000)),
            TLItem(
                "Bread with chocolate spread",
                TLCost(eur=1.80, gbp=1.50, aud=3.70),
                "EU",
            ),
            TLItem("Bundt Cake", TLCost(eur=5.50, gbp=4.50, aud=4.90), "EU"),
            TLItem("Butter cookie", TLCost(usd=1.80, jpy=180, krw=1800)),
            TLItem(
                TLName("Candy", {"EU-en": "Toffee apple"}),
                TLCost(2.50, 2.50, 2.00, 250, 2500),
            ),
            TLItem("Candy corn", 0.75, "NA"),
            TLItem("Cannoli", TLCost(eur=2.50, gbp=1.90, aud=1.60), "EU"),
            TLItem("Carrot cake", 5.30, "NA"),
            TLItem(
                "Castella cake", TLCost(eur=3.50, gbp=3.00, aud=3.60, jpy=500, krw=5000)
            ),
            TLItem("Cheesecake", TLCost(3.00, 3.90, 3.50, 4.50, 490, 4500)),
            TLItem("Cherimoya", TLCost(eur=3.00, gbp=2.50, aud=1.50), "EU"),
            TLItem("Cherries", TLCost(1.30, gbp=0.40, aud=0.40, jpy=290, krw=1300)),
            TLItem("Cherry pie", 5.20, "NA"),
            TLItem("Chewing gum", TLCost(1.50, jpy=120, krw=500)),
            TLItem("Chocolate", TLCost(1.50, 2.20, 1.50, 3.40, 150, 1500)),
            TLItem("Chocolate gâteau", TLCost(6.00, 4.00, 3.50, 4.50, 600, 6000)),
            TLItem("Chocolate sundae", TLCost(7.80, 6.50, 5.00, 7.90, 780, 7500)),
            TLItem("Christmas pudding", TLCost(eur=4.00, gbp=5.50, aud=7.40), "EU"),
            TLItem("Churros", TLCost(eur=2.50, gbp=2.00, aud=3.20, krw=3000)),
            TLItem("Cinnamon roll", TLCost(3.00, krw=1300)),
            TLItem("Clotted cream", TLCost(1.20, 1.50, 1.00, 1.20)),
            TLItem("Coconut", TLCost(3.50, 3.50, 3.00, 1.50, 550, 5500)),
            TLItem(
                TLName("Cotton candy", {"EU-en": "Candyfloss"}),
                TLCost(3.00, 1.90, 1.50, 2.40, 300, 3000),
            ),
            TLItem(
                TLName("Cracker", {"EU-en": "Biscuit"}),
                TLCost(0.50, 0.10, 0.10, 0.20, 150, 500),
            ),
            TLItem("Cream puff", TLCost(2.50, jpy=250, krw=2500)),
            TLItem("Creme brulee", TLCost(eur=6.50, gbp=5.50, aud=4.90), "EU"),
            TLItem("Crepe", TLCost(4.00, 5.50, 4.50, 6.50, 400, 4000)),
            TLItem("Croissant", TLCost(1.20, 2.90, 2.00, 2.80, 120, 1200)),
            TLItem("Custard pastry", TLCost(eur=2.50, gbp=2.10, aud=1.50), "EU"),
            TLItem("Danish pastry", TLCost(1.50, 2.10, 1.80, 2.00)),
            TLItem("Dates", TLCost(eur=2.90, aud=3.70), "EU"),
            TLItem("Doughnut", TLCost(1.30, 0.70, 0.50, 1.00, 130, 1300)),
            TLItem("Dorayaki", 450, "JP"),
            TLItem("Durian", TLCost(5.00, jpy=500, krw=10000)),
            TLItem("Elephant ear", 2.00, "NA"),
            TLItem("Elon", 4000, "KR"),
            TLItem("Fancy cupcake", 5.00, "NA"),
            TLItem(
                TLName("Flan", {"EU-en": "Creme caramel"}),
                TLCost(1.50, 5.00, 4.90, 4.50, 150, 1500),
            ),
            TLItem("French toast", TLCost(3.80, 5.90, aud=5.70, jpy=380)),
            TLItem("Frozen treat", 1.00, "NA"),
            TLItem("Frozen yogurt", TLCost(1.80, krw=1800)),
            TLItem("Fudge", TLCost(4.00, 1.70, 1.00, 2.40)),
            TLItem("Gelatin snack", TLCost(1.50, 2.50, 2.00, 3.20, 150, 1500)),
            TLItem("Gingerbread cake", TLCost(4.50, 2.10, aud=3.60)),
            TLItem("Granola parfait", 6.00, "NA"),
            TLItem("Grapefruit", TLCost(2.00, 0.50, 0.50, 1.00, 300, 2000)),
            TLItem("Grapes", TLCost(2.90, 2.80, 1.80, 1.50, 490, 2900)),
            TLItem("Gummy candy", TLCost(0.50, 0.10, 0.10, 0.20, 100, 500)),
            TLItem(
                "Handmade chocolate", TLCost(eur=17.00, aud=30.00, jpy=3000, krw=30000)
            ),
            TLItem("Hard candy", TLCost(0.50, krw=500)),
            TLItem("Honey", TLCost(4.50, 3.50, 2.00, 3.90, krw=4500)),
            TLItem("Hotteok", 2000, "KR"),
            TLItem(
                "Ice-cream cone", TLCost(2.50, gbp=1.00, aud=2.40, jpy=250, krw=2500)
            ),
            TLItem("Ice-cream sandwich", TLCost(1.00, krw=1000)),
            TLItem("Key lime pie", 4.60, "NA"),
            TLItem("Kakikori", 150, "JP"),
            TLItem("Kiwi", TLCost(1.00, 0.30, 0.20, 0.40, 150, 1000)),
            TLItem("Liquorice", TLCost(0.70, 0.50, 0.30, 0.60)),
            TLItem("Lollipop", TLCost(2.50, 2.20, 1.50, 1.80, 300, 2500)),
            TLItem("Macadamia nuts", TLCost(5.00, 5.40, 3.50, 6.50, 500, 5000)),
            TLItem("Macaron", TLCost(1.80, 2.50, 2.00, 2.80, 300, 1800)),
            TLItem("Mango", TLCost(3.00, 1.50, 1.00, 1.90, 900, 3000)),
            TLItem("Marron", TLCost(eur=4.50, gbp=4.00, aud=5.90), "EU"),
            TLItem("Marzipan fruit", TLCost(eur=3.00, gbp=3.00, aud=4.10), "EU"),
            TLItem("Medicine rice", 2500, "KR"),
            TLItem("Melon", TLCost(2.70, 0.60, 0.40, 0.80, 1000, 1000)),
            TLItem("Mince pie", TLCost(eur=1.50, gbp=1.20, aud=2.00), "EU"),
            TLItem("Mint sweet", TLCost(eur=0.20, gbp=0.20, aud=0.20), "EU"),
            TLItem("Muffin", TLCost(2.50, 2.00, 1.50, 3.20, 330, 2500)),
            TLItem(
                TLName("Napoleon cake", {"EU-en": "Custard slice"}),
                TLCost(6.20, 5.50, 4.50, 4.90, 620, 6000),
            ),
            TLItem("Natillas", TLCost(eur=3.20, gbp=3.20, aud=2.90), "EU"),
            TLItem("Oatmeal cookie", 1.00, "NA"),
            TLItem("Orange", TLCost(0.90, 0.40, aud=0.50, jpy=100, krw=900)),
            TLItem("Pain au chocolat", TLCost(eur=2.10, gbp=1.80, aud=2.40), "EU"),
            TLItem("Pancakes", TLCost(4.00, 4.90, 3.50, 4.10, 400, 4000)),
            TLItem("Pandoro", TLCost(eur=5.50, gbp=4.50, aud=7.40), "EU"),
            TLItem("Panettone", TLCost(eur=4.00, aud=4.90), "EU"),
            TLItem("Panna cotta", TLCost(eur=6.50, gbp=5.90, aud=8.40), "EU"),
            TLItem("Peach", TLCost(1.10, gbp=0.60, aud=0.80, jpy=480, krw=1100)),
            TLItem("Peanuts", TLCost(3.70, 2.50, 1.80, 2.00, 370, 2500)),
            TLItem("Pear", TLCost(1.10, gbp=0.50, aud=0.70, jpy=460, krw=5000)),
            TLItem("Persimmon", TLCost(jpy=200, krw=2000)),
            TLItem("Pineapple", TLCost(3.50, 1.50, 1.00, 0.80, 980, 5000)),
            TLItem("Pistachios", TLCost(eur=4.20, gbp=3.50, aud=4.90), "EU"),
            TLItem("Popcorn", TLCost(2.50, 4.00, 3.50, 4.10, 250, 4500)),
            TLItem("Potato chips", TLCost(1.30, 0.90, 0.70, 2.00, 130, 1300)),
            TLItem("Profiteroles", TLCost(gbp=6.90, aud=5.20), "EU"),
            TLItem("Pumpkin pie", 4.60, "NA"),
            TLItem("Red velvet cake", 4.50, "NA"),
            TLItem("Rice pudding", TLCost(eur=5.90, gbp=4.90, aud=5.70), "EU"),
            TLItem(
                TLName("Roasted chestnuts", {"EU-en": "Roast chestnuts"}),
                TLCost(5.80, 2.50, 2.00, 4.90, 580, 3000),
            ),
            TLItem("S'more", 3.00, "NA"),
            TLItem("Saltine crackers", 1.00, "NA"),
            TLItem("Senbei", TLCost(jpy=100, krw=1000)),
            TLItem(
                TLName("Soft-serve ice cream", {"EU-en": "Soft-served ice-cream"}),
                TLCost(2.50, 1.10, 0.90, 1.90, 250, 2500),
            ),
            TLItem("Strawberry", TLCost(0.30, 0.20, 0.20, 0.20, 480, 300)),
            TLItem("Strawberry shortcake", TLCost(4.00, 3.90, 3.50, 4.50, 400, 4000)),
            TLItem("Sunflower seeds", TLCost(3.00, 6.10, 5.50, 5.70, krw=3000)),
            TLItem("Sweet Potato", 380, "JP"),
            TLItem("Taiyaki", TLCost(jpy=200, krw=1000)),
            TLItem("Three color dango", 300, "JP"),
            TLItem("Tiramisu", TLCost(5.00, 5.00, 4.50, 5.70, 500)),
            TLItem("Turron", TLCost(eur=5.20, aud=6.40), "EU"),
            TLItem("Waffle", TLCost(2.00, 2.00, 1.50, 2.40, 200, 2000)),
            TLItem("Walnuts", TLCost(aud=3.70), "EU"),
            TLItem("Watermelon", TLCost(2.00, 0.50, 0.40, 0.60, 300, 2000)),
            TLItem("Yaki imo (Baked yam)", TLCost(jpy=380, krw=1500)),
            TLItem(
                TLName("Yogurt", {"EU-en": "Yoghurt"}),
                TLCost(1.90, 2.50, aud=3.60, jpy=190, krw=1900),
            ),
            TLItem("Youkan", TLCost(jpy=580, krw=3000)),
            TLItem("Yule log", TLCost(eur=7.90, gbp=6.50, aud=3.60), "EU"),
            TLItem("Zenzai", 500, "JP"),
        ]

    @cached_property
    def foods_beverages(self) -> list[TLItem]:
        """
        The list of beverages in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Food/List_of_Beverages_in_Tomodachi_Life.

        Returns:
            list[TLItem]: The list of beverages.
        """
        return [
            TLItem("Apple juice", TLCost(2.00, 3.10, 2.90, 3.60, 200, 2000)),
            TLItem("Bubble tea", TLCost(5.50, krw=4000)),
            TLItem("Cappuccino", TLCost(2.90, 2.40, 2.90, 3.60, 580, 3500)),
            TLItem("Chamomile tea", TLCost(2.70, 2.90, 2.50, 2.30, krw=3000)),
            TLItem("Coffee", TLCost(2.20, 1.90, 1.90, 2.00, 500, 2500)),
            TLItem("Eggnog", 5.00, "NA"),
            TLItem("Energy drink", TLCost(jpy=300, krw=1000)),
            TLItem("Espresso", TLCost(1.90, 2.10, 1.80, 3.20)),
            TLItem("Green juice", TLCost(3.50, jpy=200, krw=3500)),
            TLItem(
                "Green tea", TLCost(eur=1.50, gbp=1.20, aud=2.00, jpy=100, krw=2500)
            ),
            TLItem("Hot chocolate", TLCost(2.00, 2.50, 3.90, 3.60, krw=4000)),
            TLItem("Iced caffè latte", 4000, "KR"),
            TLItem("Lemonade", TLCost(2.50, 2.50, 2.50, 3.20, krw=3000)),
            TLItem("Milk", TLCost(1.80, 1.20, 1.00, 1.80, 180, 1800)),
            TLItem("Milkshake", 5.00, "NA"),
            TLItem("Orange juice", TLCost(2.00, 3.50, 2.90, 3.20, 200, 2000)),
            TLItem(
                TLName("Protein shake", {"JP-en": "Protein"}),
                TLCost(3.50, 3.00, 2.60, 3.20, 1000),
            ),
            TLItem("Root-beer float", 3.80, "NA"),
            TLItem("Schisandra berry tea", 4500, "KR"),
            TLItem(
                TLName("Smoothie", {"JP-en": "Mixed juice"}),
                TLCost(2.50, 2.50, 2.90, 3.60, 250, 3000),
            ),
            TLItem(
                TLName("Soda", {"EU-en": "Cola", "JP-en": "Cola"}),
                TLCost(2.50, 2.90, 2.50, 3.20, 180, 2500),
            ),
            TLItem("Sparkling water", TLCost(eur=1.00, gbp=1.90, aud=3.20), "EU"),
            TLItem("Spiced apple cider", TLCost(2.00, krw=2000)),
            TLItem(
                TLName("Spoiled milk", {"EU-en": "Spoilt milk"}),
                TLCost(0.20, 0.10, 0.10, 0.10, 20, 200),
                trash=True,
            ),
            TLItem("Sports drink", 2.00, "NA"),
            TLItem("Ssanghwa tea", 4500, "KR"),
            TLItem("Tap water", TLCost(0.90, 0.10, 0.10, 0.10, 90, 900)),
            TLItem("Tea", TLCost(2.30, 2.10, 1.90, 1.90, 550, 4000)),
            TLItem("Tomato juice", TLCost(1.50, 3.10, 2.90, 3.60, 150, 3000)),
            TLItem("Yerba mate", 5.40, "NA"),
        ]

    @cached_property
    def interiors_base(self) -> list[TLItem]:
        """
        The list of interiors in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Interior. Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of interiors.
        """
        return [
            TLItem("Antique", TLCost(dollars=280.00, scale=True)),
            TLItem(
                TLName("Arabian", {"JP-en": "Arabian Style", "KR-en": "Arabian Style"}),
                TLCost(dollars=500.00, jpy=17000, krw=500000),
            ),
            TLItem("Arcade", TLCost(dollars=500.00, jpy=17000, krw=500000)),
            TLItem("Art gallery", TLCost(dollars=300.00, scale=True)),
            TLItem("Bathhouse", TLCost(dollars=65.00, scale=True)),
            TLItem("Bedroom Style", 230000, "KR"),
            TLItem("Bicycle", TLCost(dollars=155.00, scale=True)),
            TLItem("Bohemian", TLCost(dollars=110.00, scale=True)),
            TLItem("Boy's", TLCost(dollars=110.00, scale=True)),
            TLItem("Campfire", TLCost(dollars=190.00, krw=190000)),
            TLItem("Cartoon", TLCost(dollars=200.00, jpy=50000, krw=200000)),
            TLItem("Cave", TLCost(dollars=80.00, scale=True)),
            TLItem(
                TLName("Checkered", {"EU-en": "Chequered"}),
                TLCost(dollars=235.00, scale=True),
            ),
            TLItem("Children's", TLCost(dollars=80.00, scale=True)),
            TLItem("Cinema", TLCost(dollars=800.00, krw=800000)),
            TLItem(
                TLName("Classroom", {"EU-en": "School", "JP-en": "Classroom Style"}),
                TLCost(dollars=150.00, jpy=10000, krw=150000),
            ),
            TLItem("Colorful", TLCost(dollars=150.00, jpy=7000, krw=150000)),
            TLItem("Country", TLCost(dollars=140.00, scale=True)),
            TLItem("Crystal", TLCost(dollars=1500.00, jpy=50000, krw=1500000)),
            TLItem("Disco", TLCost(dollars=1000.00, jpy=20000, krw=1000000)),
            TLItem("Dressing", TLCost(dollars=60.00, scale=True)),
            TLItem("Elegant", TLCost(dollars=150.00, scale=True)),
            TLItem("Empty", TLCost(dollars=20.00, jpy=5000, krw=20000)),
            TLItem("English garden", TLCost(dollars=400.00, jpy=100000, krw=400000)),
            TLItem("European", TLCost(dollars=150.00, scale=True)),
            TLItem(
                TLName("Exotic", {"EU-en": "Ethnic"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Fairy-tale castle", TLCost(dollars=500.00, krw=500000)),
            # Family is not for sale
            TLItem(
                TLName(
                    "Fast food",
                    {
                        "EU-en": "Fast-food",
                        "JP-en": "Fast Food Style",
                        "KR-en": "Fast Food Style",
                    },
                ),
                TLCost(dollars=250.00, jpy=14900, krw=250000),
            ),
            TLItem(
                TLName("Fifties Japanese", {"JP-en": "Showa era"}),
                TLCost(eur=100.00, gbp=100.00, aud=100.00, jpy=10000, krw=100000),
            ),
            TLItem("Floral", TLCost(dollars=150.00, jpy=15000, krw=150000)),
            TLItem("Flower meadow", TLCost(dollars=200.00, scale=True)),
            TLItem(
                TLName(
                    "Fluffy", {"JP-en": "Mokomoko Style", "KR-en": "Mokomoko Style"}
                ),
                TLCost(dollars=111.00, scale=True),
            ),
            TLItem(
                TLName(
                    "Frontier sunset",
                    {"JP-en": "Western Glow Style", "KR-en": "Western Glow Style"},
                ),
                TLCost(dollars=300.00, jpy=20000, krw=300000),
            ),
            TLItem("Galactic", TLCost(dollars=5000.00, jpy=200000, krw=5000000)),
            TLItem("Gamer", TLCost(dollars=1337.00, jpy=25000, krw=1337000)),
            TLItem("Garage", TLCost(dollars=150.00, scale=True)),
            TLItem("Girl's", TLCost(dollars=120.00, scale=True)),
            TLItem("Golden", TLCost(dollars=20000.00, jpy=1000000, krw=20000000)),
            TLItem("Gothic", TLCost(dollars=270.00, scale=True)),
            TLItem("Halloween", TLCost(dollars=300.00, jpy=15000, krw=300000)),
            TLItem("Hobby", TLCost(dollars=160.00, scale=True)),
            TLItem(
                TLName(
                    "Holiday",
                    {
                        "EU-en": "Christmas",
                        "JP-en": "Christmas Style",
                        "KR-en": "Christmas Style",
                    },
                ),
                TLCost(dollars=500.00, jpy=30000, krw=500000),
            ),
            TLItem("Horror", TLCost(dollars=135.00, scale=True)),
            TLItem("Hospital", TLCost(dollars=112.00, scale=True)),
            TLItem(
                TLName(
                    "Humble",
                    {
                        "EU-en": "Shack",
                        "JP-en": "Poverty Style",
                        "KR-en": "Poverty Style",
                    },
                ),
                TLCost(dollars=9.80, scale=True),
            ),
            TLItem("Ice", TLCost(dollars=200.00, jpy=16500, krw=200000)),
            TLItem("Industrial", TLCost(dollars=200.00, scale=True)),
            TLItem("Jail cell", TLCost(dollars=35.00, scale=True)),
            TLItem("Japanese garden", TLCost(dollars=128.00, jpy=12800)),
            TLItem("Jangdokdae Style", 400000, "KR"),
            TLItem("Kitchen", TLCost(dollars=180.00, jpy=9000, krw=180000)),
            TLItem(
                TLName("Laboratory", {"EU-en": "Lab"}),
                TLCost(dollars=800.00, jpy=30000, krw=800000),
            ),
            TLItem(
                TLName(
                    "Lady jet-setter", {"EU-en": "Active woman's", "JP-en": "OL Style"}
                ),
                TLCost(dollars=120.00, scale=True),
            ),
            TLItem("Library", TLCost(dollars=100.00, scale=True)),
            TLItem("Locker", TLCost(dollars=90.00, scale=True)),
            TLItem("Log cabin", TLCost(dollars=250.00, jpy=10000, krw=250000)),
            TLItem("Mask", TLCost(dollars=200.00, scale=True)),
            TLItem("Meadow", TLCost(dollars=150.00, jpy=20000, krw=150000)),
            TLItem("Medieval European", TLCost(dollars=400.00, scale=True)),
            TLItem(
                TLName("Midcentury modern", {"EU-en": "Retro"}),
                TLCost(dollars=175.00, jpy=17500, krw=175000),
            ),
            # Modern Asian is not for sale
            TLItem("Monochrome", TLCost(dollars=130.00, scale=True)),
            TLItem("Music", TLCost(dollars=260.00, jpy=12000, krw=260000)),
            TLItem("Mystery", TLCost(dollars=600.00, scale=True)),
            # Natural wood is not for sale
            TLItem("Nouveau riche", TLCost(dollars=2000.00, jpy=500000, krw=2000000)),
            TLItem("Office", TLCost(dollars=60.00, scale=True)),
            TLItem("Palace Style", 700000, "KR"),
            TLItem(
                TLName("Pet cage", {"JP-en": "Breeding Case Style"}),
                TLCost(dollars=90.00, scale=True),
            ),
            TLItem(
                TLName("Photo realistic", {"EU-en": "Real"}),
                TLCost(dollars=1000.00, jpy=200000, krw=1000000),
            ),
            TLItem("Pirate ship", TLCost(dollars=250.00, scale=True)),
            # Plant is not for sale
            # Polka dot is not for sale
            TLItem(
                TLName("Prehistoric", {"JP-en": "TAICO Style"}),
                TLCost(dollars=3000.00, jpy=500000, krw=3000000),
            ),
            TLItem("Pumpkin patch", TLCost(dollars=300.00, jpy=8300, krw=300000)),
            TLItem(
                TLName(
                    "Purple",
                    {"JP-en": "Purple Walls Style", "KR-en": "Purple Walls Style"},
                ),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Rain", {"JP-en": "Cold rain", "KR-en": "Cold rain"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName(
                    "Relaxing",
                    {"EU-en": "Moody", "JP-en": "Moody Style", "KR-en": "Moody Style"},
                ),
                TLCost(dollars=160.00, scale=True),
            ),
            TLItem("Ring", TLCost(dollars=750.00, jpy=15000, krw=750000)),
            TLItem(
                TLName(
                    "Rock club",
                    {"JP-en": "Rock Club Style", "KR-en": "Rock Club Style"},
                ),
                TLCost(dollars=240.00, jpy=12500, krw=240000),
            ),
            TLItem("Roman", TLCost(dollars=300.00, jpy=10000, krw=300000)),
            TLItem("Scandinavian", TLCost(dollars=125.00, jpy=25000, krw=125000)),
            TLItem("Seabed", TLCost(dollars=300.00, scale=True)),
            TLItem(
                TLName(
                    "Secret base",
                    {"JP-en": "Secret Base Style", "KR-en": "Secret Base Style"},
                ),
                TLCost(dollars=110.00, scale=True),
            ),
            TLItem("Sky", TLCost(dollars=450.00, scale=True)),
            TLItem("Skyscraper", TLCost(dollars=320.00, jpy=390000, krw=320000)),
            TLItem(
                TLName("Soccer stadium", {"EU-en": "Football stadium"}),
                TLCost(dollars=1100.00, jpy=8000, krw=1100000),
            ),
            TLItem("Space station", TLCost(dollars=2000.00, jpy=1000000, krw=2000000)),
            TLItem("Sparkle", TLCost(dollars=125.00, scale=True)),
            TLItem("Spring", TLCost(dollars=400.00, jpy=20000, krw=400000)),
            TLItem("Steampunk", TLCost(dollars=230.00, jpy=13000, krw=230000)),
            TLItem("Street", TLCost(dollars=165.00, scale=True)),
            TLItem("Sweets", TLCost(dollars=250.00, scale=True)),
            # Tiled is not for sale
            TLItem("Traditional Japanese", TLCost(dollars=500.00, jpy=100000)),
            TLItem("Train", TLCost(dollars=250.00, scale=True)),
            TLItem(
                TLName(
                    "Training", {"JP-en": "Training Style", "KR-en": "Training Style"}
                ),
                TLCost(dollars=300.00, jpy=8000, krw=300000),
            ),
            TLItem("Tropical beach", TLCost(dollars=900.00, jpy=30000, krw=900000)),
            TLItem("Tropical resort", TLCost(dollars=250.00, scale=True)),
            TLItem("Versailles", TLCost(dollars=3000.00, jpy=100000, krw=3000000)),
            TLItem("Wedding", TLCost(dollars=990.00, jpy=39000, krw=990000)),
            TLItem("Wild West", TLCost(dollars=150.00, scale=True)),
            TLItem(
                TLName("Winter", {"JP-en": "Winter Style"}),
                TLCost(dollars=400.00, jpy=12000, krw=400000),
            ),
            TLItem(
                TLName("Wizard", {"JP-en": "Magic Style", "KR-en": "Magic Style"}),
                TLCost(dollars=140.00, scale=True),
            ),
            TLItem("Yellow", TLCost(dollars=100.00, scale=True)),
        ]

    @cached_property
    def clothes_masculine(self) -> list[TLItem]:
        """
        The list of masculine clothes in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Clothing/Masculine. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of masculine clothes.
        """
        return [
            TLItem("Acid-washed jeans", TLCost(dollars=19.90, jpy=1980, krw=19800)),
            TLItem("Argyle sweater", TLCost(dollars=63.00, scale=True)),
            TLItem(
                TLName("Baseball shirt", {"EU-en": "Baseball T-shirt"}),
                TLCost(dollars=19.90, jpy=1980, krw=19800),
            ),
            TLItem("Belted shirt", TLCost(dollars=68.00, scale=True)),
            TLItem("Bow tie & jeans combo", TLCost(dollars=65.00, scale=True)),
            TLItem(
                TLName("Bow tie & shorts", {"EU-en": "Bow tie & shorts combo"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem("Boy band outfit", TLCost(dollars=95.00, scale=True)),
            TLItem("Boys' blazer", TLCost(dollars=68.00, scale=True)),
            TLItem("Camo trousers", TLCost(dollars=25.00, scale=True)),
            TLItem("Camouflage jacket", TLCost(dollars=20.00, scale=True)),
            TLItem(
                TLName("Car-print t-shirt", {"EU-en": "Car T-shirt"}),
                TLCost(dollars=19.90, jpy=1980, krw=19800),
            ),
            TLItem(
                TLName("Cardigan & harem pants", {"EU-en": "Low-slung jeans"}),
                TLCost(dollars=32.00, scale=True),
            ),
            TLItem(
                TLName("Cargo pants", {"EU-en": "Cargo trousers"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem(
                TLName("Checkered dress shirt", {"EU-en": "Checked shirt"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem(
                TLName("Checkered shirt & jeans", {"EU-en": "Shirt & jeans combo"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem(
                TLName("Checkered shirt & shorts", {"EU-en": "Checked T-shirt"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem(
                TLName("Chinese-print T-shirt", {"EU-en": "Chinese print T-shirt"}),
                TLCost(dollars=12.90, jpy=1280, krw=12900),
            ),
            TLItem(
                TLName("Collared car shirt", {"EU-en": "Car shirt"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem("Collared sweater", TLCost(dollars=58.00, scale=True)),
            TLItem("Commando sweater", TLCost(dollars=56.00, scale=True)),
            TLItem("Denim shorts", TLCost(dollars=29.90, jpy=2980, krw=29900)),
            TLItem(
                TLName("Diamond vest", {"EU-en": "Diamond waistcoat"}),
                TLCost(dollars=66.00, scale=True),
            ),
            TLItem("Double-layered top", TLCost(dollars=38.00, scale=True)),
            TLItem("Flannel shirt", TLCost(dollars=29.90, jpy=2980, krw=29900)),
            TLItem("Fleece jacket", TLCost(dollars=25.00, scale=True)),
            TLItem("Flight jacket", TLCost(dollars=48.00, scale=True)),
            TLItem(
                TLName("Formal shorts suit", {"EU-en": "Formal boys' clothes"}),
                TLCost(dollars=58.00, scale=True),
            ),
            TLItem(
                TLName("Jacket & jeans", {"EU-en": "Jacket & jeans combo"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem(
                TLName("Jacket & t-shirt", {"EU-en": "Jacket & T-shirt combo"}),
                TLCost(dollars=86.00, scale=True),
            ),
            TLItem(
                TLName("Jean jacket", {"EU-en": "Denim jacket"}),
                TLCost(dollars=58.00, scale=True),
            ),
            TLItem(
                TLName("Knitted vest & tie", {"EU-en": "Tank top & tie combo"}),
                TLCost(dollars=56.00, scale=True),
            ),
            TLItem(
                TLName("Leather blazer & hoodie", {"EU-en": "Hoody & jacket combo"}),
                TLCost(dollars=56.00, scale=True),
            ),
            TLItem("Leather outfit", TLCost(dollars=100.00, scale=True)),
            TLItem(
                TLName("Li'l bear t-shirt", {"EU-en": "Bear t-shirt"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem(
                TLName("Logo sweater", {"EU-en": "Rap shirt"}),
                TLCost(dollars=29.90, jpy=2980, krw=29900),
            ),
            TLItem("Long waistcoat", TLCost(dollars=25.00, scale=True)),
            TLItem("Lumberjack clothes", TLCost(dollars=38.00, krw=38000)),
            TLItem("Men's haregi", 20000, "JP"),
            TLItem("Men's yukata", 2500, "JP"),
            TLItem("Military coat", TLCost(dollars=78.00, scale=True)),
            TLItem("Montsuki Hakama", TLCost(jpy=8000, krw=80000)),
            TLItem("Nehru jacket", TLCost(dollars=40.00, scale=True)),
            TLItem(
                TLName("Outdoorsy outfit", {"EU-en": "Outdoors outfit"}),
                TLCost(dollars=19.00, scale=True),
            ),
            TLItem(
                TLName("Oversized jersey", {"EU-en": "Oversized shirt"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem(
                TLName("Peacoat", {"EU-en": "Pea jacket"}),
                TLCost(dollars=73.00, scale=True),
            ),
            TLItem("Polka-dot shirt", TLCost(dollars=28.00, scale=True)),
            TLItem("Polo shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem(
                TLName("Prepster outfit", {"EU-en": "Checked scarf"}),
                TLCost(dollars=39.00, scale=True),
            ),
            TLItem(
                TLName("Private-school uniform", {"KR-en": "Retro Schoolboy Uniform"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Puffy jacket", {"EU-en": "Puffer jacket"}),
                TLCost(dollars=56.00, scale=True),
            ),
            TLItem(
                TLName("Purple-blot t-shirt", {"EU-en": "Large T-shirt"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem(
                TLName("Rocker outfit", {"EU-en": "Ripped jeans"}),
                TLCost(dollars=98.00, scale=True),
            ),
            TLItem("Rugby shirt", TLCost(dollars=15.00, scale=True)),
            TLItem(
                TLName("Shirt & khakis", {"EU-en": "Shirt & trousers combo"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem(
                TLName("Shirt & slacks", {"EU-en": "School uniform/short sleeve"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Short-sleeved jacket", {"EU-en": "Sweat jacket"}),
                TLCost(dollars=19.00, scale=True),
            ),
            TLItem("Short-sleeved shirt", TLCost(dollars=22.00, scale=True)),
            TLItem("Skyline t-shirt", TLCost(dollars=19.90, scale=True)),
            TLItem(
                TLName("Snazzy suit", {"EU-en": "Sharp suit"}),
                TLCost(dollars=150.00, scale=True),
            ),
            TLItem(
                TLName("Soccer shirt", {"EU-en": "Football shirt"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem(
                TLName("Striped dress shirt", {"EU-en": "Striped shirt"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem("Striped jacket", TLCost(dollars=98.00, scale=True)),
            TLItem("Suede jacket", TLCost(dollars=98.00, scale=True)),
            TLItem("Surfer T-shirt", TLCost(dollars=25.00, scale=True)),
            TLItem(
                TLName("Sweater-vest", {"EU-en": "Tank top"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem("Sweatshirt", TLCost(dollars=12.90, jpy=1280, krw=12900)),
            TLItem(
                TLName("T-shirt & shorts", {"EU-en": "T-shirt & shorts combo"}),
                TLCost(dollars=18.00, scale=True),
            ),
            TLItem(
                TLName("Tank top", {"EU-en": "Vest"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem(
                TLName("Tank top & shorts", {"EU-en": "Vest & shorts combo"}),
                TLCost(dollars=7.90, jpy=780, krw=7900),
            ),
            TLItem("Tartan shirt", TLCost(dollars=45.00, scale=True)),
            TLItem("Tie-dye t-shirt", TLCost(dollars=25.00, scale=True)),
            TLItem("Tiger baseball jacket", TLCost(dollars=36.00, scale=True)),
            TLItem("Trench coat", TLCost(dollars=86.00, scale=True)),
            TLItem("Tricolor shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem(
                TLName("Tuxedo", {"EU-en": "Dinner jacket"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem("Tweed jacket", TLCost(dollars=88.00, scale=True)),
            TLItem("V-neck sweater", TLCost(dollars=28.00, scale=True)),
            TLItem(
                TLName("Wild jacket", {"EU-en": "Sheepskin jacket"}),
                TLCost(dollars=58.00, scale=True),
            ),
        ]

    @cached_property
    def clothes_feminine(self) -> list[TLItem]:
        """
        The list of feminine clothes in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Clothing/Feminine. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of feminine clothes.
        """
        return [
            TLItem("1920s dress", TLCost(dollars=56.00, scale=True)),
            TLItem("Ballet top", TLCost(dollars=24.00, scale=True)),
            TLItem("Big-ribbon dress", TLCost(dollars=50.00, scale=True)),
            TLItem(
                TLName("Bolero & dress", {"EU-en": "Shrug & dress combo"}),
                TLCost(dollars=98.00, scale=True),
            ),
            TLItem("Bow blouse", TLCost(dollars=38.00, scale=True)),
            TLItem("Bubble dress", TLCost(dollars=65.00, scale=True)),
            TLItem("Bubble skirt", TLCost(dollars=32.00, scale=True)),
            TLItem("Cactus T-shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Camisole dress", TLCost(dollars=25.00, scale=True)),
            TLItem(
                TLName("Checkered-trim dress", {"EU-en": "Checked trim dress"}),
                TLCost(dollars=36.00, krw=36000),
            ),
            TLItem(
                TLName("Checkered dress", {"EU-en": "Checked dress"}),
                TLCost(dollars=24.00, scale=True),
            ),
            TLItem(
                TLName("Cherry romper", {"EU-en": "Cherry romper suit"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem(
                TLName("Coat & skirt", {"EU-en": "Coat & skirt combo"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem("Comfy loungewear", TLCost(dollars=58.00, scale=True)),
            TLItem(
                TLName("Crocheted vest", {"EU-en": "Crochet waistcoat"}),
                TLCost(dollars=36.00, scale=True),
            ),
            TLItem(
                TLName("Denim dress", {"EU-en": "Dungaree dress"}),
                TLCost(dollars=18.00, scale=True),
            ),
            TLItem("Denim miniskirt", TLCost(dollars=32.00, scale=True)),
            TLItem("Dessert T-shirt", TLCost(dollars=30.00, scale=True)),
            TLItem("Dolman sweater", TLCost(dollars=92.00, scale=True)),
            TLItem("Dolman T-shirt", TLCost(dollars=24.00, scale=True)),
            TLItem(
                TLName("Dress & jacket", {"EU-en": "Dress & jacket combo"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem(
                TLName("Dress & tights", {"EU-en": "Dress & tights combo"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem(
                TLName("Dressy cardigan", {"EU-en": "Cardy & skirt combo"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem("Embroidered tunic", TLCost(dollars=42.00, scale=True)),
            TLItem("Evening gown", TLCost(dollars=450.00, scale=True)),
            TLItem(
                TLName("Exotic skirt", {"EU-en": "Ethnic skirt"}),
                TLCost(dollars=53.00, scale=True),
            ),
            TLItem(
                TLName("Fall dress", {"EU-en": "Autumn dress"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Faux-fur coat", {"EU-en": "Faux-fur coat"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem("Flamenco dress", TLCost(dollars=68.00, scale=True)),
            TLItem("Flannel-shirt maxi dress", TLCost(dollars=48.00, scale=True)),
            TLItem("Flared miniskirt", TLCost(dollars=46.00, scale=True)),
            TLItem("Flared skirt", TLCost(dollars=38.00, scale=True)),
            TLItem("Floral dress", TLCost(dollars=85.00, scale=True)),
            TLItem("Flower camisole dress", TLCost(dollars=39.90, jpy=3980, krw=39900)),
            TLItem("Flower leggings", TLCost(dollars=48.00, scale=True)),
            TLItem("Flower tunic", TLCost(dollars=38.00, scale=True)),
            TLItem("Folklore skirt", TLCost(dollars=42.00, scale=True)),
            TLItem("Forest-maiden outfit", TLCost(dollars=35.00, scale=True)),
            TLItem(
                TLName("Formal dress", {"EU-en": "Formal girls' clothes"}),
                TLCost(dollars=58.00, scale=True),
            ),
            TLItem("Frilled shirt", TLCost(dollars=19.90, jpy=1980, krw=19800)),
            TLItem("Frilly dress", TLCost(dollars=72.00, scale=True)),
            TLItem("Front-tied shirt", TLCost(dollars=28.00, scale=True)),
            TLItem("Gauze dress", TLCost(dollars=36.00, scale=True)),
            TLItem("Gauze nightdress", TLCost(dollars=28.00, scale=True)),
            TLItem("Girls' blazer", TLCost(dollars=68.00, scale=True)),
            TLItem(
                TLName("Girly hoodie", {"EU-en": "Hoody & skirt combo"}),
                TLCost(dollars=19.90, jpy=1980, krw=19800),
            ),
            TLItem(
                TLName("Girly school uniform", {"EU-en": "Girls' dress"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem(
                TLName("Gothic dress", {"EU-en": "Chic dress"}),
                TLCost(dollars=500.00, scale=True),
            ),
            TLItem("Hand-knitted shawl", TLCost(dollars=47.00, krw=47000)),
            TLItem(
                TLName("Heart sweatshirt", {"EU-en": "Girls' jacket"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem(
                TLName("Jacket & skirt", {"EU-en": "Jacket & skirt combo"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem("Lacy dress", TLCost(dollars=98.00, scale=True)),
            TLItem("Lacy maxi dress", TLCost(dollars=56.00, scale=True)),
            TLItem(
                TLName("Ladies' turtleneck", {"EU-en": "Turtleneck & skirt combo"}),
                TLCost(dollars=24.00, scale=True),
            ),
            TLItem("Leopard-print sweatshirt", TLCost(dollars=9.90, jpy=980, krw=9900)),
            TLItem("Logo dress", TLCost(dollars=19.90, krw=19900)),
            TLItem("Long denim skirt", TLCost(dollars=36.90, jpy=3680, krw=36900)),
            TLItem(
                TLName("Long knit sweater", {"EU-en": "Patterned tights"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem("Loose-fit dress", TLCost(dollars=76.00, scale=True)),
            TLItem("Loose sweater", TLCost(dollars=48.00, scale=True)),
            TLItem("Marble-dots shirt", TLCost(dollars=28.00, scale=True)),
            TLItem("Mini Yukata", 4200, "JP"),
            TLItem("Pinafore", TLCost(dollars=50.00, scale=True)),
            TLItem("Plain color Kimono", 20000, "JP"),
            TLItem("Pleated skirt", TLCost(dollars=48.00, scale=True)),
            TLItem("Polka-dot dress", TLCost(dollars=20.00, krw=20000)),
            TLItem(
                TLName("Polka-dot tank top", {"EU-en": "Polka-dot vest"}),
                TLCost(dollars=29.90, krw=29900),
            ),
            TLItem("Polo dress", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Psychedelic Jumpsuit", TLCost(dollars=53.00, scale=True)),
            TLItem("Puffy ribbon dress", TLCost(dollars=100.00, scale=True)),
            TLItem(
                TLName("Rainbow dress", {"EU-en": "Rainbow-stripe dress"}),
                TLCost(dollars=36.00, krw=36000),
            ),
            TLItem("Reindeer dress", TLCost(dollars=69.00, scale=True)),
            TLItem("Retro dress", TLCost(dollars=19.00, krw=19000)),
            TLItem(
                TLName("Ribbon cardigan", {"EU-en": "Shorts & cardy combo"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem("Rockabilly dress", TLCost(dollars=38.00, krw=38000)),
            TLItem(
                TLName("Round-collar blouse", {"EU-en": "Embroidered blouse"}),
                TLCost(dollars=29.00, krw=29000),
            ),
            TLItem("Sailor dress", TLCost(dollars=24.00, scale=True)),
            TLItem("Salopettes", TLCost(dollars=19.90, scale=True)),
            TLItem(
                TLName("Scarf & sweater", {"EU-en": "Colourful scarf"}),
                TLCost(dollars=69.00, scale=True),
            ),
            TLItem("Scoop-neck top", TLCost(dollars=32.00, scale=True)),
            TLItem(
                TLName("Shirt & skirt", {"EU-en": "Shirt & skirt combo"}),
                TLCost(dollars=65.00, scale=True),
            ),
            TLItem("Shirt dress", TLCost(dollars=25.00, scale=True)),
            TLItem(
                TLName("Short checkered dress", {"EU-en": "Short checked dress"}),
                TLCost(dollars=58.00, scale=True),
            ),
            TLItem("Shoulder-pad dress", TLCost(dollars=300.00, scale=True)),
            TLItem(
                TLName("Silk blazer", {"EU-en": "Blazer"}),
                TLCost(dollars=59.00, scale=True),
            ),
            TLItem(
                TLName("Silk dress", {"EU-en": "Halter-neck dress"}),
                TLCost(dollars=65.00, scale=True),
            ),
            TLItem(
                TLName("Skirt & scarf", {"EU-en": "Skirt & scarf combo"}),
                TLCost(dollars=52.00, scale=True),
            ),
            TLItem(
                TLName("Skirt & suspenders", {"EU-en": "Skirt & braces combo"}),
                TLCost(dollars=18.00, scale=True),
            ),
            TLItem("Sleeveless shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Smock", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Snood", TLCost(dollars=38.00, scale=True)),
            TLItem("Spiderweb T-shirt", TLCost(dollars=25.00, krw=25000)),
            TLItem("Spring dress", TLCost(dollars=50.00, scale=True)),
            TLItem("Spring trench coat", TLCost(dollars=48.00, scale=True)),
            TLItem(
                TLName("Stole & leggings", {"EU-en": "Stole & leggings combo"}),
                TLCost(dollars=36.90, jpy=3680, krw=36900),
            ),
            TLItem(
                TLName("Strawberry hoodie", {"EU-en": "Strawberry hoody"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem("Striped pullover", TLCost(dollars=28.00, scale=True)),
            TLItem("Striped tunic", TLCost(dollars=25.00, scale=True)),
            TLItem("Summer dress", TLCost(dollars=50.00, scale=True)),
            TLItem("Summer ensemble", TLCost(dollars=78.00, scale=True)),
            TLItem("Sweet dress", TLCost(dollars=48.00, scale=True)),
            TLItem("T-shirt maxi dress", TLCost(dollars=38.00, scale=True)),
            TLItem(
                TLName("Thigh-high boots", {"EU-en": "Knee-high boots"}),
                TLCost(dollars=56.00, krw=56000),
            ),
            TLItem(
                TLName("Training gear", {"EU-en": "Training kit"}),
                TLCost(dollars=29.90, jpy=2980, krw=29900),
            ),
            TLItem("Tropical dress", TLCost(dollars=38.00, scale=True)),
            TLItem(
                TLName("Tunic & leggings", {"EU-en": "Tunic & leggings combo"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem("Tweed dress", TLCost(dollars=45.00, scale=True)),
            TLItem("V-neck top", TLCost(dollars=24.00, scale=True)),
            TLItem("Winter dress", TLCost(dollars=50.00, scale=True)),
            TLItem("Women's Haregi", 30000, "JP"),
            TLItem("Women's Yukata", 25000, "JP"),
            TLItem("Wrap dress", TLCost(dollars=68.00, scale=True)),
            TLItem(
                TLName("Zebra-print dress", {"EU-en": "Zebra dress"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem("Schoolgirl uniform", TLCost(50.00, jpy=5000, krw=50000)),
        ]

    @cached_property
    def clothes_unisex(self) -> list[TLItem]:
        """
        The list of unisex clothes in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Clothing/Unisex. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of unisex clothes.
        """
        return [
            TLItem(
                TLName("Baby jumper", {"EU-en": "Romper suit"}),
                TLCost(dollars=30.00, scale=True),
            ),
            TLItem(
                TLName("Baggy hoodie", {"EU-en": "Baggy hoody"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem("Baggy shirt", TLCost(dollars=30.00, scale=True)),
            TLItem("Baggy T-shirt", TLCost(dollars=28.00, scale=True)),
            TLItem(
                TLName("Baseball T-shirt", {"EU-en": "Raglan & shorts combo"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem("Basic shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Bath towel", TLCost(dollars=20.00, scale=True)),
            TLItem("Bell-bottoms", TLCost(dollars=78.00, scale=True)),
            TLItem(
                TLName("Boatneck shirt", {"EU-en": "Boat neck shirt"}),
                TLCost(dollars=29.90, jpy=2980, krw=29900),
            ),
            TLItem("Breton shirt", TLCost(dollars=39.90, jpy=3980, krw=39900)),
            TLItem(
                TLName("Button cardigan", {"EU-en": "Cotton cardigan"}),
                TLCost(dollars=39.90, jpy=3980, krw=39900),
            ),
            TLItem("Cardigan", TLCost(dollars=15.00, scale=True)),
            TLItem(
                TLName("Colorful pants", {"EU-en": "Colour trousers"}),
                TLCost(dollars=36.00, scale=True),
            ),
            TLItem("Cooking apron", TLCost(dollars=19.90, scale=True)),
            TLItem("Cowichan sweater", TLCost(dollars=68.00, scale=True)),
            TLItem(
                TLName("Crazy-pattern shirt", {"EU-en": "Wild-patterned shirt"}),
                TLCost(dollars=46.00, scale=True),
            ),
            TLItem("Disco suit", TLCost(dollars=100.00, krw=100000)),
            TLItem("Dolphin T-shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem(
                TLName("Down vest", {"EU-en": "Hoody & gilet combo"}),
                TLCost(dollars=28.90, scale=True),
            ),
            TLItem("Dressing gown", TLCost(dollars=48.00, scale=True)),
            TLItem(
                TLName("Dress shirt & shorts", {"EU-en": "Shirt & shorts combo"}),
                TLCost(dollars=29.90, jpy=2980, krw=29900),
            ),
            TLItem(
                TLName("Dungaree shirt", {"EU-en": "Denim shirt"}),
                TLCost(dollars=59.00, scale=True),
            ),
            TLItem(
                TLName("Earthy clothes", {"EU-en": "Ethnic clothes"}),
                TLCost(dollars=36.00, scale=True),
            ),
            TLItem(
                TLName("Exotic shirt", {"EU-en": "Ethnic shirt"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem(
                TLName("Flared trousers", {"EU-en": "Baggy trousers"}),
                TLCost(dollars=29.90, jpy=2980, krw=29900),
            ),
            TLItem(
                TLName("Frog romper", {"EU-en": "Frog romper suit"}),
                TLCost(dollars=35.00, scale=True),
            ),
            TLItem("Gingham shirt", TLCost(dollars=65.00, scale=True)),
            TLItem(
                TLName("Harem jeans", {"EU-en": "Harem trousers"}),
                TLCost(dollars=36.00, scale=True),
            ),
            TLItem("Hiking outfit", TLCost(dollars=56.00, scale=True)),
            TLItem(
                TLName("Hippie clothes", {"EU-en": "Hippy clothes"}),
                TLCost(dollars=32.00, scale=True),
            ),
            TLItem(
                TLName("Hoodie & jeans", {"EU-en": "Hoody & jeans combo"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Hoodie & shorts", {"EU-en": "Hoody & shorts combo"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem("Jellyfish T-shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Jjimjilbang clothes", 19900, "KR"),
            TLItem(
                TLName("Kiddie smock", {"EU-en": "Nursery uniform"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem(
                TLName("Leather trench coat", {"EU-en": "Long leather coat"}),
                TLCost(dollars=150.00, scale=True),
            ),
            TLItem(
                TLName("Leisure wear", {"EU-en": "Leisurewear"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem(
                TLName("Leopard-print scarf", {"EU-en": "Leopard scarf"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem("Long-sleeved T-shirt", TLCost(dollars=15.00, scale=True)),
            TLItem("Long coat", TLCost(dollars=58.00, scale=True)),
            TLItem("Loungewear", TLCost(dollars=19.00, scale=True)),
            TLItem(
                TLName("Overalls", {"EU-en": "Dungarees"}),
                TLCost(dollars=9.90, jpy=980, krw=9900),
            ),
            TLItem(
                TLName("Pajamas", {"EU-en": "Pyjamas"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem("Patterned shorts", TLCost(dollars=65.00, scale=True)),
            TLItem("Picture T-shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Pineapple shirt", TLCost(dollars=25.00, scale=True)),
            TLItem("Pocket shirt", TLCost(dollars=18.00, scale=True)),
            TLItem("Poncho", TLCost(dollars=48.00, scale=True)),
            TLItem("Printed T-shirt", TLCost(dollars=19.00, scale=True)),
            TLItem("Puffy vest", TLCost(dollars=56.00, scale=True)),
            TLItem(
                TLName("Punk-rocker outfit", {"EU-en": "Punk rocker outfit"}),
                TLCost(dollars=89.00, krw=89000),
            ),
            TLItem("Punk outfit", TLCost(dollars=55.50, scale=True)),
            TLItem("Quilted coat", TLCost(dollars=58.00, scale=True)),
            TLItem("Raglan shirt", TLCost(dollars=24.00, scale=True)),
            TLItem("Raincoat", TLCost(dollars=19.00, scale=True)),
            TLItem(
                TLName("Shirt & cardigan", {"EU-en": "T-shirt & cardy combo"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem("Short duffle coat", TLCost(dollars=68.00, scale=True)),
            TLItem(
                TLName("Short leather jacket", {"EU-en": "Leather jacket"}),
                TLCost(dollars=86.00, scale=True),
            ),
            TLItem("Ski suit", TLCost(dollars=56.00, krw=56000)),
            TLItem("Star T-shirt", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem("Striped T-shirt", TLCost(dollars=50.00, scale=True)),
            TLItem(
                TLName("Sweat suit", {"EU-en": "Sweatsuit"}),
                TLCost(dollars=9.90, jpy=980, krw=9900),
            ),
            TLItem("Tracksuit", TLCost(dollars=29.90, jpy=2980, krw=29900)),
            TLItem("Training jacket", TLCost(dollars=28.00, scale=True)),
            TLItem("Turtleneck", TLCost(dollars=24.00, scale=True)),
            TLItem("Varsity jacket", TLCost(dollars=24.00, scale=True)),
            TLItem(
                TLName("Vintage cardigan", {"EU-en": "Cardy & flares combo"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem("Vintage sweatshirt", TLCost(dollars=5.90, jpy=580, krw=5900)),
            TLItem("White shirt", TLCost(dollars=38.00, scale=True)),
            TLItem(
                TLName("Woolly sweater", {"EU-en": "Wooly jumper"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem(
                TLName("Aloha shirt", {"EU-en": "Hawaiian shirt"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem(
                TLName("Ugly holiday sweater", {"EU-en": "Ugly Christmas jumper"}),
                TLCost(dollars=122.50, krw=122500),
            ),
        ]

    @cached_property
    def clothes_formal_wear_masculine(self) -> list[TLItem]:
        """
        The list of formal wear in Tomodachi Life that can be construed as being masculine, derived from https://tomodachi.fandom.com/wiki/Clothing/Formal_Wear. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of masculine formal wear.
        """
        return [
            TLItem(
                TLName("Ballerino costume", {"EU-en": "Men's ballet outfit"}),
                TLCost(dollars=56.00, scale=True),
            ),
            TLItem("Boys' college sweater", TLCost(dollars=48.00, scale=True)),
            TLItem(
                TLName("Boys' gymnastics clothes", {"EU-en": "Men's gym uniform"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem("Doorman uniform", TLCost(dollars=60.00, scale=True)),
            TLItem(
                TLName("Magician costume", {"EU-en": "Formal waistcoat"}),
                TLCost(dollars=77.90, jpy=7770, krw=77900),
            ),
            TLItem(
                TLName("Messenger uniform", {"EU-en": "Courier uniform"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem("Snowboarding outfit", TLCost(dollars=48.00, scale=True)),
            TLItem("Waiter's apron", TLCost(dollars=29.90, jpy=2980, krw=29900)),
            TLItem(
                TLName("Wet suit", {"EU-en": "Wetsuit"}),
                TLCost(dollars=55.00, scale=True),
            ),
        ]

    @cached_property
    def clothes_formal_wear_feminine(self) -> list[TLItem]:
        """
        The list of formal wear in Tomodachi Life that can be construed as being feminine, derived from https://tomodachi.fandom.com/wiki/Clothing/Formal_Wear. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of feminine formal wear.
        """
        return [
            TLItem("Ballerina outfit", TLCost(dollars=65.00, scale=True)),
            TLItem("Bunny girl set", TLCost(jpy=10000, krw=100000)),
            TLItem(
                "Checked skirt",
                TLCost(eur=55.00, gbp=55.00, aud=55.00, jpy=5500, krw=55000),
            ),
            TLItem("Cheerleader uniform", TLCost(dollars=70.00, scale=True)),
            TLItem(
                TLName("Cute maid outfit", {"EU-en": "Short maid outfit"}),
                TLCost(dollars=56.00, scale=True),
            ),
            TLItem("Girls' college sweater", TLCost(dollars=48.00, scale=True)),
            TLItem(
                TLName("Girls' gymnastics clothes", {"EU-en": "Women's gym uniform"}),
                TLCost(dollars=38.00, scale=True),
            ),
            TLItem(
                TLName("Ice-skating costume", {"EU-en": "Ice skater outfit"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem(
                "Ladies' police set",
                TLCost(eur=52.00, gbp=52.00, aud=52.00, jpy=5200, krw=52000),
            ),
            TLItem("Maid outfit", TLCost(dollars=58.00, scale=True)),
            TLItem("Office outfit", TLCost(dollars=28.00, scale=True)),
            TLItem(
                TLName("Silk blouse", {"EU-en": "Blouse & skirt combo"}),
                TLCost(dollars=58.00, scale=True),
            ),
            TLItem(
                TLName("Sunday dress", {"EU-en": "Sunday outfit"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem("Tennis dress", TLCost(dollars=56.00, scale=True)),
            TLItem("Two-tone dress", TLCost(dollars=46.00, scale=True)),
            TLItem("Waitress uniform", TLCost(dollars=29.90, jpy=2980, krw=29900)),
            TLItem("Yoga outfit", TLCost(dollars=20.00, scale=True)),
        ]

    @cached_property
    def clothes_formal_wear_unisex(self) -> list[TLItem]:
        """
        The list of formal wear in Tomodachi Life that can be construed as being neither masculine nor feminine, derived from https://tomodachi.fandom.com/wiki/Clothing/Formal_Wear. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of unisex formal wear.
        """
        return [
            TLItem("Aerobics outfit", TLCost(dollars=20.00, scale=True)),
            TLItem("Baseball uniform", TLCost(dollars=48.00, scale=True)),
            TLItem("Basketball uniform", TLCost(dollars=24.00, scale=True)),
            TLItem("Bowling shirt", TLCost(dollars=50.00)),
            TLItem(
                TLName("Boxing outfit", {"EU-en": "Boxer trunks"}),
                TLCost(dollars=16.00, scale=True),
            ),
            TLItem("Business shirt", TLCost(dollars=56.00, scale=True)),
            TLItem("Captain uniform", TLCost(dollars=120.00, krw=120000)),
            TLItem("Carpenter uniform", TLCost(eur=35.00, krw=35000)),
            TLItem("Chauffeur uniform", TLCost(dollars=55.00, scale=True)),
            TLItem("Chef outfit", TLCost(dollars=42.00, scale=True)),
            TLItem("Construction worker clothes", 3500, "JP"),
            TLItem(
                TLName("Corner-store uniform", {"EU-en": "Corner shop uniform"}),
                TLCost(dollars=36.90, jpy=3680),
            ),
            TLItem(
                TLName("Coveralls", {"EU-en": "Overalls"}),
                TLCost(dollars=19.00, scale=True),
            ),
            TLItem("Cycling outfit", TLCost(dollars=28.00, scale=True)),
            TLItem("Dance clothes", TLCost(dollars=56.00, scale=True)),
            TLItem("Farmer outfit", TLCost(dollars=38.00, krw=38000)),
            TLItem("Firefighter uniform", TLCost(dollars=70.00, scale=True)),
            TLItem("Flight-attendant uniform", TLCost(dollars=78.00, scale=True)),
            TLItem(
                TLName("Foot-guard uniform", {"EU-en": "Guardsman uniform"}),
                TLCost(dollars=80.00, krw=80000),
            ),
            TLItem("Goalkeeper uniform", TLCost(dollars=28.00, scale=True)),
            TLItem("Golf outfit", TLCost(dollars=38.00, scale=True)),
            TLItem("Guard uniform", TLCost(36.00, jpy=3600)),
            TLItem("Gym clothes", TLCost(dollars=18.00, scale=True)),
            TLItem("Hakama", 10000, "JP"),
            TLItem(
                TLName("Jockey outfit", {"EU-en": "Showjumping outfit"}),
                TLCost(dollars=68.00, krw=68000),
            ),
            TLItem("Judge robe", TLCost(dollars=58.00, krw=58000)),
            TLItem("Judo uniform", TLCost(dollars=27.90, jpy=2780, krw=27900)),
            TLItem(
                TLName("Kung-fu outfit", {"EU-en": "Kung fu outfit"}),
                TLCost(dollars=40.00, scale=True),
            ),
            TLItem(
                TLName("Lab coat", {"EU-en": "Doctor's coat"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem(
                TLName("Long-day outfit", {"EU-en": "Long day outfit"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem("Loose-tie outfit", TLCost(dollars=55.00, scale=True)),
            TLItem("Nurse uniform", TLCost(dollars=60.00, scale=True)),
            TLItem("Pilot uniform", TLCost(dollars=50.00, scale=True)),
            TLItem(
                TLName(
                    "Police uniform",
                    {"EU-en": "Police officer set", "JP-en": "Police officer set"},
                ),
                TLCost(dollars=56.00, scale=True),
            ),
            TLItem("Postal uniform", TLCost(55.00, jpy=5500)),
            TLItem(
                TLName("Race-driver suit", {"EU-en": "Racing driver suit"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem("Referee uniform", TLCost(dollars=28.00)),
            TLItem("Roller-skater outfit", TLCost(dollars=28.00, scale=True)),
            TLItem("Rubber waders", TLCost(dollars=19.90, jpy=1980, krw=19900)),
            TLItem(
                TLName("Running gear", {"EU-en": "Marathon outfit"}),
                TLCost(dollars=25.00, scale=True),
            ),
            TLItem("Sailor outfit", TLCost(dollars=45.00, krw=45000)),
            TLItem("Sailor uniform (long-sleeved)", 5000, "JP"),
            TLItem("Samue", 2500, "JP"),
            TLItem(
                TLName("Soccer-referee uniform", {"EU-en": "Football referee uniform"}),
                TLCost(dollars=28.00, krw=28000),
            ),
            TLItem(
                TLName("Soccer uniform", {"EU-en": "Football uniform"}),
                TLCost(dollars=28.00, scale=True),
            ),
            TLItem("Sous-chef outfit", TLCost(50.00, jpy=5000)),
            TLItem("Suit", TLCost(dollars=58.00, scale=True)),
            TLItem("Table-tennis uniform", TLCost(dollars=38.00, scale=True)),
            TLItem("Taekwondo uniform", 27900, "KR"),
            TLItem("Tennis outfit", TLCost(56.00, jpy=5600, krw=56000)),
            TLItem(
                TLName("Wrestling outfit", {"EU-en": "Wrestling costume"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Wrestling singlet", {"EU-en": "Wrestling uniform"}),
                TLCost(dollars=50.00, krw=50000),
            ),
            TLItem(
                TLName("Clothing uniform", {"EU-en": "Clothing shop uniform"}),
                TLCost(dollars=40.00, scale=True),
            ),
            TLItem(
                TLName("Food Mart uniform", {"EU-en": "Supermarket uniform"}),
                TLCost(dollars=40.00, scale=True),
            ),
            TLItem(
                TLName("Football uniform", {"EU-en": "American football uniform"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Hats uniform", {"EU-en": "Headwear shop uniform"}),
                TLCost(dollars=40.00, scale=True),
            ),
            TLItem("Import Wear uniform", TLCost(dollars=40.00, scale=True)),
            TLItem(
                TLName("Interiors uniform", {"EU-en": "Interiors shop uniform"}),
                TLCost(dollars=40.00, scale=True),
            ),
            TLItem("Military training uniform", 30000, "KR"),
            TLItem("Nintendo uniform", TLCost(dollars=100, scale=True)),
            TLItem("Pawn Shop uniform", TLCost(dollars=40.00, scale=True)),
        ]

    @cached_property
    def clothes_costumes_masculine(self) -> list[TLItem]:
        """
        The list of costumes in Tomodachi Life that can be construed as being masculine, derived from https://tomodachi.fandom.com/wiki/Clothing/Costumes. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of masculine costumes.
        """
        return [
            TLItem(
                TLName("Arabian-prince outfit", {"EU-en": "Arabian prince outfit"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem("Cool-pop-star outfit", TLCost(dollars=250.00, scale=True)),
            TLItem(
                TLName("Cowboy duds", {"EU-en": "Cowboy outfit"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem("Dragon robe", 500000, "KR"),
            TLItem(
                TLName("Friendly-pop-star outfit", {"EU-en": "Fresh pop star outfit"}),
                TLCost(dollars=150.00, scale=True),
            ),
            TLItem("Gladiator armor", TLCost(dollars=150.00, krw=150000)),
            TLItem("Military uniform set", 80000, "KR"),
            TLItem(
                TLName("Napoleonic clothes", {"EU-en": "Napoleonic Uniform"}),
                TLCost(dollars=100.00, krw=100000),
            ),
            TLItem("Prince Charming outfit", TLCost(dollars=600.00, scale=True)),
            TLItem(
                TLName("Santa suit", {"EU-en": "Santa costume"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem(
                TLName("Superhero costume", {"EU-en": "Masked-hero costume"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem("Victorian suit", TLCost(dollars=68.00, scale=True)),
            TLItem("Wild-pop star outfit", TLCost(dollars=250.00, scale=True)),
        ]

    @cached_property
    def clothes_costumes_feminine(self) -> list[TLItem]:
        """
        The list of costumes in Tomodachi Life that can be construed as being feminine, derived from https://tomodachi.fandom.com/wiki/Clothing/Costumes. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of feminine costumes.
        """
        return [
            TLItem("Alpine dress", TLCost(dollars=50.00, scale=True)),
            TLItem(
                TLName("Arabian-princess outfit", {"EU-en": "Arabian princess outfit"}),
                TLCost(dollars=78.00, scale=True),
            ),
            TLItem(
                TLName("Basic swimsuit", {"EU-en": "Plain swimming costume"}),
                TLCost(dollars=48.00, scale=True),
            ),
            TLItem("Chima jeogori", 150000, "KR"),
            TLItem("Chinese dress", TLCost(dollars=69.00, scale=True)),
            TLItem("Cleaning apron", TLCost(dollars=12.90, jpy=1280, krw=12900)),
            TLItem(
                TLName("Cowgirl duds", {"EU-en": "Cowgirl outfit"}),
                TLCost(dollars=42.00, scale=True),
            ),
            TLItem(
                TLName("Cute-pop-star outfit", {"EU-en": "Cute pop star outfit"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem("Dangui", 500000, "KR"),
            TLItem("Fairy costume", TLCost(dollars=500.00, scale=True)),
            TLItem(
                TLName("Flapper dress", {"EU-en": "Flapper outfit"}),
                TLCost(dollars=80.00, krw=80000),
            ),
            TLItem("Grass skirt", TLCost(dollars=20.00, scale=True)),
            TLItem("Haramaki", 980, "JP"),
            TLItem("Jewel dress", TLCost(dollars=9900.00, scale=True)),
            TLItem("Jūnihitoe", 200000, "JP"),
            TLItem("Maid's clothing set", 80000, "KR"),
            TLItem("Mermaid costume", TLCost(dollars=100.00, scale=True)),
            TLItem("Pop-star outfit", TLCost(dollars=150.00, scale=True)),
            TLItem("Princess outfit", TLCost(dollars=1000.00, scale=True)),
            TLItem(
                TLName("Samba dress", {"EU-en": "Samba outfit"}),
                TLCost(dollars=80.00, krw=80000),
            ),
            TLItem(
                TLName("Santa dress", {"EU-en": "Ladie's Santa Costume"}),
                TLCost(100.00, aud=100.00, jpy=10000, krw=100000),
            ),
            TLItem("Sari", TLCost(dollars=60.00, scale=True)),
            TLItem("Stage-performer dress", TLCost(dollars=98.00, scale=True)),
            TLItem(
                TLName("Superheroine costume", {"EU-en": "Girls' hero costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Vagabond outfit", TLCost(dollars=2.00, scale=True)),
            TLItem("Versailles court dress", TLCost(dollars=500.00, scale=True)),
            TLItem("Victorian dress", TLCost(dollars=68.00, scale=True)),
            TLItem(
                TLName("Witch costume", {"EU-en": "Witch outfit"}),
                TLCost(dollars=23.00, scale=True),
            ),
            TLItem("Patterned kimono", TLCost(dollars=560.00, jpy=56000)),
            TLItem(
                TLName("Vacay swimsuit", {"EU-en": "Holiday swimwear"}),
                TLCost(dollars=29.90, jpy=2980, krw=29900),
            ),
            TLItem(
                TLName("Wedding dress", {"EU-en": "Wedding outfit"}),
                TLCost(dollars=3500.00, scale=True),
            ),
        ]

    @cached_property
    def clothes_costumes_unisex(self) -> list[TLItem]:
        """
        The list of costumes in Tomodachi Life that can be construed as being neither masculine nor feminine, derived from https://tomodachi.fandom.com/wiki/Clothing/Costumes. British pound and Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of unisex costumes.
        """
        return [
            TLItem("Aristocratic clothes", TLCost(dollars=560.00, scale=True)),
            TLItem(
                TLName("Astronaut suit", {"EU-en": "Spacesuit"}),
                TLCost(dollars=4000.00, scale=True),
            ),
            TLItem(
                TLName("Baby-chick suit", {"EU-en": "Chick costume"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem("Bajijeogori", 35000, "KR"),
            TLItem(
                TLName("Banana suit", {"EU-en": "Banana costume"}),
                TLCost(dollars=70.00, krw=70000),
            ),
            TLItem(
                TLName("Bear suit", {"EU-en": "Bear costume"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Bee suit", {"EU-en": "Bee costume"}),
                TLCost(dollars=83.00, scale=True),
            ),
            TLItem(
                TLName("Bodysuit", {"EU-en": "Body suit set"}),
                TLCost(dollars=9.90, jpy=980, krw=9900),
            ),
            TLItem(
                TLName("Calico-cat suit", {"EU-en": "Cat costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Cat suit", {"EU-en": "Plain cat costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Caveman outfit", TLCost(dollars=56.00, scale=True)),
            TLItem("Colonial uniform", TLCost(dollars=80.00, krw=80000)),
            TLItem(
                TLName("Comedian outfit", {"EU-en": "Entertainer outfit"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem("Daimyo's clothes", 50000, "JP"),
            TLItem(
                TLName("Dinosaur suit", {"EU-en": "Dinosaur costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Dog suit", {"EU-en": "Guard dog costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Dopo", 65000, "KR"),
            TLItem("Dotera", 1580, "JP"),
            TLItem("Elf outfit", TLCost(dollars=58.00, scale=True)),
            TLItem("Flower kimono", TLCost(dollars=500.00, scale=True)),
            TLItem(
                TLName("Future suit", {"EU-en": "Future outfit"}),
                TLCost(dollars=220.00, scale=True),
            ),
            TLItem("Ghost costume", TLCost(eur=50.00, gbp=50.00, aud=50.00, krw=50000)),
            TLItem("Gnome outfit", TLCost(dollars=60.00, krw=60000)),
            TLItem("Gwanbok", 200000, "KR"),
            TLItem(
                "Half suit", TLCost(eur=5.90, gbp=5.90, aud=5.90, jpy=580, krw=5900)
            ),
            TLItem(
                TLName("Hamster suit", {"EU-en": "Hamster costume"}),
                TLCost(dollars=80.00, scale=True),
            ),
            TLItem("Happi", 2400, "JP"),
            TLItem("Hot-dog suit", TLCost(dollars=65.00)),
            TLItem(
                TLName(
                    "General Armor clothing set", {"KR-en": "Jang-gun gab-os seteu"}
                ),
                180000,
                "KR",
            ),
            TLItem("Jester outfit", TLCost(dollars=28.00, scale=True)),
            TLItem("Kappa set", 8000, "JP"),
            TLItem(
                TLName("Kilt", {"EU-en": "Highland outfit"}),
                TLCost(dollars=100.00, krw=100000),
            ),
            TLItem(
                TLName("Kung-fu shirt", {"EU-en": "Kung fu shirt"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Ladybug suit", {"EU-en": "Ladybird costume"}),
                TLCost(dollars=100.00, krw=100000),
            ),
            TLItem(
                TLName("Metallic bodysuit", {"EU-en": "Metallic body set"}),
                TLCost(dollars=19.90, jpy=1980, krw=19900),
            ),
            TLItem("Monpe hakama", TLCost(jpy=2800, krw=28000)),
            TLItem("Muscle suit", TLCost(dollars=150.00, scale=True)),
            TLItem(
                TLName("Ninja suit", {"EU-en": "Ninja outfit"}),
                TLCost(dollars=58.00, jpy=5800),
            ),
            TLItem(
                TLName("Panda suit", {"EU-en": "Panda costume"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem(
                TLName("Penguin suit", {"EU-en": "Penguin costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Phantom outfit", TLCost(dollars=100.00, scale=True)),
            TLItem("Pharaoh costume", TLCost(dollars=100.00, krw=100000)),
            TLItem("Pirate outfit", TLCost(dollars=100.00, scale=True)),
            TLItem(
                TLName("Prisoner costume", {"EU-en": "Prison uniform"}),
                TLCost(dollars=5.00, scale=True),
            ),
            TLItem(
                TLName("Puppy suit", {"EU-en": "Plain dog costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Robo-hero suit", {"EU-en": "Robo-hero outfit"}),
                TLCost(dollars=150.00, scale=True),
            ),
            TLItem(
                TLName("Robot suit", {"EU-en": "Robot costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Royal costume", {"EU-en": "King set"}),
                TLCost(dollars=5000.00, scale=True),
            ),
            TLItem("Safari outfit", TLCost(dollars=48.00, scale=True)),
            TLItem("Samurai armor", TLCost(dollars=1000.00, jpy=100000)),
            TLItem("Shinsengumi clothes", 5800, "JP"),
            TLItem(
                TLName("Skeleton suit", {"EU-en": "Skeleton costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Snowsuit", {"EU-en": "Eskimo clothes"}),
                TLCost(dollars=100.00, krw=100000),
            ),
            TLItem(
                TLName("Socks-cat suit", {"EU-en": "Socks cat costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Socks-dog suit", {"EU-en": "Socks dog costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Stylish-pop-star outfit", {"EU-en": "Smart pop star outfit"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem(
                TLName("Suit of armor", {"EU-en": "Suit of armour"}),
                TLCost(dollars=1000.00, scale=True),
            ),
            TLItem("Sumo loincloth", TLCost(eur=38.00, gbp=38.00, aud=38.00, jpy=3800)),
            TLItem("Swimsuit", TLCost(dollars=29.90, jpy=2980, krw=29900)),
            TLItem(
                TLName("Tabby-cat suit", {"EU-en": "Stripy cat costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Toga", TLCost(dollars=99.00, scale=True)),
            TLItem(
                TLName("Unitail", {"EU-en": "Unitard"}),
                TLCost(dollars=64.90, jpy=6480, krw=64900),
            ),
            TLItem(
                TLName("Vegas-performer outfit", {"EU-en": "Vegas performer suit"}),
                TLCost(dollars=280.00, scale=True),
            ),
            TLItem("Viking costume", TLCost(dollars=158.00, krw=158000)),
            TLItem(
                TLName("Wizard costume", {"EU-en": "Wizard outfit"}),
                TLCost(dollars=80.00, krw=80000),
            ),
            TLItem("Graduation Ceremony Hakama", 25000, "JP"),
            TLItem(
                TLName("Lederhosen", {"EU-en": "Bavarian outfit"}),
                TLCost(dollars=80.00, scale=True),
            ),
            TLItem("Mummy costume", TLCost(dollars=999.00, scale=True)),
            TLItem(
                TLName("Oni set", {"KR-en": "Dokkaebi (Goblin) set"}),
                TLCost(jpy=5000, krw=50000),
            ),
            TLItem(
                TLName("Pumpkin suit", {"EU-en": "Pumpkin costume"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem("Samurai clothes", TLCost(dollars=77.90, jpy=7770)),
            TLItem("Uncle Sam costume", TLCost(dollars=100.00, scale=True)),
        ]

    @cached_property
    def gifts_base(self) -> list[TLItem]:
        """
        The list of gifts in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Gifts.

        Returns:
            list[TLItem]: The list of gifts.
        """
        return [
            TLItem("Age-o-matic"),
            TLItem("AR camera"),
            TLItem("Bath set"),
            TLItem("Cold medicine"),
            TLItem("Disposable camera"),
            TLItem("Fan"),
            TLItem("Frying pan"),
            TLItem("Hair-color spray"),
            TLItem(TLName("Hypnotizer", {"EU-en": "Hypnotism set"})),
            TLItem("Kaliedoscope"),
            TLItem("Kid-o-matic"),
            TLItem("Mobile"),
            TLItem("Music box"),
            TLItem("Sewing machine"),
            TLItem("Slide Puzzle"),
            TLItem("Stomach medicine"),
            TLItem("Swing"),
            TLItem("Travel ticket"),
        ]

    @cached_property
    def treasures_base(self) -> list[TLItem]:
        """
        The list of treasures in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Treasures. Australian dollar costs are assumed to be the same as other dollar costs.

        Returns:
            list[TLItem]: The list of treasures.
        """
        return [
            TLItem("Abacus", TLCost(dollars=14.00, krw=14000)),
            TLItem("Acorn", TLCost(dollars=0.10, scale=True)),
            TLItem("Ammonite fossil", TLCost(dollars=100.00, scale=True)),
            TLItem(
                TLName("Antique clock", {"EU-en": "Grandfather clock"}),
                TLCost(dollars=260.00, krw=260000),
            ),
            TLItem(
                TLName("Backpack", {"JP-en": "School bag"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem("Balloon", TLCost(dollars=2.00, scale=True)),
            TLItem(
                TLName("Bamboo box", {"EU-en": "Bamboo clothes box"}),
                TLCost(dollars=10.00, scale=True),
            ),
            TLItem(
                TLName("Barbell", {"EU-en": "Dumb-bell"}),
                TLCost(dollars=14.50, jpy=800, krw=14500),
            ),
            TLItem("Basketball", TLCost(dollars=20.00, scale=True)),
            TLItem("Beads", TLCost(dollars=6.00, krw=6000)),
            TLItem("Bell", TLCost(dollars=4.00, scale=True)),
            TLItem(
                TLName("Binoculars", {"EU-en": "Pair of binoculars"}),
                TLCost(dollars=60.00, scale=True),
            ),
            TLItem("Bojobo Dolls", TLCost(jpy=2000, krw=20000)),
            TLItem("Bonsai tree", TLCost(dollars=59.00, scale=True)),
            TLItem("Bouquet", TLCost(dollars=40.00, scale=True)),
            TLItem("Bowling ball", TLCost(dollars=35.00, krw=35000)),
            TLItem("Box of matches", TLCost(dollars=1.00, scale=True)),
            TLItem("Box of tissues", TLCost(dollars=1.00, scale=True)),
            TLItem(
                TLName("Brass key", {"EU-en": "Random key", "JP-en": "Random key"}),
                TLCost(dollars=5.00, scale=True),
            ),
            TLItem("Broom", TLCost(dollars=3.00, krw=3000)),
            TLItem(
                TLName("Cane", {"EU-en": "Walking stick"}),
                TLCost(dollars=30.00, scale=True),
            ),
            TLItem("Carnation", TLCost(dollars=10.00, scale=True)),
            TLItem(
                TLName("Chattery teeth", {"EU-en": "Set of wind-up teeth"}),
                TLCost(dollars=2.50, krw=2500),
            ),
            TLItem(
                TLName("Chess piece", {"JP-en": "Shogi king"}),
                TLCost(dollars=10.00, scale=True),
            ),
            TLItem("Chopsticks holder", 700, "JP"),
            TLItem(
                TLName("Clay figure", {"JP-en": "Haniwa"}),
                TLCost(dollars=100.00, scale=True),
            ),
            TLItem(
                TLName("Clothespin", {"EU-en": "Clothes peg"}),
                TLCost(dollars=0.30, jpy=100, krw=1000),
            ),
            TLItem("Collar", TLCost(dollars=7.00, scale=True)),
            TLItem("Comb", TLCost(dollars=2.00, scale=True)),
            TLItem("Compass", TLCost(dollars=3.50, scale=True)),
            TLItem("Conch", TLCost(dollars=80.00, scale=True)),
            TLItem("Copper coin", TLCost(dollars=50.00, scale=True)),
            TLItem(
                TLName("Coral", {"EU-en": "Piece of coral"}),
                TLCost(dollars=1.00, scale=True),
            ),
            TLItem("Cork stopper", TLCost(dollars=1.00, scale=True)),
            TLItem("Cowbell", TLCost(dollars=8.00, scale=True)),
            TLItem(
                TLName("CRT television", {"EU-en": "CRT TV"}),
                TLCost(dollars=39.00, scale=True),
            ),
            TLItem("Crystal", TLCost(dollars=60.00, scale=True)),
            TLItem("Cuckoo clock", TLCost(dollars=130.00, krw=130000)),
            TLItem("Cup and ball", TLCost(dollars=7.80)),
            TLItem("Daruma doll", 2000, "JP"),
            TLItem("Daruma stack game", 780, "JP"),
            TLItem("Desert sand", TLCost(dollars=5.00, jpy=500)),
            TLItem("Diamond", TLCost(dollars=500.00, scale=True)),
            TLItem("Diary", TLCost(dollars=6.00, krw=6000)),
            TLItem(TLName("Die", {"EU-en": "Dice"}), TLCost(dollars=1.50, scale=True)),
            TLItem(
                TLName("Disco ball", {"EU-en": "Mirrorball"}),
                TLCost(dollars=200.00, scale=True),
            ),
            TLItem(
                TLName("Disposable diaper", {"EU-en": "Disposable nappy"}),
                TLCost(dollars=0.50, scale=True),
            ),
            TLItem("Dol Hareubang", 10000, "KR"),
            TLItem("Domino", TLCost(dollars=2.00)),
            TLItem("Door handle", TLCost(dollars=7.00, scale=True)),
            TLItem("Dowsing rods", TLCost(dollars=1.50, scale=True)),
            TLItem("Engagement ring", TLCost(dollars=500.00, scale=True)),
            TLItem("Expensive-looking vase", TLCost(dollars=400.00, scale=True)),
            TLItem("Fan", 30000, "KR"),
            TLItem("Fancy soap", TLCost(dollars=10.00, scale=True)),
            TLItem(
                TLName("Faucet", {"EU-en": "Tap"}), TLCost(dollars=4.80, scale=True)
            ),
            TLItem("Finger trap", TLCost(dollars=0.50)),
            TLItem(
                TLName("Flashlight", {"EU-en": "Torch"}),
                TLCost(dollars=5.50, scale=True),
            ),
            TLItem("Foam hand", TLCost(dollars=1.20)),
            TLItem(
                TLName("Folding fan", {"JP-en": "Kyoto fan"}),
                TLCost(dollars=20.00, scale=True),
            ),
            TLItem("Footbag", TLCost(dollars=4.20)),
            TLItem("Fountain pen", TLCost(dollars=100.00, scale=True)),
            TLItem("Four-leaf clover", TLCost(dollars=10.00, scale=True)),
            TLItem(
                TLName("Game & Watch", {"EU-en": "Game & Watch system"}),
                TLCost(dollars=60.00, scale=True),
            ),
            TLItem("Game Boy", TLCost(dollars=125.00, scale=True)),
            TLItem("Geode", TLCost(dollars=41.00)),
            TLItem(
                TLName("Glass ornament", {"EU-en": "Cut-glass ornament"}),
                TLCost(dollars=50.00, scale=True),
            ),
            TLItem("Glass slipper", TLCost(dollars=30.00, scale=True)),
            TLItem("Globe", 24.00, "NA"),
            TLItem(
                TLName("Gold bar", {"EU-en": "Gold ingot"}),
                TLCost(dollars=1000.00, scale=True),
            ),
            TLItem("Gold coin", TLCost(dollars=200.00, scale=True)),
            TLItem("Gold earrings", TLCost(dollars=150.00, scale=True)),
            TLItem("Golden pig", 1000000, "KR"),
            TLItem(
                TLName("Historical bust", {"EU-en": "Bust"}),
                TLCost(dollars=500.00, krw=500000),
            ),
            TLItem("Home-run ball", TLCost(dollars=50.00, scale=True)),
            TLItem("Hotel toiletries", TLCost(dollars=3.00, scale=True)),
            TLItem("Hourglass", TLCost(dollars=9.50, scale=True)),
            TLItem(
                TLName("Hula girl", {"EU-en": "Bobblehead doll"}),
                TLCost(dollars=10.50, krw=10500),
            ),
            TLItem(
                TLName("Inner tube", {"EU-en": "Rubber ring"}),
                TLCost(dollars=12.00, scale=True),
            ),
            TLItem(
                TLName("Jewelry box", {"EU-en": "Jewellery box"}),
                TLCost(dollars=7.00, scale=True),
            ),
            TLItem(
                TLName("Jump rope", {"EU-en": "Skipping rope"}),
                TLCost(dollars=4.80, scale=True),
            ),
            TLItem("Kangaroo warning sign", TLCost(dollars=60.00)),
            TLItem(
                TLName("Kneaded eraser", {"EU-en": "Putty rubber"}),
                TLCost(dollars=1.00, scale=True),
            ),
            TLItem(
                TLName("Krama scarf", {"EU-en": "Krama headscarf"}),
                TLCost(dollars=15.00, scale=True),
            ),
            TLItem("Lantern", TLCost(dollars=15.00, krw=15000)),
            TLItem("Leather gloves", TLCost(jpy=6000, krw=60000)),
            TLItem("Lipstick", TLCost(dollars=20.00, scale=True)),
            TLItem("Loofah", TLCost(dollars=3.00, scale=True)),
            TLItem("Luck Charm", 1000, "JP"),
            TLItem(
                TLName("Lucky cat", {"EU-en": "Waving cat"}),
                TLCost(dollars=57.00, jpy=5700),
            ),
            TLItem("Lump of coal", TLCost(dollars=0.10, krw=100), trash=True),
            TLItem("Magnifying glass", TLCost(dollars=7.00, scale=True)),
            TLItem("Mahjong piece", 200, "JP"),
            TLItem("Manhole cover", TLCost(dollars=50.00, scale=True)),
            TLItem("Marble", TLCost(dollars=1.00, scale=True)),
            TLItem("Marionette", TLCost(dollars=50.00, scale=True)),
            TLItem("Martian rock", TLCost(dollars=100.00, scale=True)),
            TLItem("Melodica", TLCost(jpy=2500, krw=25000)),
            TLItem(
                TLName(
                    "Metal spatula",
                    {"EU-en": "Fish slice", "JP-en": "Big wooden spoon"},
                ),
                TLCost(dollars=2.00, scale=True),
            ),
            TLItem("Microchip", TLCost(dollars=10.00, scale=True)),
            TLItem("Mosquito coil", TLCost(jpy=2000, krw=20000)),
            TLItem("Mug", TLCost(dollars=8.00, scale=True)),
            TLItem(
                TLName("NES", {"EU-en": "NES console", "JP-en": "Famicom"}),
                TLCost(dollars=148.00, scale=True),
            ),
            TLItem("Nintendo DS card", 3800, "JP"),
            TLItem("Nutcracker", 75.00, "NA"),
            TLItem("Origami crane", TLCost(dollars=1.00, scale=True)),
            TLItem("Packet of tissues", TLCost(dollars=1.00, scale=True)),
            TLItem(
                TLName("Paint bucket", {"EU-en": "Tin of paint"}),
                TLCost(dollars=9.80, scale=True),
            ),
            TLItem(
                TLName("Pan flute", {"EU-en": "Pan pipes"}),
                TLCost(dollars=35.00, scale=True),
            ),
            TLItem("Pearl necklace", TLCost(dollars=100.00, scale=True)),
            TLItem("Pebble", TLCost(dollars=0.10, scale=True)),
            TLItem("Perfume", TLCost(dollars=38.00, scale=True)),
            TLItem(
                TLName("Phonograph", {"EU-en": "Gramophone"}),
                TLCost(dollars=300.00, krw=300000),
            ),
            TLItem(
                "Piece of Berlin Wall",
                TLCost(eur=6.00, gbp=6.00, aud=6.00, jpy=600, krw=6000),
            ),
            TLItem(
                TLName("Pinecone", {"EU-en": "Pine cone"}),
                TLCost(dollars=0.10, scale=True),
            ),
            TLItem("Plastic trophy", TLCost(dollars=20.00, scale=True)),
            TLItem(
                TLName("Plush panda", {"EU-en": "Panda toy"}),
                TLCost(dollars=30.00, scale=True),
            ),
            TLItem("Pocket watch", TLCost(dollars=65.00, scale=True)),
            TLItem("Potty", TLCost(dollars=15.00, scale=True)),
            TLItem(
                TLName("R.O.B.", {"JP-en": "Famicom Robot"}),
                TLCost(dollars=198.00, jpy=9800, krw=198000),
            ),
            TLItem("Receipt", TLCost(dollars=0.10, scale=True)),
            TLItem("Red thread", TLCost(dollars=1.00, scale=True)),
            TLItem("Rocking horse", TLCost(dollars=80.00, krw=80000)),
            TLItem("Rose", TLCost(dollars=10.00, scale=True)),
            TLItem(
                TLName("Rubber ducky", {"EU-en": "Rubber duck"}),
                TLCost(dollars=4.00, scale=True),
            ),
            TLItem("Rubber rope", 7000, "KR"),
            TLItem("Ruby pendant", TLCost(dollars=100.00, scale=True)),
            TLItem("Russian dolls", TLCost(dollars=30.00, scale=True)),
            TLItem("Scented candle", TLCost(dollars=3.00, scale=True)),
            TLItem("Scourer", TLCost(dollars=1.00, scale=True)),
            TLItem("Screw", TLCost(dollars=0.50, scale=True)),
            TLItem("Seashell", TLCost(dollars=1.00, scale=True)),
            TLItem("Security camera", TLCost(dollars=75.00, scale=True)),
            TLItem("Shell necklace", TLCost(dollars=3.00)),
            TLItem("Silver bracelet", TLCost(dollars=80.00, scale=True)),
            TLItem("Silver coin", TLCost(dollars=100.00, scale=True)),
            TLItem(
                TLName("Skeleton key chain", {"EU-en": "Skeleton key ring"}),
                TLCost(dollars=4.80, scale=True),
            ),
            TLItem("Smelly sock", TLCost(dollars=0.10, scale=True), trash=True),
            TLItem("Snow globe", TLCost(dollars=19.80, scale=True)),
            TLItem("Solar panel", TLCost(dollars=100.00, scale=True)),
            TLItem("Spinning top", TLCost(dollars=3.50, scale=True)),
            TLItem(
                TLName("Spinning toy", {"JP-en": "Yo-yo"}),
                TLCost(dollars=6.00, scale=True),
            ),
            TLItem(
                TLName("Squirt gun", {"EU-en": "Water pistol"}),
                TLCost(dollars=4.80, scale=True),
            ),
            TLItem("Stethoscope", TLCost(dollars=25.00, scale=True)),
            TLItem("Stone pig", 100, "KR"),
            TLItem(
                TLName("Sunset key chain", {"EU-en": "Key ring"}),
                TLCost(dollars=4.80, scale=True),
            ),
            TLItem(
                TLName(
                    "Super Scope", {"EU-en": "Nintendo Scope", "JP-en": "Super Scope"}
                ),
                TLCost(dollars=95.00, scale=True),
            ),
            TLItem("Swimming certificate", TLCost(dollars=0.30)),
            TLItem("Takoyaki maker", 3000, "JP"),
            TLItem("Tanuki figure", 1200, "JP"),
            TLItem("Tape player", 12.00, "NA"),
            TLItem(
                TLName("Teapot", {"EU-en": "Kettle"}), TLCost(dollars=19.80, scale=True)
            ),
            TLItem("Teddy bear", TLCost(dollars=30.00, scale=True)),
            TLItem(
                TLName("Toilet paper", {"EU-en": "Roll of toilet paper"}),
                TLCost(dollars=1.00, scale=True),
            ),
            TLItem("Toothbrush", TLCost(dollars=2.00, scale=True)),
            TLItem(
                "Totem pole",
                TLCost(eur=60.00, gbp=60.00, aud=60.00, jpy=6000, krw=60000),
            ),
            TLItem(
                TLName(
                    "Toy robot", {"EU-en": "Tin robot toy", "JP-en": "Tin robot toy"}
                ),
                TLCost(dollars=10.00, scale=True),
            ),
            TLItem("Tulip", TLCost(dollars=4.80, scale=True)),
            TLItem("Virtual Boy", TLCost(dollars=150.00, scale=True)),
            TLItem("Vuvuzela", TLCost(dollars=8.50, krw=8500)),
            TLItem("Wet towel", TLCost(jpy=1000, krw=10000)),
            TLItem(
                TLName("Whiteboard eraser", {"JP-en": "Blackboard eraser"}),
                TLCost(dollars=10.00, scale=True),
            ),
            TLItem("Whoopee cushion", TLCost(dollars=5.00, scale=True)),
            TLItem("Wind chime", TLCost(dollars=10.00, scale=True)),
            TLItem(
                "Wooden bear statue",
                TLCost(eur=60.00, gbp=60.00, aud=60.00, jpy=6000, krw=60000),
            ),
            TLItem("Wooden spoon", TLCost(dollars=6.00, scale=True)),
            # Golden spoon, Family album, Bronze trophy, Silver trophy, Gold trophy and Platinum trophy are not for sale
        ]

    @cached_property
    def level_up_items_base(self) -> list[TLItem]:
        """
        The list of level up items in Tomodachi Life, derived from https://tomodachi.fandom.com/wiki/Level-Up_Gifts.

        Returns:
            list[TLItem]: The list of level up items.
        """
        return [
            TLItem("Ballad song"),
            TLItem("Ballet manual"),
            TLItem("Baseball bat"),
            TLItem("Beauty kit"),
            TLItem("Book"),
            TLItem(TLName("Bubble blower", {"EU-en": "Bubbles"})),
            TLItem("CD"),
            TLItem(TLName("Cell phone", {"EU-en": "Mobile Phone"})),
            TLItem(TLName("Fishing pole", {"EU-en": "Fishing rod"})),
            TLItem(TLName("Golf club", {"EU-en": "Golf clubs"})),
            TLItem("Guitar"),
            TLItem("Heavy Metal song"),
            TLItem(TLName("Hula-dancing manual", {"EU-en": "Hula Dancing Manual"})),
            TLItem("Kite"),
            TLItem("Laptop"),
            TLItem("Light green interior"),
            TLItem("Maracas"),
            TLItem("Metal detector"),
            TLItem("Mirror"),
            TLItem("Modern Asian interior"),
            TLItem("Musical song"),
            TLItem("Natural wood interior"),
            TLItem("Nintendo 3DS XL"),
            TLItem("Opera song"),
            TLItem("Phrase"),
            TLItem("Plant interior"),
            TLItem("$10 pocket money"),
            TLItem("$50 pocket money"),
            TLItem("$100 pocket money"),
            TLItem("Pop song"),
            TLItem(TLName("Punching bag", {"EU-en": "Punchbag"})),
            TLItem("Rap song"),
            TLItem("Regular family interior"),
            TLItem(TLName("Rent-a-cat coupon", {"EU-en": "Cat Voucher"})),
            TLItem(TLName("Rent-a-dog coupon", {"EU-en": "Dog Voucher"})),
            TLItem("Rock & Roll song"),
            TLItem("Scale"),
            TLItem("Skateboard"),
            TLItem(TLName("Soccer ball", {"EU-en": "Football"})),
            TLItem("Study kit"),
            TLItem("Techno song"),
            TLItem("Tennis racket"),
            TLItem("Tiled interior"),
            TLItem("Treadmill"),
            TLItem("Wii U"),
            TLItem("Yoga manual"),
        ]

    def is_item_in_region(self, item: TLItem) -> bool:
        """
        Checks whether a Tomodachi Life item may be valid for the selected region and trash options. Also requires the use of `get_item_cost()` to check for validity.

        Args:
            item (TLItem): The item to check.

        Returns:
            bool: Whether the item is valid for the selected region.
        """
        region: int = self.archipelago_options.tomodachi_life_region.value
        if not bool(self.archipelago_options.tomodachi_life_trash.value) and item.trash:
            return False
        return (
            item.region is None
            or (
                region == TomodachiLifeRegion.option_north_america
                and item.region == "NA"
            )
            or (
                (
                    region == TomodachiLifeRegion.option_europe
                    or region == TomodachiLifeRegion.option_united_kingdom
                    or region == TomodachiLifeRegion.option_australia
                )
                and item.region == "EU"
            )
            or (region == TomodachiLifeRegion.option_japan and item.region == "JP")
            or (region == TomodachiLifeRegion.option_korea and item.region == "KR")
        )

    def get_item_name(self, item: TLItem) -> str:
        """
        Extracts the name of a Tomodachi Life item based on the selected region.

        Args:
            item (TLItem): The item to extract the name from.

        Returns:
            str: The name of the item.
        """
        if isinstance(item.name, str):
            return item.name
        language: int = self.archipelago_options.tomodachi_life_language.value
        show_non_english: bool = bool(
            self.archipelago_options.tomodachi_life_special_characters.value
        )
        region: int = self.archipelago_options.tomodachi_life_region.value
        item_name: str = item.name.na
        if language != TomodachiLifeLanguage.option_north_america:
            if "EU-en" in item.name.other.keys():
                item_name = item.name.other["EU-en"]
            if (
                language == TomodachiLifeLanguage.option_japan
                and "JP-en" in item.name.other.keys()
            ):
                item_name = item.name.other["JP-en"]
            elif (
                language == TomodachiLifeLanguage.option_korea
                and "KR-en" in item.name.other.keys()
            ):
                item_name = item.name.other["KR-en"]
        if (
            show_non_english
            and region == TomodachiLifeRegion.option_japan
            and "JP" in item.name.other.keys()
        ):
            item_name += f" ({item.name.other['JP']})"
        return item_name

    def get_item_cost(self, item: TLItem) -> float | int | None:
        """
        Extracts the cost of a Tomodachi Life item based on the selected region. This method can return a None cost, and if so, the item is not valid for the selected region.

        Args:
            item (TLItem): The item to extract the cost from.

        Returns:
            float | int | None: The cost of the item, or None if the item is not valid for the selected region.
        """
        if not isinstance(item.cost, TLCost):
            return item.cost
        region: int = self.archipelago_options.tomodachi_life_region.value
        if region == TomodachiLifeRegion.option_north_america:
            if item.cost.usd is not None:
                return item.cost.usd
            return item.cost.dollars
        if region == TomodachiLifeRegion.option_europe:
            if item.cost.eur is not None:
                return item.cost.eur
            return item.cost.dollars
        if region == TomodachiLifeRegion.option_united_kingdom:
            if item.cost.gbp is not None:
                return item.cost.gbp
            return item.cost.dollars
        if region == TomodachiLifeRegion.option_australia:
            if item.cost.aud is not None:
                return item.cost.aud
            return item.cost.dollars
        if region == TomodachiLifeRegion.option_japan:
            if item.cost.scale and item.cost.dollars is not None:
                return int(item.cost.dollars * 100)
            return item.cost.jpy
        if region == TomodachiLifeRegion.option_korea:
            if item.cost.scale and item.cost.dollars is not None:
                return int(item.cost.dollars * 1000)
            return item.cost.krw
        return None

    def get_item_strings(self, items: list[TLItem]) -> list[str]:
        """
        Converts a list of Tomodachi Life items with names and costs into a list of strings. The strings are duplicated based on the costs of the items, to ensure that cheaper items are found more commonly in the list.

        Args:
            items (list[TLItem]): The list of items to convert.

        Returns:
            list[str]: The weighted list of strings.
        """
        # Get all items for the given region, also get min and max costs
        region_items: list[tuple[str, float]] = []
        min_cost: float = float("inf")
        max_cost: float = 0
        for item in items:
            if not self.is_item_in_region(item):
                continue
            item_name: str = self.get_item_name(item)
            item_cost: float | int | None = self.get_item_cost(item)
            if item_cost is None:
                continue
            region_items.append((item_name, item_cost))
            min_cost = min(min_cost, item_cost)
            max_cost = max(max_cost, item_cost)
        # Duplicate items based on their costs, cheaper items appear more frequently
        cost_diff: float = max_cost - min_cost
        if cost_diff == 0:
            return [item[0] for item in region_items]
        weighted_items: list[str] = []
        max_weight: int = 4
        for item in region_items:
            item_weight: int = (
                round(((max_cost - item[1]) / cost_diff) * (max_weight - 1)) + 1
            )
            for _ in range(item_weight):
                weighted_items.append(item[0])
        return weighted_items

    def foods(self) -> list[str]:
        return self.get_item_strings(
            [
                *self.foods_mains,
                *self.foods_sides,
                *self.foods_desserts,
                *self.foods_beverages,
            ]
        )

    def interiors(self) -> list[str]:
        return self.get_item_strings(self.interiors_base)

    def clothes(self) -> list[str]:
        return self.get_item_strings(
            [
                *self.clothes_masculine,
                *self.clothes_feminine,
                *self.clothes_unisex,
                *self.clothes_formal_wear_masculine,
                *self.clothes_formal_wear_feminine,
                *self.clothes_formal_wear_unisex,
                *self.clothes_costumes_masculine,
                *self.clothes_costumes_feminine,
                *self.clothes_costumes_unisex,
            ]
        )

    def clothes_male(self) -> list[str]:
        return self.get_item_strings(
            [
                *self.clothes_masculine,
                *self.clothes_unisex,
                *self.clothes_formal_wear_masculine,
                *self.clothes_formal_wear_unisex,
                *self.clothes_costumes_masculine,
                *self.clothes_costumes_unisex,
            ]
        )

    def clothes_female(self) -> list[str]:
        return self.get_item_strings(
            [
                *self.clothes_feminine,
                *self.clothes_unisex,
                *self.clothes_formal_wear_feminine,
                *self.clothes_formal_wear_unisex,
                *self.clothes_costumes_feminine,
                *self.clothes_costumes_unisex,
            ]
        )

    def gifts(self) -> list[str]:
        return self.get_item_strings(self.gifts_base)

    def treasures(self) -> list[str]:
        return self.get_item_strings(self.treasures_base)

    def level_up_items(self) -> list[str]:
        return self.get_item_strings(self.level_up_items_base)

    @staticmethod
    def bonus_objectives_base() -> list[str]:
        """
        The list of base bonus objectives for Tomodachi Life.

        Returns:
            list[str]: The list of base bonus objectives.
        """
        return [
            "Accept donations at the Fountain",
            "Check the Rankings Board",
            "Create a new Mii from a QR code",
            "Create a new Mii from scratch",
            "Create a new group song at the Concert Hall",
            "Create a new solo song at the Concert Hall",
            "Edit a Mii",
            "Erase a Mii",
            "Listen to a Mii's random thought",
            "Look in a Mii's dream",
            "Look in a Mii's stomach and find food inside",
            "Observe a Mii at the Amusement Park",
            "Observe a Mii at the Beach",
            "Observe a Mii at the Café",
            "Observe a Mii at the Fountain",
            "Observe a Mii at the Observation Tower",
            "Observe a Mii farting",
            "Pet a Mii",
            "Play a game with a Mii",
            "Play Judgement Bay at the Beach",
            "Play Quirky Questions at the Observation Tower",
            "Save your progress",
            "Sell items at the Pawn Shop",
            "Solve a Mii's neighbour dispute",
            "Solve a Mii's random problem",
            "Stock up on clothes",
            "Stock up on food",
            "Stock up on hats",
            "Stock up on import wear",
            "Stock up on interiors",
            "Take a Couple Photo at the Photo Studio",
            "Take a Group Photo at the Photo Studio",
            "Take a Kid Photo at the Photo Studio",
            "Take a Whole Island Photo at the Photo Studio",
            "Use the Compatibility Forecast at the Compatibility Tester",
            "Use the Compatibility Test at the Compatibility Tester",
            "Visit the Mii Homes",
            "Visit the Port",
            "Watch old Mii News",
            "Watch the latest Mii News",
        ]

    @staticmethod
    def bonus_objectives_time_consuming() -> list[str]:
        """
        The list of time consuming bonus objectives for Tomodachi Life. These objectives are considered time consuming because it needs to be a specific time of the day for them to be possible.

        Returns:
            list[str]: The list of time consuming bonus objectives.
        """
        return [
            "Observe a Girls' Meeting at the Café",
            "Observe a Guys' Meeting at the Café",
            "Observe a Magic Show at the Amusement Park",
            "Observe a Rap Battle at the Fountain",
            "Observe a Word Chain battle at the Fountain",
            "Play Tomodachi Quest at the Amusement Park",
            "Purchase an item at the Amusement Park",
            "Purchase an item at the Fountain",
            "Purchase an item at the Park",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.tomodachi_life_weights.value
        factor: int = 100
        objectives: list[GameObjectiveTemplate] = [
            GameObjectiveTemplate(
                label=f"Feed FOOD{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''} to any Mii",
                data={"FOOD": (self.foods, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_food"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Give any Mii the INTERIOR interior{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                data={"INTERIOR": (self.interiors, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_interior"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Dress any Mii in CLOTHES{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                data={"CLOTHES": (self.clothes, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_clothes"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Gift GIFT{' if owned' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''} to any Mii",
                data={"GIFT": (self.gifts, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_gift"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Give any Mii the TREASURE treasure{' if owned' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                data={"TREASURE": (self.treasures, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_treasure"] * factor,
            ),
            GameObjectiveTemplate(
                label="Give ITEM to any Mii on level up",
                data={"ITEM": (self.level_up_items, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_level_up_item"] * factor,
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["bonus"] * factor / 5 * 4),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_time_consuming, 1)},
                is_time_consuming=True,
                is_difficult=False,
                weight=int(weights["bonus"] * factor / 5),
            ),
        ]
        if len(self.archipelago_options.tomodachi_life_male_miis.value) > 0:

            def get_male_data() -> tuple[Callable, int]:
                return (
                    lambda: self.archipelago_options.tomodachi_life_male_miis.value,
                    1,
                )

            def get_male_weight(weight_key: str) -> int:
                """
                Gets the weight of Tomodachi Life objectives that require a named male Mii using the given weight key. Ensures that male and female objectives are balanced based on the total number of Miis.

                Args:
                    weight_key (str): The weight key.

                Returns:
                    int: The weight of the objective type.
                """
                return int(
                    weights[weight_key]
                    * factor
                    * (
                        len(self.archipelago_options.tomodachi_life_male_miis.value)
                        / (
                            len(self.archipelago_options.tomodachi_life_male_miis.value)
                            + len(
                                self.archipelago_options.tomodachi_life_female_miis.value
                            )
                        )
                    )
                )

            objectives.extend(
                [
                    GameObjectiveTemplate(
                        label=f"Feed FOOD{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''} to MALE",
                        data={"FOOD": (self.foods, 1), "MALE": get_male_data()},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_male_weight("named_mii_food"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Give MALE the INTERIOR interior{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                        data={"MALE": get_male_data(), "INTERIOR": (self.interiors, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_male_weight("named_mii_interior"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Dress MALE in CLOTHES{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                        data={"MALE": get_male_data(), "CLOTHES": (self.clothes, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_male_weight("named_mii_clothes"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Gift GIFT{' if owned' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''} to MALE",
                        data={"GIFT": (self.gifts, 1), "MALE": get_male_data()},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_male_weight("named_mii_gift"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Give MALE the TREASURE treasure{' if owned' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                        data={"MALE": get_male_data(), "TREASURE": (self.treasures, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_male_weight("named_mii_treasure"),
                    ),
                ]
            )
        if len(self.archipelago_options.tomodachi_life_female_miis.value) > 0:

            def get_female_data() -> tuple[Callable, int]:
                return (
                    lambda: self.archipelago_options.tomodachi_life_female_miis.value,
                    1,
                )

            def get_female_weight(weight_key: str) -> int:
                """
                Gets the weight of Tomodachi Life objectives that require a named female Mii using the given weight key. Ensures that male and female objectives are balanced based on the total number of Miis.

                Args:
                    weight_key (str): The weight key.

                Returns:
                    int: The weight of the objective type.
                """
                return int(
                    weights[weight_key]
                    * factor
                    * (
                        len(self.archipelago_options.tomodachi_life_female_miis.value)
                        / (
                            len(self.archipelago_options.tomodachi_life_male_miis.value)
                            + len(
                                self.archipelago_options.tomodachi_life_female_miis.value
                            )
                        )
                    )
                )

            objectives.extend(
                [
                    GameObjectiveTemplate(
                        label=f"Feed FOOD{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''} to FEMALE",
                        data={"FOOD": (self.foods, 1), "FEMALE": get_female_data()},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_female_weight("named_mii_food"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Give FEMALE the INTERIOR interior{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                        data={
                            "FEMALE": get_female_data(),
                            "INTERIOR": (self.interiors, 1),
                        },
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_female_weight("named_mii_interior"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Dress FEMALE in CLOTHES{' if unlocked' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                        data={
                            "FEMALE": get_female_data(),
                            "CLOTHES": (self.clothes, 1),
                        },
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_female_weight("named_mii_clothes"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Gift GIFT{' if owned' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''} to FEMALE",
                        data={"GIFT": (self.gifts, 1), "FEMALE": get_female_data()},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_female_weight("named_mii_gift"),
                    ),
                    GameObjectiveTemplate(
                        label=f"Give FEMALE the TREASURE treasure{' if owned' if self.archipelago_options.tomodachi_life_skip_locked_items.value else ''}",
                        data={
                            "FEMALE": get_female_data(),
                            "TREASURE": (self.treasures, 1),
                        },
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=get_female_weight("named_mii_treasure"),
                    ),
                ]
            )
        return objectives
