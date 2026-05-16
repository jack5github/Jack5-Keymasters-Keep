"""
A Keymaster's Keep implementation of Tomodachi Life: Living the Dream, created by Jack5. The following objective types are included:

- Feed specific Miis specific food
- Dress specific Miis in specific clothing
- Give specific Miis specific treasures
- Give specific Miis specific level up gifts (time consuming)
- Give specific Miis specific interiors/exteriors
- Place objects/landscape tiles on the island
- Bonus objectives (time consuming)

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `tomodachi_life_living_the_dream_weights` YAML option.

Tomodachi Life: Living the Dream is different from the original Tomodachi Life in that items are not region-locked, but they are unlocked in an order that is dependent on the player's region. For this reason, it is recommended to accompany this implementation with a meta-implementation (e.g. Consumables). Cheap items still appear in objectives more frequently than expensive items.

WARNING: This implementation is incomplete, as it does not support all of the items in the game. For some item types, Jack5 has only added the items he has unlocked, as he is unable to find a complete items database online. Once a complete database is found with American and Australian item names, this implementation will be fully updated.
"""

from dataclasses import dataclass
from functools import cached_property
from Options import (  # pyright: ignore[reportMissingImports]
    Choice,
    DefaultOnToggle,
    OptionCounter,
    OptionDict,
    OptionList,
    Toggle,
)
from schema import Optional, Schema
from typing import Any
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class TomodachiLifeLTDWeights(OptionCounter):
    """
    The weights to use for Tomodachi Life: Living the Dream objective types. The default weights include objectives that require a player to give specific Miis specific items, which would be undesirable for players that want to keep their Miis accurate. If this is the case, set all "named_mii_named_..." weights to 0 except "named_mii_named_food".
    """

    display_name: str = "Tomodachi Life: Living the Dream Weights"
    default: dict[str, int] = {
        "any_mii_named_food": 6,
        "any_mii_named_clothing": 6,
        "any_mii_named_treasure": 4,
        "any_mii_named_level_up_gift": 4,
        "any_mii_named_interior": 4,
        "any_mii_named_exterior": 2,
        "named_mii_any_food": 3,
        "named_mii_any_clothing": 3,
        "named_mii_any_treasure": 2,
        "named_mii_any_level_up_gift": 2,
        "named_mii_any_interior": 2,
        "named_mii_any_exterior": 1,
        "named_mii_named_food": 3,
        "named_mii_named_clothing": 3,
        "named_mii_named_treasure": 2,
        "named_mii_named_level_up_gift": 2,
        "named_mii_named_interior": 2,
        "named_mii_named_exterior": 1,
        "place_objects": 8,
        "place_building": 1,
        "place_landscapes": 2,
        "bonus": 20,
    }


class TomodachiLifeLTDRegion(Choice):
    """
    The region of the copy of Tomodachi Life: Living the Dream being played. Affects only the names of items. Only `north_america` and `europe` are implemented at the moment. If multiple names are not implemented for a given item in this implementation, either region's name may be used.
    """

    display_name: str = "Tomodachi Life: Living the Dream Region"
    option_north_america: int = 0
    option_europe: int = 1
    default: int = 0


class TomodachiLifeLTDSkipLockedItems(DefaultOnToggle):
    """
    Whether Tomodachi Life: Living the Dream objectives involving items should include a notice that allows them to be skipped if their items are not unlocked or owned by the player, depending on the item type. Defaults to true.
    """

    display_name: str = "Tomodachi Life: Living the Dream Skip Locked Items"


class TomodachiLifeLTDTrashItems(Toggle):
    """
    Whether to allow trash food and treasures (e.g. 'moldy bread', 'Box of tissues' etc.) to appear as part of Tomodachi Life: Living the Dream objectives. Defaults to false.
    """

    display_name: str = "Tomodachi Life: Living the Dream Trash Items"


class TomodachiLifeLTDMiis(OptionList):
    """
    The list of names of Miis living in a given copy of Tomodachi Life: Living the Dream, to use for objectives that require a specific Mii. If empty, specific Mii objectives will not appear. Defaults to generic categories for each gender.
    """

    display_name: str = "Tomodachi Life: Living the Dream Miis"
    default: list[str] = ["a male Mii", "a female Mii", "a non-binary Mii"]


class TomodachiLifeLTDCreations(OptionDict):
    """
    The list of names of items created in the Studio Workshop (a.k.a. Palette House) to include as part of Tomodachi Life: Living the Dream objectives. Expects a dictionary where each value is a lists of strings. Supported keys are "food", "clothing", "treasures", "interiors", "exteriors", "objects" and "landscapes". Defaults to a dictionary with empty lists for each key.
    """

    display_name: str = "Tomodachi Life: Living the Dream Creations"
    schema: Schema = Schema(
        {
            Optional("food"): list[str],
            Optional("clothing"): list[str],
            Optional("treasures"): list[str],
            Optional("interiors"): list[str],
            Optional("exteriors"): list[str],
            Optional("objects"): list[str],
            Optional("landscapes"): list[str],
        }
    )
    default: dict[str, Any] = {
        "food": [],
        "clothing": [],
        "treasures": [],
        "interiors": [],
        "exteriors": [],
        "objects": [],
        "landscapes": [],
    }


@dataclass
class TomodachiLifeLTDArchipelagoOptions:
    tomodachi_life_living_the_dream_weights: TomodachiLifeLTDWeights
    tomodachi_life_living_the_dream_region: TomodachiLifeLTDRegion
    tomodachi_life_living_the_dream_skip_locked_items: TomodachiLifeLTDSkipLockedItems
    tomodachi_life_living_the_dream_trash_items: TomodachiLifeLTDTrashItems
    tomodachi_life_living_the_dream_miis: TomodachiLifeLTDMiis
    tomodachi_life_living_the_dream_creations: TomodachiLifeLTDCreations


@dataclass
class LTDName:
    """
    The names of an item from Tomodachi Life: Living the Dream.

    Args:
        na (str): The name of the item in the American version of the game.
        eu (str): The name of the item in the European version of the game.
    """

    na: str
    eu: str


@dataclass
class LTDItem:
    """
    An item from Tomodachi Life: Living the Dream.

    Args:
        name (str | LTDName): The name of the item.
        cost (float | int | None): The cost of the item, or None if it can only be obtained under special circumstances.
    """

    name: str | LTDName
    cost: float | int | None


class TomodachiLifeLTDGame(Game):
    """
    Tomodachi Life: Living the Dream is a social simulation game that centres on the everyday lives of Miis who live on a remote island. The player can create Miis via a number of means, and use more advanced customisation options including additional choices for hair, facial features, ears, gender, pronouns and dating preferences. A personality is assigned through the selection of various temperament attributes. By continuously adding Miis and completing miscellaneous objectives, additional buildings, shops and attractions become unlocked, all of which are placed on the island by the player. It is a sequel to the 3DS-exclusive Tomodachi Life, which itself was a sequel to the Japan-only DS-exclusive Tomodachi Collection.

    The game has no end condition, instead the player's objective is to sustain the happiness of their Miis. Occasionally Miis will signal the player that they have a particular problem. These issues include requesting food or clothing, getting advice on relationships, participating in short minigames and needing assistance from being paralysed, the latter of which either the player or another Mii can remedy. Fulfilling their needs boosts their happiness level, which gives "warm fuzzies", cash and the possibility for a Mii to level up and receive a gift. This game introduces the ability to completely customise the layout of the island and create custom items through the Studio Workshop (a.k.a. Palette House).
    """

    name: str = "Tomodachi Life: Living the Dream"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.SW
    is_adult_only_or_unrated: bool = False
    options_cls: type[TomodachiLifeLTDArchipelagoOptions] = (
        TomodachiLifeLTDArchipelagoOptions
    )

    @cached_property
    def food_food(self) -> list[LTDItem]:
        """
        The food items classified as 'Food' in Tomodachi Life: Living the Dream. Derived from https://docs.google.com/spreadsheets/d/1TyLMb9qR52tpPSeCWo3kovkHwIGDUlJQYmKz77NHAIE/htmlview#gid=415930329.

        Returns:
            list[LTDItem]: The list of 'Food' food items.
        """
        return [
            LTDItem('avocado', 1),
            LTDItem('bacalao', 7.6),
            LTDItem('bacon', 3.8),
            LTDItem('baguette', 1.5),
            LTDItem('baked beans', 2.5),
            LTDItem('baked potato', 5),
            LTDItem('banh mi', 5.6),
            LTDItem('barbecue', 15),
            LTDItem('beans on toast', 1.5),
            LTDItem('beef borguignon', 9.8),
            LTDItem('bibimbap', 8),
            LTDItem('bitter melon', 1.5),
            LTDItem('blue cheese', 4),
            LTDItem('boiled dumplings', 8.5),
            LTDItem('boiled octopus', 3),
            LTDItem('bonito-flakes rice bowl', 1.7),
            LTDItem('borscht', 7.8),
            LTDItem('broccoli', 1.9),
            LTDItem('brussels sprouts', 1),
            LTDItem('buchimgae', 5.5),
            LTDItem('budae-jigae', 6),
            LTDItem('buffalo wings', 8.6),
            LTDItem('bulgogi', 12),
            LTDItem('buttered potato', 3.8),
            LTDItem('calamari', 4.8),
            LTDItem('caprese salad', 8.7),
            LTDItem('carbonara', 8.8),
            LTDItem('caviar', 65),
            LTDItem('celery', 1.3),
            LTDItem('ceviche', 9.8),
            LTDItem('chankonabe', 15.8),
            LTDItem('charcoal-grilled beef', 13),
            LTDItem('chawanmushi', 5),
            LTDItem('cheese', 2),
            LTDItem('cheese board', None),
            LTDItem('cheeseburger', 3),
            LTDItem('chicken noodle soup', 6.8),
            LTDItem('chicken pho', 8),
            LTDItem('chicken pot pie', 7.8),
            LTDItem('chicken tikka masala', 12.9),
            LTDItem('chikuwa fish cake', 1),
            LTDItem('chili prawns', 6.4),
            LTDItem(LTDName('chili sin carne', 'chilli bowl'), 7.6),
            LTDItem('chinese mitten crabs', 32),
            LTDItem('chirashi-zushi', 8),
            LTDItem('clam chowder', 6),
            LTDItem('cold soba noodles', 6),
            LTDItem('cold somen noodles', 6.7),
            LTDItem('coleslaw', 3.2),
            LTDItem('corn dog', 2.5),
            LTDItem('corn on the cob', 3.5),
            LTDItem('cornflakes', 4),
            LTDItem('Cornish pasty', 4),
            LTDItem('couscous', 9.9),
            LTDItem('crab', 60),
            LTDItem('creamy corn soup', 3.8),
            LTDItem('creamy stew', 6.8),
            LTDItem('croissant', 1.2),
            LTDItem('croquettes', 6.8),
            LTDItem('curry bun', 1.2),
            LTDItem('curry with rice', 7),
            LTDItem('dan bing', 6.5),
            LTDItem('deviled eggs', 6),
            LTDItem('dim sum', 9.5),
            LTDItem('doenjang-jigae', 5),
            LTDItem('doner kebab', 5.9),
            LTDItem('dried squid', 2),
            LTDItem('drumstick', 10),
            LTDItem('dubu-kimchi', 12),
            LTDItem('edamame', 3),
            LTDItem('eggplant parmigiana', 10),
            LTDItem('ehomaki', 7),
            LTDItem('empanadas', 12),
            LTDItem('enchiladas', 14),
            LTDItem(LTDName('English breakfast', 'full English'), 8),
            LTDItem('escargot', 12),
            LTDItem('falafel', 7.8),
            LTDItem('filet mignon', 50),
            LTDItem('fish cakes', 7.8),
            LTDItem('french fries', 2.8),
            LTDItem('French onion soup', 4.1),
            LTDItem('French toast', 3.8),
            LTDItem('fresh spring rolls', 5.9),
            LTDItem('fried chicken', 4.5),
            LTDItem('fried egg', 3.8),
            LTDItem('fried rice', 4.8),
            LTDItem('fried sardines', 4),
            LTDItem('fried shrimp', 3.7),
            LTDItem('fried spring rolls', 6.3),
            LTDItem('fried tofu', 2.5),
            LTDItem('fruity granola', 2.5),
            LTDItem('fugu sashimi', 29),
            LTDItem('fukumame', 4),
            LTDItem('gamja-tang', 22),
            LTDItem('ganjang-gejang', 19),
            LTDItem('garlic', 1.1),
            LTDItem('gazpacho', 4.9),
            LTDItem('gim', 2),
            LTDItem('ginseng', 50),
            LTDItem('gnocchi', 5.6),
            LTDItem('gochujang', 1.5),
            LTDItem('grated carrot', 1.5),
            LTDItem('gratin', 9.8),
            LTDItem('Greek salad', 6.8),
            LTDItem('green curry', 9.5),
            LTDItem('green pepper', 1.1),
            LTDItem('grilled cheese', 2),
            LTDItem('grilled cutlassfish', 4),
            LTDItem('grilled pacific saury', 4.8),
            LTDItem('grilled sweetfish', 4.5),
            LTDItem('grilled turban shell', 6.5),
            LTDItem('grilled-eel rice bowl', 28),
            LTDItem('grits', 5),
            LTDItem('gyeran-jjim', 3),
            LTDItem('gyudon', 6),
            LTDItem('habanero', 1),
            LTDItem('haggis', 6.5),
            LTDItem('hake fillet', 7),
            LTDItem('ham and asparagus', 6),
            LTDItem('hard-boiled egg', 1),
            LTDItem('hash browns', 1.5),
            LTDItem('hayashi rice', 7.8),
            LTDItem('herring', 4.5),
            LTDItem('hiyashi-chuka noodles', 6),
            LTDItem('hobak-buchimgae', 4.5),
            LTDItem('hot and sour soup', 14),
            LTDItem('hot dog', 2.8),
            LTDItem('hot pot', 16),
            LTDItem('hummus', 5.3),
            LTDItem('Iberian ham', 12),
            LTDItem('inari sushi', 1.5),
            LTDItem('instant noodles', 1.9),
            LTDItem('jajangmyeon', 4.5),
            LTDItem('janchi-guksu', 3.5),
            LTDItem('japchae', 5),
            LTDItem('jeonbok-juk', 8),
            LTDItem('kasujiru', 2.5),
            LTDItem('katsudon', 6.8),
            LTDItem('khao man gai', 11),
            LTDItem("kid's meal", 7),
            LTDItem('kimchi', 2.8),
            LTDItem(LTDName('kimchi-bokkeum-bap', 'kimchi fried rice'), 6),
            LTDItem('kimchi-jjigae', 5),
            LTDItem('kimchijeon', 8),
            LTDItem('kitsune udon', 6.5),
            LTDItem('kkakdugi', 2.5),
            LTDItem('konnyaku', 1),
            LTDItem('Korean chili pepper', 0.5),
            LTDItem('Korean sausage', 3),
            LTDItem(LTDName('lasagna', 'lasagne'), 6.5),
            LTDItem('liver', 4.8),
            LTDItem('lobster', 9.8),
            LTDItem('lobster roll', 18),
            LTDItem('loco moco', 8.1),
            LTDItem('macaroni and cheese', 5.8),
            LTDItem('mapo tofu', 6.7),
            LTDItem('mashed potatoes', 3.5),
            LTDItem('matsutake mushroom', 78),
            LTDItem('meat-and-potato stew', 6),
            LTDItem('meatballs', 5),
            LTDItem(LTDName('minestrone soup', 'minestrone'), 7),
            LTDItem('miso soup', 2.8),
            LTDItem('miyeok-guk', 3),
            LTDItem('mochi', 1.5),
            LTDItem('moldy bread', 0.2),
            LTDItem('monjayaki', 6.2),
            LTDItem('mooncakes', 9.5),
            LTDItem('mozzarella', 3),
            LTDItem('mul naengmyeon', 6.7),
            LTDItem(LTDName('mushroom', 'porcini mushroom'), 1.3),
            LTDItem('mussels', 7.9),
            LTDItem('myoga ginger', 1),
            LTDItem('nachos', 7.5),
            LTDItem('namul', 3),
            LTDItem('napa cabbage', 2),
            LTDItem('natto', 1),
            LTDItem('ochazuke', 4.8),
            LTDItem('oden', 3),
            LTDItem('oi kimchi', 4),
            LTDItem('okonomiyaki', 7.8),
            LTDItem('olives', 3),
            LTDItem('Olivier salad', 6),
            LTDItem('omelet', 6.5),
            LTDItem('omurice', 6.8),
            LTDItem('onion rings', 5.4),
            LTDItem('osechi', 100),
            LTDItem('oyakodon', 6),
            LTDItem('oyster', 6.8),
            LTDItem('ozoni', 3.3),
            LTDItem('pad krapow', 9.5),
            LTDItem('paella', 8.8),
            LTDItem('panini', 4.5),
            LTDItem('pão de queijo', 2.5),
            LTDItem('patatas bravas', 4.5),
            LTDItem('PB&J', 1.5),
            LTDItem('Peking duck', 50),
            LTDItem('pesto pasta', 7.3),
            LTDItem('pickled plum', 1),
            LTDItem(LTDName('pickles', 'gherkins'), 2),
            LTDItem('pizza', 3.9),
            LTDItem('poke', 15),
            LTDItem('polenta', 5.8),
            LTDItem('popcorn shrimp', 4),
            LTDItem('pork bun', 1.2),
            LTDItem('pork cutlet', 8),
            LTDItem('pork pie', 4.5),
            LTDItem('porridge', 3),
            LTDItem('pot stickers', 2.8),
            LTDItem('pot-au-feu', 7),
            LTDItem('prawn salad', 7.5),
            LTDItem('prosicutto', 6.9),
            LTDItem('quiche', 5.5),
            LTDItem('raclette', 11),
            LTDItem('ramen', 6.8),
            LTDItem('ramyeon', 4),
            LTDItem('ratatouille', 6.9),
            LTDItem('ravioli', 6.4),
            LTDItem('red chili pepper', 0.5),
            LTDItem('rice', 2),
            LTDItem('rice ball', 1.1),
            LTDItem('rice porridge', 1.5),
            LTDItem('risotto', 7.8),
            LTDItem('roast beef', 15),
            LTDItem('roast chicken', 20),
            LTDItem('roast duck', 16),
            LTDItem('roast goose', 15),
            LTDItem('roast lamb', 12),
            LTDItem('roast turkey', 33),
            LTDItem(LTDName('roasted leg of lamb', 'roasted lamb leg'), 17),
            LTDItem('rollmop herrings', 5.4),
            LTDItem('ruined meal', 0.2),
            LTDItem('salad', 5.6),
            LTDItem('salami', 3.9),
            LTDItem('Salisbury steak', 7),
            LTDItem('salmon meunière', 7.5),
            LTDItem('salmon roe', 9.8),
            LTDItem('saltimbocca', 11.9),
            LTDItem('samgye-tang', 9),
            LTDItem('samgyeopsal', 8),
            LTDItem('sandwich', 3.3),
            LTDItem('sardines', 1.4),
            LTDItem('sashimi', 12.8),
            LTDItem('sauerkraut', 4.5),
            LTDItem('sausage', 2),
            LTDItem('sautéed zucchini', 4.8),
            LTDItem('schnitzel', 13),
            LTDItem('scrambled eggs', 1.5),
            LTDItem('sea urchin', 10),
            LTDItem('seafood platter', 8.2),
            LTDItem('sekihan', 3),
            LTDItem('seolleongtang', 6),
            LTDItem('shrimp pilaf', 7),
            LTDItem('shumai', 1.2),
            LTDItem(LTDName('sliced sea bream', 'sea bream sashimi'), 38),
            LTDItem('smoked salmon', 9),
            LTDItem('sotteok sotteok', 7.8),
            LTDItem('space food', 20),
            LTDItem('spaghetti', 7.8),
            LTDItem(LTDName('spaghetti aglio e olio', 'spaghetti peperoncino'), 7.8),
            LTDItem('spicy pollack roe', 7.8),
            LTDItem('spinach', 2),
            LTDItem('split-pea soup', 4.7),
            LTDItem('squid-ink spaghetti', 7.8),
            LTDItem('steak', 19.8),
            LTDItem('stewed beef', 808),
            LTDItem('stir-fried tomato and eggs', 8.9),
            LTDItem('store-bought lunch', 5),
            LTDItem('string cheese', 4),
            LTDItem('stuffed cabbage roll', 7),
            LTDItem('stuffed peppers', 13),
            LTDItem('stuffing', 6.7),
            LTDItem('sukiyaki', 17.8),
            LTDItem('sundubu-jjigae', 6),
            LTDItem('sushi', 15.8),
            LTDItem('suyuk', 15),
            LTDItem('sweet-and-sour pork', 7.8),
            LTDItem('tacos', 4.8),
            LTDItem('takoyaki', 3),
            LTDItem('tamale', 5),
            LTDItem('tempura', 8.8),
            LTDItem('tempura rice bowl', 8.5),
            LTDItem('tofu', 1.5),
            LTDItem('tomato', 1.4),
            LTDItem('tonkatsu', 8),
            LTDItem('truffle mushroom', 60),
            LTDItem('tteokbokki', 3),
            LTDItem('tteokguk', 6),
            LTDItem('veggie burger', 4.8),
            LTDItem('white bread', 1),
            LTDItem('xiaolongbao', 7.8),
            LTDItem('yakisoba', 4),
            LTDItem('yakitori', 3.5),
            LTDItem('yangnyeom chikin', 10),
            LTDItem('yeonggye-baeksuk', 14),
            LTDItem('youtiao', 6),
            LTDItem('yukhoe', 11),
            LTDItem('zampone sausage', 9.7),
            LTDItem('zongzi', 7),
            LTDItem('zucchini', 3),
        ]

    @cached_property
    def food_desserts(self) -> list[LTDItem]:
        """
        The food items classified as 'Dessert' in Tomodachi Life: Living the Dream. Derived from https://docs.google.com/spreadsheets/d/1TyLMb9qR52tpPSeCWo3kovkHwIGDUlJQYmKz77NHAIE/htmlview#gid=415930329.

        Returns:
            list[LTDItem]: The list of 'Dessert' food items.
        """
        return [
            LTDItem('anpan', 1.5),
            LTDItem('apple', 1.5),
            LTDItem('apple crumble', 6.8),
            LTDItem('apple pie', 4.8),
            LTDItem('baked sweet potato', 3.8),
            LTDItem('banana', 1),
            LTDItem('banana peel', 0.2),
            LTDItem('banana split', 6.5),
            LTDItem('beef jerky', 3),
            LTDItem('birthday cake', None),
            LTDItem('biscuit', 1.5),
            LTDItem(LTDName('Black Forest cake', 'Black Forest gateau'), 4.5),
            LTDItem('brownie', 4.2),
            LTDItem('bubble waffle', 9.8),
            LTDItem(LTDName('bugnes', 'angel wings'), 8),
            LTDItem('bundkuchen', 6.2),
            LTDItem('butter cookie', 1.8),
            LTDItem('candy apple', 2.5),
            LTDItem('candy corn', 0.75),
            LTDItem('canelé', 4),
            LTDItem('cannoli', 2),
            LTDItem(LTDName('caramelized nuts', 'caramelised nuts'), 5.7),
            LTDItem('carrot cake', 5.3),
            LTDItem('castella cake', 5),
            LTDItem('cheesecake', 4.9),
            LTDItem('cherimoya', 3),
            LTDItem('cherries', 2.9),
            LTDItem('cherry pie', 5.2),
            LTDItem('chewing gum', 1.2),
            LTDItem('chocolate', 1.5),
            LTDItem('chocolate egg', 3.5),
            LTDItem('chocolate gâteau', 6),
            LTDItem('chocolate sundae', 7.8),
            LTDItem('chocolate toast', 1.5),
            LTDItem('churros', 3),
            LTDItem('cinnamon roll', 1.3),
            LTDItem('clotted cream', 1.2),
            LTDItem('coconut', 5.5),
            LTDItem('colomba pasquale', 7.8),
            LTDItem('cotton candy', 3),
            LTDItem('cracker', 1.5),
            LTDItem('cream puff', 2.5),
            LTDItem('crème brûlée', 4.6),
            LTDItem('crepe', 4),
            LTDItem('dalgona', 4),
            LTDItem('dates', 2.5),
            LTDItem('dorayaki', 4.5),
            LTDItem('doughnut', 1.3),
            LTDItem('durian', 5),
            LTDItem('elephant ear', 2),
            LTDItem('fancy cupcake', 5),
            LTDItem('flan', 1.5),
            LTDItem('fried plantains', 4),
            LTDItem('frozen treat', 1),
            LTDItem('frozen yoghurt', 1.8),
            LTDItem('fudge', 4),
            LTDItem('gelatin snack', 1.5),
            LTDItem('gingerbread', 4.5),
            LTDItem('gingersnap', 2.3),
            LTDItem('granola parfait', 6),
            LTDItem('grapefruit', 3),
            LTDItem('grapes', 4.9),
            LTDItem('gummy candy', 1),
            LTDItem(LTDName('handmade chocolates', 'handmade chocolate'), 30),
            LTDItem(LTDName('hard candy', 'boiled sweet'), 0.5),
            LTDItem('honey', 4.5),
            LTDItem('ice-cream cone', 2.5),
            LTDItem('ice-cream sandwich', 3.1),
            LTDItem('key lime pie', 4.6),
            LTDItem('king cake', 5.2),
            LTDItem('kiwi', 1.5),
            LTDItem(LTDName('licorice', 'liquorice'), 0.7),
            LTDItem('lollipop', 3),
            LTDItem('macadamia nuts', 5),
            LTDItem('macaron', 3),
            LTDItem('mango', 9),
            LTDItem('maple taffy', 3.4),
            LTDItem('marzipan fruit', 7),
            LTDItem('melon', 10),
            LTDItem('mince pie', 2),
            LTDItem('mint candy', 0.2),
            LTDItem('mithai', None),
            LTDItem('muffin', 3.3),
            LTDItem('napoleon cake', 6.2),
            LTDItem('natillas', 2.5),
            LTDItem('oatmeal cookie', 2.2),
            LTDItem('orange', 1),
            LTDItem('oriental melon', 1),
            LTDItem('pain au chocolat', 1.2),
            LTDItem(LTDName('pain aux raisins', 'raisin bread'), 1.5),
            LTDItem('pancakes', 4),
            LTDItem('pandoro', 5.5),
            LTDItem('panettone', 2),
            LTDItem('panna cotta', 2.8),
            LTDItem('pastel de nata', 2.8),
            LTDItem('peach', 4.8),
            LTDItem('peanuts', 3.7),
            LTDItem('pear', 4.6),
            LTDItem('persimmon', 2),
            LTDItem('pineapple', 9.8),
            LTDItem('pineapple cakes', 7.6),
            LTDItem('pistachios', 3.5),
            LTDItem('plum pudding', 4.8),
            LTDItem('popcorn', 2.5),
            LTDItem('potato chips', 1.3),
            LTDItem('pretzel', 1.3),
            LTDItem('profiteroles', 6.9),
            LTDItem('pumpkin pie', 4.6),
            LTDItem('red velvet cake', 4.5),
            LTDItem('rice cracker', 1),
            LTDItem('rice pudding', 4.5),
            LTDItem('roasted chestnuts', 5.8),
            LTDItem("s'more", 3),
            LTDItem('saltine crackers', 1),
            LTDItem('shaved ice', 1.5),
            LTDItem(LTDName('soft-serve ice cream', 'soft ice cream'), 2.5),
            LTDItem('songpyeon', 6),
            LTDItem('soufflé', 5),
            LTDItem('stollen', 8),
            LTDItem('strawberry', 4.8),
            LTDItem('strawberry shortcake', 4),
            LTDItem('sunflower seeds', 3),
            LTDItem('sweet potato', 3.8),
            LTDItem('taiyaki', 2),
            LTDItem('tangyuan', 7.6),
            LTDItem('tiramisu', 5),
            LTDItem('tompouce', 5),
            LTDItem('torrijas', 7),
            LTDItem('tricolor dango', 3),
            LTDItem('turrones', 5.2),
            LTDItem('waffle', 2),
            LTDItem('walnuts', 3),
            LTDItem(LTDName('watermelon', 'watermelon slice'), 2),
            LTDItem('yogurt', 1.9),
            LTDItem('yokan', 5.8),
            LTDItem('Yule log', 9),
            LTDItem('zenzai', 5),
        ]

    @cached_property
    def food_drinks(self) -> list[LTDItem]:
        """
        The food items classified as 'Drinks' in Tomodachi Life: Living the Dream. Derived from https://docs.google.com/spreadsheets/d/1TyLMb9qR52tpPSeCWo3kovkHwIGDUlJQYmKz77NHAIE/htmlview#gid=415930329.

        Returns:
            list[LTDItem]: The list of 'Drinks' food items.
        """
        return [
            LTDItem('apple juice', 2),
            LTDItem('bubble tea', 5.5),
            LTDItem('cappuccino', 5.8),
            LTDItem('chamomile tea', 2.7),
            LTDItem('coffee', 5),
            LTDItem('daechu-cha', 4.5),
            LTDItem('energy drink', 3),
            LTDItem('espresso', 5.5),
            LTDItem('green juice', 2),
            LTDItem('green tea', 1),
            LTDItem('hot chocolate', 4),
            LTDItem('iced latte', 4),
            LTDItem('lemonade', 2.5),
            LTDItem('matcha', None),
            LTDItem('milk', 1.8),
            LTDItem('milkshake', 2),
            LTDItem('omija-cha', 4.5),
            LTDItem('orange juice', 2),
            LTDItem('protein shake', 10),
            LTDItem('root-beer float', 2.5),
            LTDItem('smoothie', 2.5),
            LTDItem('soda', 1.8),
            LTDItem('sparkling water', 1.2),
            LTDItem('spoiled milk', 0.2),
            LTDItem('sports drink', 2),
            LTDItem('tap water', 0.9),
            LTDItem('tea', 5.5),
            LTDItem('tomato juice', 1.5),
            LTDItem('yerba mate', 5.4),
        ]

    @cached_property
    def clothing_outfits(self) -> list[LTDItem]:
        """
        The clothing items classified as 'Outfits' in Tomodachi Life: Living the Dream. Derived from https://animalcrossingworld.com/tomodachi-life/catalog/clothing/outfits.

        Returns:
            list[LTDItem]: The list of 'Outfits' clothing items.
        """
        return [
            LTDItem(LTDName('ABC-loungewear outfit', 'ABC loungewear set'), 25.7),
            LTDItem('Aerobics outfit', 38.9),
            LTDItem('All-black outfit', 69.7),
            LTDItem('All-out summer-vacay outfit', 39),
            LTDItem('Angel costume', 67.9),
            LTDItem('Anorak-jacket outfit', 48.6),
            LTDItem('Argyle-vest outfit', 32.8),
            LTDItem('Aristocratic-coat costume', 1643.1),
            LTDItem(LTDName('Astronaut costume', 'Space suit'), 5000),
            LTDItem('B-3 outfit', 60.8),
            LTDItem('Baby-bird costume', 48),
            LTDItem('Baby-snapsuit outfit', 46),
            LTDItem('Baji jeogori outfit', 60.3),
            LTDItem('Baseball uniform', 60),
            LTDItem('Basic-dress-shirt outfit', 33.4),
            LTDItem('Basic-pullover outfit', 31.8),
            LTDItem('Basic-sweatshirt outfit', 31.2),
            LTDItem('Basic-tee outfit', 30.9),
            LTDItem('Basic-turtleneck outfit', 31.7),
            LTDItem('Basketball uniform', 35.7),
            LTDItem('Bear costume', 51),
            LTDItem('Bear-ear-cap outfit', 49.8),
            LTDItem('Bee costume', 45),
            LTDItem('Biker outfit', 65.5),
            LTDItem('Bird costume', 51),
            LTDItem('Blazer-with-necktie outfit', 37.4),
            LTDItem('Bodysuit outfit', 35),
            LTDItem('Bomber-jacket outfit', 32.3),
            # TODO: LTDItem('Bow tie and suspender outfit', 31.1), is not an American item
            LTDItem('Breezy business outfit', 31.2),
            LTDItem('Business suit & tie outfit', 42.5),
            LTDItem('Cardboard-box costume', 10),
            LTDItem(LTDName('Cardboard-robot costume', 'Cardboard robot outfit'), 12),
            LTDItem('Cargo-shorts outfit', 31.5),
            LTDItem(LTDName('Casual cardigan outfit', 'Casual cardigan combo'), 37.4),
            LTDItem('Casual-kimono outfit', 59.5),
            LTDItem('Casual vest outfit', 53),
            LTDItem('Catcher uniform', 75),
            LTDItem('Cat costume', 44),
            LTDItem('Chef outfit', 53.9),
            LTDItem(LTDName('Cheongsam outfit', 'Changshan set'), 42.5),
            LTDItem('Chicken costume', 63),
            LTDItem('City-walk outfit', 49.1),
            LTDItem('Coach-jacket outfit', 37.1),
            LTDItem(LTDName('Collarless-coat outfit', 'Collarless coat combo'), 44.2),
            LTDItem('Color-blocked-tee outfit', 33.4),
            LTDItem('Comfy sweats outfit', 28),
            # TODO: LTDItem('Colourful shirt combo', 40.4), is not an American item
            # TODO: LTDItem('Combat shorts combo', 31.5), is not an American item
            LTDItem(LTDName('Compression outfit', 'Compression set'), 44.2),
            LTDItem('Cool leather outfit', 57.7),
            LTDItem('Corduroy outfit', 40.1),
            # TODO: LTDItem('Construction worker outfit', 48.2), is not an American item
            LTDItem(LTDName('Cosmic outfit', 'Cosmic combo'), 56.7),
            LTDItem('Country outfit', 53.3),
            LTDItem('Cow costume', 45),
            LTDItem('Cowichan-sweater outfit', 33.3),
            LTDItem('Crazy-color-shirt outfit', 40.4),
            LTDItem(LTDName('Cyberpunk costume', 'Cyberpunk set'), 46.6),
            LTDItem('Cycling uniform', 65.7),
            LTDItem('Denim-jacket outfit', 31.8),
            LTDItem('Detective outfit', 57.8),
            LTDItem('Devil costume', 58.6),
            LTDItem('Dinosaur costume', 60),
            LTDItem('Disco-star outfit', 81.4),
            LTDItem(LTDName('Diving costume', 'Atmospheric diving suit'), 87),
            LTDItem('DJ outfit', 62.4),
            LTDItem('Dog costume', 50),
            LTDItem('Dog-logo-tracksuit outfit', 50.5),
            LTDItem(LTDName('Dotted-shirt outfit', 'Dotted shirt combo'), 33.6),
            LTDItem('Dotted-shirt outfit', 33.6),
            LTDItem('Down-jacket outfit', 34),
            LTDItem('Dragon costume', 95),
            LTDItem(LTDName('Exercise outfit', 'Gym outfit'), 48.5),
            LTDItem('Explorer outfit', 77.6),
            LTDItem('Far-future costume', 60),
            LTDItem('Figure-skating costume', 50),
            LTDItem('Firefighter outfit', 83.5),
            LTDItem('Fish-folk costume', 55),
            LTDItem(LTDName('Flannel-shirt outfit', 'Lumberjack combo'), 33.5),
            LTDItem('Fleece-pullover outfit', 48.3),
            LTDItem('Flower costume', 45),
            LTDItem('Fly-fisher outfit', 58.9),
            LTDItem(LTDName('Football uniform', 'American football set'), 69),
            LTDItem('Formal suspenders outfit', 46.5),
            LTDItem('Formal vest outfit', 38.5),
            LTDItem('Frog costume', 52.6),
            LTDItem('Fruit-print-tee outfit', 26.5),
            LTDItem('Garden-gnome costume', 56),
            LTDItem('Gaudy-suit outfit', 40.2),
            LTDItem('Geometric-print-tee outfit', 51.8),
            LTDItem(LTDName('Gingham outfit', 'Gingham combo'), 33.7),
            LTDItem('Gladiator costume', 234.9),
            LTDItem('Goodnight pajama outfit', 32),
            LTDItem('Gothic prince outfit', 48.7),
            LTDItem(LTDName('Graduation outfit', 'Academic set'), 52.6),
            LTDItem('Grunge outfit', 50.9),
            LTDItem('Hamster costume', 51),
            LTDItem(LTDName('Heart-to-heart outfit', 'Heart-heavy combo'), 42.4),
            LTDItem(
                LTDName('Hemp-leaf-yukata outfit', "Hemp leaf men's yukata set"), 45.8
            ),
            LTDItem('Hero costume', 69.8),
            LTDItem('Hibiscus-print-shirt outfit', 25.4),
            LTDItem('Hiking outfit', 33.8),
            LTDItem('Hip-hop outfit', 83.2),
            LTDItem('Holiday-party outfit', 62.2),
            LTDItem('Holiday-tree costume', 61),
            LTDItem('Horse costume', 63),
            LTDItem('Hot-dog costume', 55),
            LTDItem('Ice-cream-tee outfit', 31.8),
            LTDItem('Ice-hockey uniform', 71),
            LTDItem("Jack-o'-lantern costume", 57),
            LTDItem('Japanese-print outfit', 46.8),
            LTDItem('Jester costume', 51),
            LTDItem('Jockey uniform', 57.2),
            LTDItem('Jogging outfit', 40.1),
            LTDItem('Knight costume', 1070),
            LTDItem('Koala costume', 63),
            LTDItem(LTDName('Kung-fu uniform', 'Kung fu outfit'), 35),
            LTDItem('Kurta outfit', 42.4),
            LTDItem('Lab-coat outfit', 31.4),
            LTDItem(
                LTDName('Lettered-tee outfit', 'Inspirational T-shirt combo'), 32.2
            ),
            # TODO: LTDItem('Letterman cardigan combo', 34.1), is not an American item
            LTDItem('Lion costume', 63),
            LTDItem(
                LTDName(
                    'Long-sleeve deck-striped outfit', 'Long-sleeved striped combo'
                ),
                53,
            ),
            LTDItem('Long-sleeve striped-tee outfit', 41.9),
            LTDItem('Luchador uniform', 64.1),
            LTDItem('Marathon outfit', 34.7),
            LTDItem('Mid-shower-doorbell outfit', 32.2),
            LTDItem('Mid-shower-phone-call outfit', 22),
            # TODO: LTDItem('Mii logo T-shirt combo', 33.7), is not an American item
            LTDItem('Monkey costume', 46),
            LTDItem('Monster costume', 56),
            # TODO: LTDItem('Motorcycling combo', 65.5), is not an American item
            LTDItem('Mummy costume', 50),
            LTDItem('Mushroom costume', 46),
            LTDItem('Nautical outfit', 56.7),
            # TODO: LTDItem('Necktie and blazer outfit', 37.4), is not an American item
            # TODO: LTDItem('Necktie and suit set', 42.5), is not an American item
            # TODO: LTDItem('Nerd outfit', 66.6), is not an American item
            LTDItem('Ninja costume', 160.6),
            LTDItem('Noir-detective outfit', 84.2),
            LTDItem('Oni costume', 51),
            LTDItem('Open-school-uniform outfit', 35.9),
            LTDItem('Open-sized-tee outfit', 51.5),
            LTDItem(LTDName('Painter outfit', 'Art explosion combo'), 40),
            LTDItem(LTDName('Paisley-jacket outfit', 'Paisley jacket combo'), 34.6),
            LTDItem('Pastel-suit outfit', 31.9),
            LTDItem('Patterned-shirt outfit', 29.5),
            LTDItem(LTDName('Peacoat outfit', 'Pea jacket outfit'), 56.7),
            LTDItem('Penguin costume', 63),
            LTDItem(LTDName('Phantom-thief costume', 'Phantom thief outfit'), 100),
            LTDItem('Pharaoh costume', 253.9),
            LTDItem(
                LTDName('Photo-print-tee outfit', 'Photo print T-shirt combo'), 26.5
            ),
            LTDItem('Pig costume', 63),
            LTDItem(LTDName('Pilot outfit', 'Pilot uniform'), 42.4),
            LTDItem('Pineapple costume', 46.1),
            LTDItem('Pirate costume', 78),
            LTDItem('Plaid-coat outfit', 38),
            LTDItem('Plaid-flannel outfit', 33.2),
            LTDItem('Plaid-jacket outfit', 73.7),
            # TODO: LTDItem('Plain collarless shirt combo', 34.8), is not an American item
            # TODO: LTDItem('Plain dress combo', 33.9), is not an American item
            # TODO: LTDItem('Plain dress set', 110.1), is not an American item
            # TODO: LTDItem('Plain dress shirt combo', 33.4), is not an American item
            # TODO: LTDItem('Plain jumper combo', 31.2), is not an American item
            # TODO: LTDItem('Plain skirt suit', 43.1), is not an American item
            # TODO: LTDItem('Plain T-shirt combo', 30.9), is not an American item
            LTDItem('Police uniform', 61.5),
            LTDItem('Prince costume', 866),
            # TODO: LTDItem('Polo-neck jumper combo', 37.8), is not an American item
            LTDItem(LTDName('Punky cargo-pants outfit', 'Punky skirt combo'), 44.5),
            LTDItem('Quilted-jacket outfit', 34.6),
            LTDItem(LTDName('Rabbit costume', 'Bunny costume'), 56),
            LTDItem('Racing uniform', 77.2),
            LTDItem('Ragged outfit', 8),
            LTDItem('Raglan-sweatshirt outfit', 31.5),
            LTDItem('Rainy-day outfit', 47.7),
            LTDItem('Reindeer costume', 53),
            LTDItem('Retro-swimsuit outfit', 46),
            LTDItem('RN outfit', 53),
            LTDItem('Rodeo-rider costume', 72.4),
            LTDItem('Royal costume', 3513.1),
            LTDItem('Rugby uniform', 48.8),
            LTDItem('Sage costume', 86.2),
            LTDItem('Samba costume', 101.9),
            LTDItem('Samurai outfit', 794.5),
            LTDItem('Santa outfit', 70.6),
            LTDItem('School outfit', 80.5),
            LTDItem('School-smock outfit', 44.5),
            LTDItem('School uniform', 35.5),
            # TODO: LTDItem('Shampoo bathrobe combo', 32.2), is not an American item
            LTDItem('Sheep costume', 50),
            LTDItem('Shirt-with-necktie outfit', 34.4),
            # TODO: LTDItem('Short-sleeved cardie combo', 32.9), is not an American item
            LTDItem('Simple-parka outfit', 58.7),
            LTDItem('Skeleton costume', 42),
            LTDItem('Skiing outfit', 52.3),
            LTDItem('Skull-tee outfit', 64.1),
            LTDItem('Sleek cyberpunk outfit', 46.6),
            LTDItem('Sleeveless-knit-top outfit', 61.8),
            # TODO: LTDItem('Sleeveless shirt outfit', 32.4), is not an American item
            LTDItem('Sleeveless-turtleneck outfit', 32),
            LTDItem('Snorkeling outfit', 95),
            LTDItem('Snowman costume', 50),
            LTDItem('Soccer uniform', 33.2),
            LTDItem(LTDName('Soft-drink costume', 'Fizzy drink costume'), 31),
            LTDItem('Soft-serve costume', 52.9),
            # TODO: LTDItem('Sporty tracksuit set', 32), is not an American item
            LTDItem('Sprout costume', 32),
            LTDItem('Stag-beetle costume', 60),
            LTDItem(LTDName('Star-print-tee outfit', 'Star T-shirt combo'), 32),
            LTDItem('Steampunk-coat outfit', 75.2),
            LTDItem('Store-attendant outfit', 42.6),
            LTDItem('Street-style layered outfit', 48),
            LTDItem('Street-style outfit', 82),
            # TODO: LTDItem('Striped long-sleeved set', 41.9), is not an American item
            LTDItem('Striped outfit', 33.3),
            LTDItem('Striped-polo outfit', 30.1),
            LTDItem('Striped rugby outfit', 35),
            # TODO: LTDItem('Subdued kimono set', 59.5), is not an American item
            LTDItem('Summer vintage-suit outfit', 60),
            LTDItem(LTDName('Sunny-side-up outfit', 'Sunny-side-up T-shirt combo'), 32),
            LTDItem('Superfan outfit', 66.6),
            LTDItem('Surveyor outfit', 63.2),
            LTDItem(LTDName('Suspenders outfit', 'Suspender combo'), 62),
            LTDItem('Swim outfit', 17.8),
            LTDItem('Tailcoat outfit', 210.4),
            LTDItem(LTDName('Tailored-jacket outfit', 'Casual jacket combo'), 33.8),
            LTDItem('Tam outfit', 60.3),
            LTDItem('Tennis-sweater outfit', 35.2),
            LTDItem('Tidy button-down outfit', 34.8),
            LTDItem('Tie-dye-tee outfit', 27.4),
            LTDItem('Tiger-baseball-jacket outfit', 33.8),
            LTDItem('Tiger costume', 68),
            LTDItem('Toy-robot costume', 64.5),
            LTDItem('Tracksuit outfit', 32),
            LTDItem('Tracksuit with shorts outfit', 31),
            LTDItem('Traffic-guard outfit', 48.2),
            LTDItem(
                LTDName('Traffic-print-tee outfit', 'Busy traffic T-shirt combo'), 32.4
            ),
            LTDItem('Tree costume', 54),
            LTDItem('Trench-coat outfit', 36),
            # TODO: LTDItem('Triangles T-shirt combo', 33.4), is not an American item
            # TODO: LTDItem('Two piece skirt suit', 117.6), is not an American item
            LTDItem('Turkey costume', 63),
            LTDItem('Tyrolean-lederhosen outfit', 70.4),
            LTDItem('University outfit', 35.6),
            LTDItem('Utility-vest outfit', 51.2),
            # TODO: LTDItem('Urban hiking combo', 49.1), is not an American item
            LTDItem('Vampire costume', 92.1),
            LTDItem('Varsity-cardigan outfit', 34.1),
            LTDItem('Varsity-jacket outfit', 48.1),
            LTDItem('Viking costume', 188.9),
            # TODO: LTDItem('Vintage flower dress combo', 58.5), is not an American item
            # TODO: LTDItem('Vintage plaid shirt combo', 33.2), is not an American item
            LTDItem('Waitstaff outfit', 34),
            LTDItem('Warm fleece outfit', 60.6),
            LTDItem(LTDName('Wedding-suit outfit', 'Wedding suit set'), 221.5),
            LTDItem('Western outfit', 64.3),
            LTDItem('Windbreaker outfit', 57.3),
            LTDItem('Winter camo outfit', 71),
            LTDItem('Wizard costume', 91.5),
            LTDItem('Work-from-home outfit', 33.8),
            LTDItem('Yoga outfit', 25),
            LTDItem('Animal-print-blouson outfit', 54.7),
            LTDItem('Ao dai outfit', 57.5),
            LTDItem('Aran outfit', 35),
            LTDItem('Aristocratic-dress costume', 2529.1),
            LTDItem('Ballet costume', 213.8),
            LTDItem('Bandanna-top outfit', 62.4),
            LTDItem('Basic-dress outfit', 33.9),
            LTDItem('Beach-vacation outfit', 46.3),
            LTDItem('Biker-jacket outfit', 61.4),
            LTDItem(LTDName('Blazer-with-bow outfit', 'Bow and blazer outfit'), 37.4),
            LTDItem('Botanical-print-skirt outfit', 39.2),
            LTDItem('Business-suit outfit', 43.1),
            LTDItem('Camisole-layered-tee outfit', 38.9),
            LTDItem('Celebrity outfit', 74),
            LTDItem(LTDName('Cheerleader uniform', 'Cheerleader set'), 41),
            LTDItem('Chima jeogori outfit', 60.6),
            LTDItem('Classical-dress outfit', 57.7),
            LTDItem('Classic-maid costume', 97.9),
            LTDItem('Coat-dress outfit', 43.2),
            LTDItem(
                LTDName('Colorful checkered outfit', 'Colourful plaid combo'), 60.8
            ),
            LTDItem('Cozy fleece outfit', 55.7),
            LTDItem('Dance-performance outfit', 65.2),
            LTDItem('Denim-dress outfit', 37.6),
            LTDItem('Dolly-dress outfit', 38.7),
            LTDItem(LTDName('Dolly-shirt outfit', 'Dark dolly set'), 56.6),
            LTDItem('Dreamy-dress outfit', 77.7),
            LTDItem('Dreamy-jacket outfit', 42.8),
            LTDItem('Dreamy-unicorn outfit', 44.6),
            LTDItem('Dress shirt & sweater outfit', 35.6),
            LTDItem(
                LTDName('Duffle coat & skirt outfit', 'Duffle coat and skirt combo'),
                58.2,
            ),
            LTDItem('Elegant-dress outfit', 110.1),
            LTDItem('Energetic-skirt outfit', 33.7),
            LTDItem('Fairy costume', 78.9),
            LTDItem('Faux-fur-coat-dress outfit', 61.5),
            LTDItem('Figure-skating-dress costume', 72.1),
            LTDItem('Flapper-dress outfit', 92.1),
            LTDItem('Flight-attendant outfit', 64.1),
            LTDItem('Floral-sweater outfit', 36.3),
            LTDItem('Flowery outfit', 45),
            LTDItem('Fluffy loungewear outfit', 41.6),
            LTDItem('Formal-dress outfit', 41.9),
            LTDItem('Formal peacoat outfit', 39.2),
            LTDItem('Gaudy bubble-era outfit', 61.7),
            LTDItem('Geometric-skirt outfit', 65.3),
            LTDItem('High-waist-pinafore outfit', 61.1),
            LTDItem('Houndstooth-dress outfit', 43),
            LTDItem('Jumpsuit outfit', 50.1),
            LTDItem('Knit-dress outfit', 58.1),
            LTDItem('Lace-overlay-dress outfit', 87.2),
            LTDItem(LTDName('Lace-top outfit', 'Lace polo neck combo'), 62.9),
            LTDItem('Long-denim-dress outfit', 56.1),
            LTDItem('Long-knit-cardigan outfit', 75),
            LTDItem(
                LTDName(
                    'Long-sleeve tee & skirt outfit', 'Long-sleeved tee & skirt set'
                ),
                44.9,
            ),
            LTDItem('Lovely hearts outfit', 34.2),
            LTDItem('Magical costume', 106.2),
            LTDItem('Maid costume', 89),
            LTDItem('Morning-glory-yukata outfit', 87),
            LTDItem('Multistriped-sweater outfit', 49.3),
            LTDItem('Natural-fiber-dress outfit', 96.1),
            LTDItem('Nordic-sweater outfit', 34.9),
            LTDItem('Nurse outfit', 71.5),
            LTDItem('Over-the-top outfit', 66.8),
            LTDItem('Party-dress outfit', 88.2),
            LTDItem(LTDName('Patchwork outfit', 'Patchwork maxi skirt combo'), 53.1),
            LTDItem('Pinafore-dress outfit', 61.3),
            LTDItem('Plaid-dress outfit', 56.9),
            LTDItem('Polka-dot-dress outfit', 43.1),
            LTDItem('Polo-dress outfit', 52.4),
            LTDItem('Pom-pom-dress outfit', 53.1),
            LTDItem('Pop-idol outfit', 90),
            LTDItem(LTDName('Princess costume', 'Princess attire set'), 670.1),
            LTDItem('Punky skirt outfit', 44.5),
            LTDItem(LTDName('Qipao outfit', 'Qipao set'), 55.6),
            LTDItem('Quilted jacket & skirt outfit', 36.5),
            LTDItem(LTDName('Refreshing lemon outfit', 'Lemon enthusiast outfit'), 29),
            LTDItem('Relaxed tunic-top outfit', 33),
            LTDItem('Retro bedtime outfit', 67),
            LTDItem('Retro-dress outfit', 62.5),
            LTDItem('Retro-floral-dress outfit', 58.5),
            LTDItem('Running outfit', 43.7),
            LTDItem('Sailor-dress outfit', 64.3),
            LTDItem('Sailor school uniform', 36.1),
            LTDItem('Santa-dress outfit', 70.1),
            LTDItem('Sari outfit', 89.9),
            LTDItem('Seaside-stroll outfit', 49.4),
            LTDItem('Semi-formal-kimono outfit', 99.5),
            LTDItem('Shirtdress outfit', 31.9),
            LTDItem(LTDName('Shirt-with-bow outfit', 'Bow and shirt outfit'), 34.4),
            LTDItem('Short-sleeve-cardigan outfit', 32.9),
            LTDItem('Silk-dress outfit', 101.7),
            LTDItem(LTDName('Simple-dress outfit', 'Loose T-shirt dress combo'), 42.3),
            LTDItem('Skipper-collar-shirt outfit', 33.4),
            LTDItem('Skirt & down-jacket outfit', 52.1),
            LTDItem('Sleeveless-shirtdress outfit', 44.1),
            # 'Starter outfit' is not included here, as you cannot give it to a Mii, for all start with one
            LTDItem('Steampunk-dress outfit', 79),
            LTDItem('Stylish heart outfit', 55.3),
            LTDItem(LTDName('Summer-cardigan outfit', 'Summer cardigan combo'), 34),
            LTDItem('Summer sailor school uniform', 55.3),
            LTDItem('Sunny sunflower outfit', 52),
            LTDItem('Sweatshirt & miniskirt outfit', 32.9),
            LTDItem('Tennis uniform', 32.5),
            LTDItem('Tropical-vacation outfit', 48.1),
            LTDItem('Turtleneck-sweater outfit', 37.8),
            LTDItem('Tweed outfit', 117.6),
            LTDItem('Two-toned-shirt outfit', 54.1),
            LTDItem('Tyrolean-dress outfit', 61.1),
            LTDItem('Vintage outfit', 59),
            LTDItem(LTDName('Wedding-dress outfit', 'Wedding dress set'), 1162.1),
            LTDItem('Witch costume', 67),
            LTDItem('Wrap-dress outfit', 44.9),
            LTDItem('Y2K outfit', 41.4),
        ]

    @cached_property
    def clothing_shirts(self) -> list[LTDItem]:
        return [
            LTDItem('Accent-striped polo shirt', 11),
            LTDItem('Animal T-shirt', 14),
            LTDItem('Anorak jacket', 13),
            LTDItem('Argyle vest', 11),
            LTDItem('Balmacaan coat', 18),
            LTDItem('Basic vest', 12),
            LTDItem('Big number T-shirt', 11.5),
            LTDItem('Blazer with bow', 15),
            LTDItem('Blazer with tie', 15),
            LTDItem('Business vest with bow', 14),
            LTDItem('Busy traffic T-shirt', 12),
            LTDItem('Camisole layered T-shirt', 14.3),
            LTDItem("Coach's jacket", 14),
            LTDItem('Collarless coat', 22),
            LTDItem('Collarless shirt', 11.5),
            LTDItem('Colourful shirt', 18),
            LTDItem('Compression shirt', 17.8),
            LTDItem('Cosmic pullover', 16),
            LTDItem('Cyberpunk jacket', 16),
            LTDItem('Denim jacket', 12),
            LTDItem('Dotty shirt', 11.8),
            LTDItem('Dress shirt and cardigan', 13.5),
            LTDItem('Dress shirt and jumper', 13.5),
            LTDItem('Dress shirt with vest', 16),
            LTDItem('Duffle coat', 18),
            LTDItem('Fancy pirate coat', 33),
            LTDItem('Football jersey', 13),
            LTDItem('Frill collar bow blouse', 19),
            LTDItem('Geometric print T-shirt', 12),
            LTDItem('Gingham shirt', 13),
            LTDItem('Gym vest', 11),
            LTDItem('Heart T-shirt', 11.5),
            LTDItem('Hiking jacket', 12),
            LTDItem('Inspirational T-shirt', 11),
            LTDItem('Jockey outfit', 17),
            LTDItem('Kanji T-shirt', 15),
            LTDItem('Kung fu shirt', 15),
            LTDItem('Lace polo neck', 14.3),
            LTDItem('Leopard T-shirt', 16.5),
            LTDItem('Letterman cardigan', 12),
            LTDItem('Long-sleeved crop top', 13),
            LTDItem('Long-sleeved striped T-shirt', 13),
            LTDItem('Mackintosh raincoat', 11.5),
            LTDItem('Male school uniform top', 15),
            LTDItem('Mii logo pullover jacket', 11),
            LTDItem('Mii logo T-shirt', 12),
            LTDItem('Motorcycle jacket', 20),
            LTDItem('Oversized T-shirt', 13),
            LTDItem('Paisley jacket', 13),
            LTDItem('Pea jacket', 17.5),
            LTDItem('Phantom thief attire', 25.5),
            LTDItem('Photo print T-shirt', 12),
            LTDItem('Pilot jacket', 19.9),
            LTDItem('Plaid flannel shirt', 11.4),
            LTDItem('Plain blazer', 20),
            LTDItem('Plain dress shirt', 11),
            LTDItem('Plain jumper', 10),
            LTDItem('Plain long-sleeved T-shirt', 11),
            LTDItem('Plain T-shirt', 10),
            LTDItem('Police uniform top', 14),
            LTDItem('Polo neck pullover', 17),
            LTDItem('Quirky patterned shirt', 13),
            LTDItem('Rectangular Mii logo T-shirt', 15),
            LTDItem('Ringer T-shirt', 10),
            LTDItem('Rock band T-shirt', 13.4),
            LTDItem('Rugby jersey', 12),
            LTDItem('Running vest', 11.5),
            LTDItem('Safety vest', 14),
            LTDItem('Samurai armour', 500),
            LTDItem('Sarashi', 9.5),
            LTDItem('Short-sleeved cardigan', 11),
            LTDItem('Short-sleeved shirt with bow', 12),
            LTDItem('Skull jumper', 10),
            LTDItem('Sleeveless denim shirt', 15),
            LTDItem('Sleeveless shirt', 11),
            LTDItem('Star T-shirt', 12),
            LTDItem('Steampunk coat', 33.5),
            LTDItem('Striped long-sleeved T-shirt', 12.2),
            LTDItem('Striped loungewear', 12),
            LTDItem('Stripy mix shirt', 13.5),
            LTDItem('Suit jacket', 20),
            LTDItem('Summer cardigan', 11),
            LTDItem('Sunny-side-up T-shirt', 12),
            LTDItem('Tailcoat', 150),
            LTDItem('Tailored jacket', 11.5),
            LTDItem('Tennis jumper', 11),
            LTDItem('Tiger baseball jacket', 12),
            LTDItem('Tracksuit jacket', 13.5),
            LTDItem('Tracksuit top', 11),
            LTDItem('Triangles T-shirt', 11.8),
            LTDItem('Tweed jacket', 25),
            LTDItem('University jumper', 13),
            LTDItem('Vintage plaid shirt', 12),
            LTDItem('Waistcoat and T-shirt', 13),
            LTDItem('Wide-striped shirt', 12.5),
            LTDItem('Workwear jacket', 13),
            LTDItem('Wrinkled outfit', 7.5),
            LTDItem('Zip-up hooded sweatshirt', 11),
        ]

    @cached_property
    def clothing_dresses(self) -> list[LTDItem]:
        return [
            LTDItem('Aerobics leotard', 27.9),
            LTDItem("Baseball catcher's uniform", 39),
            LTDItem('Baseball jersey and trousers', 33),
            LTDItem("Basic men's kimono", 45),
            LTDItem('Bathrobe', 15),
            LTDItem('Boilersuit', 23.4),
            LTDItem('Casual jumpsuit', 29),
            LTDItem('Changshan', 32),
            LTDItem('Cheerleading uniform', 29),
            LTDItem('Dreamy dress', 32.5),
            LTDItem('Dungaree dress', 25),
            LTDItem('Dungarees', 25.6),
            LTDItem('Flapper dress', 50),
            LTDItem('Floral dress', 25),
            LTDItem('Flower dress', 27),
            LTDItem("Hemp leaf men's yukata", 37.8),
            LTDItem('Kandora', 39),
            LTDItem('Karate gi', 27.5),
            LTDItem('Katrina dress', 41),
            LTDItem('Kimono', 85),
            LTDItem('Linen dress', 22),
            LTDItem("Painter's boilersuit", 21),
            LTDItem('Plain dress', 40),
            LTDItem('Qipao', 43.5),
            LTDItem('Racing suit', 35),
            LTDItem('Retro mini dress', 29),
            LTDItem('Rumba outfit', 48),
            LTDItem('Steampunk dress', 42),
            LTDItem('T-shirt dress', 20),
            LTDItem('T-shirt dress with logo', 22),
            LTDItem('Wedding dress', 1000),
        ]

    @cached_property
    def clothing_pants(self) -> list[LTDItem]:
        return [
            LTDItem('Accordion pleated skirt', 9.7),
            LTDItem('Basic trousers', 8),
            LTDItem('Basic wide-leg trousers', 11.5),
            LTDItem('Boxing shorts', 7.5),
            LTDItem('Bubble shorts', 9),
            LTDItem('Capri pants', 11),
            LTDItem('Chino shorts', 8.1),
            LTDItem('Chinos', 10),
            LTDItem('Colourful plaid trousers', 9.8),
            LTDItem('Combat shorts', 8.4),
            LTDItem('Combat trousers', 9.4),
            LTDItem('Corduroy trousers', 9),
            LTDItem('Cosmic shorts', 15),
            LTDItem('Cropped wide-leg trousers', 9.5),
            LTDItem('Cyberpunk trousers', 20),
            LTDItem('Denim maxi skirt', 10.2),
            LTDItem('Distressed jeans', 9.5),
            LTDItem('Dotted bubble shorts', 10),
            LTDItem('Dotted maxi skirt', 9.8),
            LTDItem('Fab jeans', 11),
            LTDItem('Frilled mini skirt', 11),
            LTDItem('Gym shorts', 11),
            LTDItem('Japanese monpe trousers', 8.5),
            LTDItem('Japanese pattern trousers', 15),
            LTDItem('Jeans', 9.2),
            LTDItem('Joggers', 8.2),
            LTDItem('Knee pad trousers', 11),
            LTDItem('Knitted skirt', 9.8),
            LTDItem('Lace pencil skirt', 14),
            LTDItem('Lemon pattern skirt', 12),
            LTDItem('Leopard pattern maxi skirt', 12),
            LTDItem('Leopard pattern trousers', 12),
            LTDItem('Long pencil skirt', 12.2),
            LTDItem('Multi stripe trousers', 8.9),
            LTDItem('Patchwork maxi skirt', 9.4),
            LTDItem('Plaid buckle mini skirt', 9.5),
            LTDItem('Plaid hem trousers', 9.2),
            LTDItem('Plaid mini skirt', 9.8),
            LTDItem('Plaid trousers', 35),
            LTDItem('Plaid wide-leg trousers', 12),
            LTDItem('Professional pencil skirt', 11),
            LTDItem('Rocker shorts', 11),
            LTDItem('Running shorts', 11.2),
            LTDItem('Sequin mini skirt', 14),
            LTDItem('Shorts', 9),
            LTDItem('Split hem trousers', 12.5),
            LTDItem('Striped lounge shorts', 8.4),
            LTDItem('Striped maxi skirt', 12),
            LTDItem('Tennis skirt', 9),
            LTDItem('Tiered skirt', 11.5),
            LTDItem('Tracksuit bottoms', 9),
            LTDItem('Tulie skirt', 10),
            LTDItem('Tweed pencil skirt', 30),
            LTDItem('Unicolour trousers', 8.5),
        ]

    @cached_property
    def clothing_hats(self) -> list[LTDItem]:
        return [
            LTDItem('5-panel cap', 15.5),
            LTDItem('Acorn beanie', 18),
            LTDItem('Backwards baseball cap', 16.5),
            LTDItem('Baker boy cap', 18),
            LTDItem('Bandit mask', 21),
            LTDItem('Baseball team cap', 16),
            LTDItem('Beret', 19),
            LTDItem('Big ribbon bow', 19),
            LTDItem('Boater', 18),
            LTDItem('Bunny ears', 19.5),
            LTDItem('Bunny ears ribbon bow', 14),
            LTDItem('Cardboard box hat', 5),
            LTDItem('Cow hood', 20),
            LTDItem('Dog hood', 25),
            LTDItem('Drinking straw', 7),
            LTDItem('Floral hairclip', 9),
            LTDItem('Floral kanzashi haripin', 32),
            LTDItem('Flower hair pin', 8.7),
            LTDItem('Flower headdress', 21.3),
            LTDItem('Flower hood', 20),
            LTDItem('Frill headdress', 32),
            LTDItem('Froggy hood', 26),
            LTDItem('Granny square bucket hat', 15.5),
            LTDItem('Hamster hood', 26),
            LTDItem('Hard hat', 15),
            LTDItem('Heart pattern baseball cap', 11),
            LTDItem('Heart sunglasses', 19.9),
            LTDItem('Hypno glasses', 12),
            LTDItem('Ice hockey mask', 18.7),
            LTDItem('Jockey cap', 17),
            LTDItem('Monkey hood', 20),
            LTDItem('Open face helmet', 23),
            LTDItem('Paper bag', 2),
            LTDItem('Pixel sunglasses', 10),
            LTDItem('Plaid baker boy cap', 18.5),
            LTDItem('Plaid beret', 20),
            LTDItem('Plain baseball cap', 10),
            LTDItem('Plain beanie', 10),
            LTDItem('Plate armour helmet', 420),
            LTDItem('Pop-out eye glasses', 12.3),
            LTDItem('Printed-design mask', 8),
            LTDItem('Propeller cap', 11),
            LTDItem('Rabbit hood', 23),
            LTDItem('Samurai helmet', 150),
            LTDItem('Shampoo bubbles hat', 12),
            LTDItem('Sheep hood', 25),
            LTDItem('Snap hair clip', 5.8),
            LTDItem('Snorkelling set', 18),
            LTDItem('Space suit helmet', 2000),
            LTDItem('Spangly hat', 25),
            LTDItem('Star sunglasses', 14),
            LTDItem('Tower hair wrap', 6),
            LTDItem('Tulip hat', 15),
            LTDItem('Turkey hood', 35),
            LTDItem('Wedding tiara', 150),
        ]

    @cached_property
    def clothing_accessories(self) -> list[LTDItem]:
        return [
            LTDItem('Angelic wings', 20),
            LTDItem('Basic scarf', 17),
            LTDItem('Bead necklace', 15),
            LTDItem('Bow tie', 7),
            LTDItem('Butterfly wings', 17),
            LTDItem('Buttonhole flower', 49),
            LTDItem('Chain necklace', 16),
            LTDItem('Cow tail', 12),
            LTDItem('Cute badge', 6.1),
            LTDItem('Fairy wings', 18),
            LTDItem('Flower garland', 16),
            LTDItem('Happy flowers', 5),
            LTDItem('Headphones', 16),
            LTDItem('Katana', 100),
            LTDItem('Lanyard with name badge', 14),
            LTDItem('Love hearts', 15),
            LTDItem('Magic symbol', 21),
            LTDItem('Pearl brooch', 38),
            LTDItem('Pearl necklace', 50),
            LTDItem('Practical rucksack', 14),
            LTDItem('Ring necklace', 30),
            LTDItem('Rose corsage', 30),
            LTDItem('Rose petals', 17),
            LTDItem('Rosette', 15),
            LTDItem('Rosette pin', 50),
            LTDItem('Snood', 18),
            LTDItem('Spiky choker', 12),
            LTDItem('Star necklace', 17),
            LTDItem('Studded rucksack', 21),
            LTDItem('Triple-chain necklace', 35),
            LTDItem('Turtle shell', 25),
            LTDItem('Whistle', 6),
            LTDItem('Wind-up key', 15.5),
            LTDItem('Wooden bead necklace', 18),
        ]

    @cached_property
    def clothing_socks(self) -> list[LTDItem]:
        return [
            LTDItem('Ankle socks', 4.8),
            LTDItem('Back ribbon socks', 5.2),
            LTDItem('Colourful plaid socks', 5.5),
            LTDItem('Compression leg sleeves', 8.2),
            LTDItem('Corduroy legwarmers', 5.2),
            LTDItem('Cosmic thigh highs', 7.7),
            LTDItem('Cuff striped ankle socks', 4.6),
            LTDItem('Double striped socks', 5),
            LTDItem('Embroidered socks', 4.7),
            LTDItem('Fishnet stockings', 4.5),
            LTDItem('Floral knee-high socks', 6),
            LTDItem('Floral-stitch thigh highs', 6.2),
            LTDItem('Mismatched thigh highs', 7.5),
            LTDItem('Monster socks', 7.9),
            LTDItem('No-show socks', 4.5),
            LTDItem('Plaid ankle socks', 5.2),
            LTDItem('Plain legwarmers', 5),
            LTDItem('Plain socks', 4.5),
            LTDItem('Plain thigh highs', 5),
            LTDItem('Polka dot legwarmers', 5.2),
            LTDItem('Retro plaid socks', 5.3),
            LTDItem('Ruffled socks', 5.8),
            LTDItem('Sheer dotted socks', 5.1),
            LTDItem('Stockings', 5.1),
            LTDItem('Sushi socks', 10),
            LTDItem('Tabi socks', 4.5),
            LTDItem('Thigh warmers', 4),
        ]

    @cached_property
    def clothing_shoes(self) -> list[LTDItem]:
        return [
            LTDItem('Ankle boots', 8),
            LTDItem('Boat shoes', 7.8),
            LTDItem('Business shoes', 10),
            LTDItem('Cosmic trainers', 8),
            LTDItem('Cowboy boots', 9.1),
            LTDItem('Engineer boots', 8.2),
            LTDItem('Flip-flops', 5.5),
            LTDItem('Flower sandals', 6),
            LTDItem('Glitter pumps', 15),
            LTDItem('Japanese geta sandals', 8),
            LTDItem('Japanese zori sandals', 10),
            LTDItem('Kids trainers', 6),
            LTDItem('Korean flower shoes', 12),
            LTDItem('Kung fu shoes', 5.5),
            LTDItem('Lace-up boots', 7.8),
            LTDItem('Loafers', 7.9),
            LTDItem('Long pleather boots', 8.5),
            LTDItem('Plain pumps', 7),
            LTDItem('Plain trainers', 7),
            LTDItem('Princess shoes', 30),
            LTDItem('Punk boots', 9),
            LTDItem('Ribbon bow pumps', 7.5),
            LTDItem('Ribbon bow strappy pumps', 7.7),
            LTDItem('Roman sandals', 5.9),
            LTDItem('Rubber slippers', 5.5),
            LTDItem('Rubber-toed high-tops', 7.8),
            LTDItem('Rubber-toed trainers', 7.1),
            LTDItem('Samurai boots', 25),
            LTDItem('Shoes with colourful socks', 6.5),
            LTDItem('Shoes with stripy socks', 8.5),
            LTDItem('Shower slippers', 5.3),
            LTDItem('Side stripe trainers', 7.2),
            LTDItem('Slip-ons', 6.9),
            LTDItem('Slippers', 5.2),
            LTDItem('Strappy pumps', 6.9),
            LTDItem('Studded dress shoes', 11),
            LTDItem('Track spikes', 6),
            LTDItem('Trekking boots', 8),
            LTDItem('Vintage boots', 8),
            LTDItem('Wellies', 6.7),
            LTDItem('Zebra pattern pumps', 7.3),
        ]

    @cached_property
    def clothing_costumes(self) -> list[LTDItem]:
        return [
            LTDItem('Bodysuit', 25),
            LTDItem('Bubble tea outfit', 25),
            LTDItem('Building outfit', 40),
            LTDItem('Bunny outfit', 33),
            LTDItem('Cake outfit', 35),
            LTDItem('Cardboard robot suit', 7),
            LTDItem('Car outfit', 40),
            LTDItem('Corn on the cob outfit', 26),
            LTDItem('Cow outfit', 25),
            LTDItem('Daruma outfit', 23),
            LTDItem('Dustbin outfit', 18),
            LTDItem('Fizzy drink outfit', 24),
            LTDItem('Fried prawn outfit', 25),
            LTDItem('Froggy outfit', 26.6),
            LTDItem('Hamster outfit', 25),
            LTDItem('Heavy metal outfit', 31.5),
            LTDItem('Monkey outfit', 26),
            LTDItem('Pig outfit', 28),
            LTDItem('Playing card outfit', 21),
            LTDItem('Police car outfit', 45),
            LTDItem('Sheep outfit', 25),
            LTDItem('Spacesuit', 3000),
            LTDItem('Train outfit', 43),
        ]

    # TODO: Only some treasures have been implemented, use item database to populate the rest

    @cached_property
    def treasures_base(self) -> list[LTDItem]:
        return [
            LTDItem('9-volt battery', 3.4),
            LTDItem('alebrije', 34),
            LTDItem('alpaca', 120),
            LTDItem('balloon animal', 5),
            LTDItem('bird feather', 5),
            LTDItem('botanical field guide', 25),
            LTDItem('botijo', 87),
            LTDItem('bottle of perfume', 51),
            LTDItem('bouquet', 40),
            LTDItem('box of tissues', 1.2),
            LTDItem('bunch of carnations', 10),
            LTDItem('call bell', 5),
            LTDItem('ceremonial mountain of buns', 33),
            LTDItem('chess piece', 3),
            LTDItem('chick', 15),
            LTDItem('compass', 5.3),
            LTDItem('crystal', 60),
            LTDItem('crystal ball', 75.5),
            LTDItem('cut-glass ornament', 50),
            LTDItem('dance music album', 30),
            LTDItem('dancing game', 38),
            LTDItem('Daruma-otoshi game', 5),
            LTDItem(LTDName('dating-sim game', 'dating sim game'), 53),
            LTDItem('die', 1),
            LTDItem('disco ball', 200),
            LTDItem('embroidered decoration', 33),
            LTDItem('flamingo', 150),
            LTDItem('foxtail frond', 0.2),
            LTDItem('globe', 34),
            LTDItem('gold ingot', 1000),
            LTDItem('hand mirror', 17),
            LTDItem('hedgehog', 20),
            LTDItem('historical bust', 67),
            LTDItem('horror film', 15),
            LTDItem('horror game', 62),
            LTDItem('hourglass', 3.2),
            LTDItem('insect collection', 81),
            LTDItem('J-pop album', 30),
            LTDItem('jellyfish', 3),
            LTDItem('Jōmon-era pottery', 130),
            LTDItem('kettle', 9),
            LTDItem('koala cuddly toy', 36),
            LTDItem('lightbulb', 5.5),
            LTDItem('lion', 200),
            LTDItem('loofah', 2),
            LTDItem('love story', 8),
            LTDItem('lump of amber', 200),
            LTDItem('magnifying glass', 10),
            LTDItem('moon-shaped lamp', 19),
            LTDItem('mysterious egg', 2),
            LTDItem('mysterious solution', 1.5),
            LTDItem('octopus', 20),
            LTDItem('pair of binoculars', 34),
            LTDItem('penguin', 150),
            LTDItem('picture postcard set', 18),
            LTDItem('piece of coral', 53),
            LTDItem('pig', 120),
            LTDItem('pop album', 25),
            LTDItem('puzzle game', 38),
            LTDItem('rabbit', 45),
            LTDItem('racing game', 55),
            LTDItem('reggae album', 25),
            LTDItem('restaurant menu', 12),
            LTDItem(LTDName('rock album', "rock 'n' roll album"), 25),
            LTDItem('roll of toilet paper', 1),
            LTDItem('romantic drama', 15),
            LTDItem('rose', 10),
            LTDItem('rubber duck', 4),
            LTDItem('sci-fi film', 20),
            LTDItem('sea urchin skeleton', 0.1),
            LTDItem('shark', 150),
            LTDItem('ship in a bottle', 45),
            LTDItem('solar panel', 150),
            LTDItem('spinning top', 7),
            LTDItem('stick', 0.3),
            LTDItem('stopwatch', 16),
            LTDItem('supposedly expensive vase', 400),
            LTDItem('tanuki statue', 30),
            LTDItem('tap', 4),
            LTDItem('tawashi scrub brush', 1),
            LTDItem('treasure map', 99),
            LTDItem('tuna', 150),
            LTDItem('UFO', 58),
            LTDItem('unicorn', 300),
            LTDItem('vacuum tube', 18),
            LTDItem('variety show', 15),
            LTDItem('video game soundtrack', 25),
            LTDItem('water flea', 1),
            LTDItem('weak-looking elastic cord', 1),
        ]

    @cached_property
    def gifts_prezzies(self) -> list[str]:
        return [
            '"Ballet For The Bumbling" DVD',
            '"Breaking Into Breaking" DVD',
            '"Sensei-Tional Karate" DVD',
            'Baseball',
            '"Yoga: A Balanced View" DVD',
            '"Bulk Your Bod" DVD',
            'Guitar',
            'Set Of Paints',
            'Toy Sword',
            'Camera',
            'Football',
            'Bubble Blower',
            'Maracas',
            'Knitting Kit',
            '"Jogging: A Rundown" DVD',
            'Laptop',
            # While Kid-o-matic is a separate category to prezzies, it is included here due to it functioning similarly
            'Kid-o-matic',
        ]

    @cached_property
    def gifts_little_quirks(self) -> list[str]:
        return [
            # Greeting
            'Greets eagerly',
            'Greets energetically',
            'Greets cheekily',
            'Greets macho-style',
            'Greets enthusiastically',
            'Greets with a curtsy',
            'Greets powerfully',
            'Greets smugly',
            'Greets shyly',
            "Greets like it's a bother",
            'Greets with a forwards bow',
            'Greets with a nod',
            'Greets with a sweeping bow',
            "Won't greet others",
            # Standing
            'Stands cutely',
            'Stands proudly',
            'Stands confidently',
            'Stands bow-legged',
            'Stands moving to the rhythm',
            'Stands shaking hips',
            'Stands while wiping sweat',
            'Stands with arms crossed',
            'Stands with hands folded',
            'Stands shyly',
            'Stands restlessly',
            'Stands at attention',
            'Stands leaning forwards',
            'Stands while adjusting glasses',
            # Walking
            'Walks with a swagger',
            'Walks bow-legged',
            'Walks with a rhythm',
            'Walks like a model',
            'Walks like a robot',
            'Walks like an astronaut',
            'Walks cutely',
            'Walks leaning forwards',
            'Walks with tiny steps',
            'Walks nervously',
            'Walks without swinging arms',
            'Floats instead',
            # Eating
            'Eats with gusto',
            'Eats voraciously',
            'Eats while savouring',
            'Eats blissfully',
            'Eats gracefully',
            'Eats quickly',
            'Eats cautiously',
            'Eats shyly',
            # Appetite
            'Big eater',
            'Light eater',
            # Anger
            'Flips out when angry',
            'Grins when angry',
            'Cries when angry',
            # Face
            'Smug',
            'Smiley',
            'Wide-eyed',
            'Winky',
            'Blissful',
            'Raised eyebrows',
            'Unimpressed',
            'Closed eyes',
            'Nonchalant',
            # Voice
            'Outdoor voice',
            'Radiant voice',
            'Library voice',
            'Creepy voice',
            # Extras
            'Shameless farter',
            'Snores like a chainsaw',
            'Restless sleeper',
            'Lashes out',
            'Fainthearted',
            'Night owl',
            'Fashionista',
            'Blinks a lot',
        ]

    @cached_property
    def gifts_expressions(self) -> list[str]:
        return [
            'Starting a sentence',
            'Ending a sentence',
            'A pet phrase',
            'When happy',
            'When sad',
            'When angry',
            'Greeting',
            'While sleeping',
            'Shouted at the sea',
            'Before eating',
        ]

    # TODO: Only some interior sets have been implemented, use item database to populate the rest

    @cached_property
    def interiors_base(self) -> list[LTDItem]:
        interiors: list[LTDItem] = [
            LTDItem('8-Bit', 188),
            LTDItem('All Aboard', 250),
            LTDItem('Aristocrat', 1000),
            LTDItem('Bathhouse', 180),
            LTDItem('Birthday Blowout', 150),
            LTDItem('Bookworm', 135),
            LTDItem('Camo Campsite', 110),
            LTDItem('Cuddly Kingdom', 76),
            LTDItem('Damask', 131),
            LTDItem('Desert Oasis', 85),
            LTDItem("Emperor's Chambers", 122),
            LTDItem('Eureka', 200),
            LTDItem('Exposed Brick', 80),
            LTDItem('Fair-weather Wedding', 225),
            LTDItem('Feline Friend', 120),
            LTDItem('Flower Meadow', 80),
            LTDItem('Garage', 115),
            LTDItem('Gym Rat', 85),
            LTDItem('Haunted House', 134),
            LTDItem('Heart Overload', 82),
            LTDItem('Honeycomb', 78),
            LTDItem('Hospital', 151),
            LTDItem('Humble Herder', 82),
            LTDItem('In the Doghouse', 79),
            LTDItem('Jailbird', 50),
            LTDItem('Log Cabin', 81),
            LTDItem('Marble', 215),
            LTDItem('Minimalist', 50),
            LTDItem('Monochromatic', 20),
            LTDItem('Moving In', 35),
            LTDItem('Natural Wood', 70),
            LTDItem('Nothing But Mii', 20),
            LTDItem('Office', 145),
            LTDItem('Ornate', 125),
            LTDItem('Outside the Lines', 91),
            LTDItem('Plant Parent', 120),
            LTDItem('Playroom', 76),
            LTDItem('Polka Dot', 100),
            LTDItem("Pots 'n' Pans", 90),
            LTDItem('Raining Buckets', 55),
            LTDItem('Retro', 175),
            LTDItem('Shabby', 15),
            LTDItem('Simple Living', 70),
            LTDItem('Spooky Cemetery', 171),
            LTDItem('Starry-Eyed', 61),
            LTDItem('Sushi', 340),
            LTDItem('Sweet Treat', 125),
            LTDItem('Teahouse', 200),
            LTDItem('Top Floor', 350),
            LTDItem('Tri As You Might', 95),
            LTDItem('Under Construction', 155),
            LTDItem('Urban Underground', 125),
            LTDItem('Veni Vidi Vici', 140),
            LTDItem('Wedding', 320),
        ]
        for interior in interiors:
            interior.name = f"{interior.name} set"
        return interiors

    # TODO: Only some objects have been implemented, use item database to populate the rest

    @cached_property
    def objects_props(self) -> list[LTDItem]:
        return [
            LTDItem('Animal spring rider', 78),
            LTDItem('Bird whirligig', 18),
            LTDItem('Braizer', 5),
            LTDItem('Campfire', 12),
            LTDItem('Deck chair', 30),
            LTDItem('Drinking fountain', 12),
            LTDItem('Garden bench', 21),
            LTDItem('Globe streetlight', 10),
            LTDItem('Ground light', 10),
            LTDItem('Hanging bell', 22),
            LTDItem('Inflatable arch', 50),
            LTDItem('Lighthouse', 100),
            LTDItem('Litter bin', 40),
            LTDItem('Open-air shower', 40),
            LTDItem('Outdoor dining set', 43),
            LTDItem('Parasol', 30),
            LTDItem('Park bench', 25),
            LTDItem('Picnic table', 62),
            LTDItem('Seesaw', 70),
            LTDItem('Sprinkler', 35),
            LTDItem('Street clock', 30),
            LTDItem('Throne', 1000),
            LTDItem('Traffic cone', 10),
            LTDItem('Traffic light', 45),
            LTDItem('Vending machine', 120),
            LTDItem('Victorian streetlight', 15),
            LTDItem('Warning sign', 20),
            LTDItem('Wind turbine', 300),
        ]

    @cached_property
    def objects_fences(self) -> list[LTDItem]:
        return [
            LTDItem('Barbed wire fencing', 4.2),
            LTDItem('Beach steps (metal)', 9.99),
            LTDItem('Beach steps (stone)', 10),
            LTDItem('Beach steps (wooden)', 9.99),
            LTDItem('Guard rail', 6),
            LTDItem('Hoop barrier', 5),
            LTDItem('Iron fencing', 3.7),
            LTDItem('Lattice fence', 3.5),
            LTDItem('Picket fence', 3),
            LTDItem('Pipe guard rail', 4),
            LTDItem('Post and chain fencing', 3.5),
            LTDItem('Wooden stake fence', 2.5),
        ]

    @cached_property
    def objects_foliage(self) -> list[LTDItem]:
        return [
            LTDItem('Boulder', 3),
            LTDItem('Broad-leaved tree', 7),
            LTDItem('Broad-leaved tree (autumn)', 7),
            LTDItem('Cosmos flowers', 2.2),
            LTDItem('Ginkgo tree', 5),
            LTDItem('Hedge', 5.5),
            LTDItem('Hedge (autumn)', 5.5),
            LTDItem('Hedge (fragrant olive)', 5.5),
            LTDItem('Palm tree', 8),
            LTDItem('Patch of grass', 1),
            LTDItem('Patch of grass (withered)', 1),
            LTDItem('Pine tree', 7),
            LTDItem('Raised brick flower bed', 10),
            LTDItem('Silvergrass', 1.8),
        ]

    @cached_property
    def objects_buildings_base(self) -> list[LTDItem]:
        return [
            LTDItem('Restaurant', 300),
            LTDItem('Clothes Shop', 1000),
            LTDItem('Supermarket', 1000),
            LTDItem('Island Design Centre', 1000),
            LTDItem('Treasure Shop', 1000),
            LTDItem('Studio Workshop', 1000),
            LTDItem('Photo Studio', 1000),
            LTDItem('News Station', 1000),
            LTDItem('Pawn Shop', 3000),
            LTDItem('Renovation Centre', 3000),
            LTDItem('Ferris Wheel', 8000),
            LTDItem('Market Stall', 5000),
        ]

    @cached_property
    def landscapes_base(self) -> list[str]:
        return [
            'Arched Cobblestone',
            'Asphalt',
            'Brick',
            'Clovers',
            'Cobblestone',
            'Concrete',
            'Crushed Sandstone',
            'Dirt',
            'Fallen Leaves',
            'Grass',
            'Sand',
            'Steel Plate',
            'Wooden Boards',
            'Sandy Beach',
            'Sea',
        ]

    def item_is_trash(self, item: LTDItem) -> bool:
        """
        Returns whether a Tomodachi Life: Living the Dream item is trash based on its name.

        Args:
            item (LTDItem): The item to check.

        Returns:
            bool: Whether the item is trash. This is always false if `tomodachi_life_living_the_dream_trash_items` is true.
        """
        return (
            not self.archipelago_options.tomodachi_life_living_the_dream_trash_items.value
            and item.name
            in [
                'banana peel',
                'moldy bread',
                'ruined bread',
                'spoiled milk',
                'Box of tissues',
                'Roll of toilet paper',
            ]
        )

    ITEM_MAX_WEIGHT: int = 4

    def get_item_strings(self, items: list[LTDItem]) -> list[str]:
        """
        Converts a list of Tomodachi Life: Living the Dream items with names and costs into a list of strings. The strings are duplicated based on the costs of the items, to ensure that cheaper items are found more commonly in the list. Items with no cost can only be obtained under special circumstances, so they are assumed to have the maximum cost.

        Args:
            items (list[LTDItem]): The list of items to convert.

        Returns:
            list[str]: The weighted list of strings.
        """
        # Get all items for the given region, also get min and max costs
        min_cost: float = float("inf")
        max_cost: float = 0
        for item in items:
            if self.item_is_trash(item) or item.cost is None:
                continue
            min_cost = min(min_cost, item.cost)
            max_cost = max(max_cost, item.cost)
        # Duplicate items based on their costs, cheaper items appear more frequently
        cost_diff: float = max_cost - min_cost
        region: int = (
            self.archipelago_options.tomodachi_life_living_the_dream_region.value
        )
        if cost_diff == 0:
            return [
                (
                    item.name
                    if isinstance(item.name, str)
                    else (
                        item.name.na
                        if region == TomodachiLifeLTDRegion.option_north_america
                        else item.name.eu
                    )
                )
                for item in items
                if not self.item_is_trash(item)
            ]
        weighted_items: list[str] = []
        for item in items:
            if self.item_is_trash(item):
                continue
            if item.cost is None:
                item.cost = max_cost
            item_weight: int = (
                round(((max_cost - item.cost) / cost_diff) * (self.ITEM_MAX_WEIGHT - 1))
                + 1
            )
            for _ in range(item_weight):
                weighted_items.append(
                    item.name
                    if isinstance(item.name, str)
                    else (
                        item.name.na
                        if region == TomodachiLifeLTDRegion.option_north_america
                        else item.name.eu
                    )
                )
        return weighted_items

    def miis(self) -> list[str]:
        return self.archipelago_options.tomodachi_life_living_the_dream_miis.value

    def food(self) -> list[str]:
        food: list[str] = self.get_item_strings(
            [*self.food_food, *self.food_desserts, *self.food_drinks]
        )
        if (
            "food"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                food.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "food"
                    ]
                )
        return food

    def clothing(self) -> list[str]:
        clothing: list[str] = self.get_item_strings(
            [
                *self.clothing_outfits,
                *self.clothing_shirts,
                *self.clothing_dresses,
                *self.clothing_pants,
                *self.clothing_hats,
                *self.clothing_accessories,
                *self.clothing_socks,
                *self.clothing_shoes,
                *self.clothing_costumes,
            ]
        )
        if (
            "clothing"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                clothing.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "clothing"
                    ]
                )
        return clothing

    def treasures(self) -> list[str]:
        treasures: list[str] = self.get_item_strings(self.treasures_base)
        if (
            "treasures"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                treasures.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "treasures"
                    ]
                )
        return treasures

    def gifts(self) -> list[str]:
        return [
            *[f"{gift} prezzie" for gift in self.gifts_prezzies],
            *[f"{gift} little quirk" for gift in self.gifts_little_quirks],
            *[f"{gift} expression" for gift in self.gifts_expressions],
        ]

    def interiors(self) -> list[str]:
        interiors: list[str] = self.get_item_strings(self.interiors_base)
        interiors = [
            *[f"{interior} entire room interior" for interior in interiors],
            *[f"{interior} wallpaper" for interior in interiors],
            *[f"{interior} flooring" for interior in interiors],
        ]
        if (
            "interiors"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                interiors.extend(
                    [
                        *[
                            f"{interior} wallpaper"
                            for interior in self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                                "interiors"
                            ]
                        ],
                        *[
                            f"{interior} flooring"
                            for interior in self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                                "interiors"
                            ]
                        ],
                    ]
                )
        return interiors

    def exteriors(self) -> list[str]:
        return (
            self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                "exteriors"
            ]
            if "exteriors"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
            else []
        )

    @staticmethod
    def object_amounts() -> list[str]:
        return [f"{i} new {'copy' if i == 1 else 'copies'}" for i in range(1, 5 + 1)]

    def objects_non_buildings(self) -> list[str]:
        objects: list[str] = self.get_item_strings(
            [*self.objects_props, *self.objects_fences, *self.objects_foliage]
        )
        if (
            "objects"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                objects.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "objects"
                    ]
                )
        return objects

    def objects_buildings(self) -> list[str]:
        return self.get_item_strings(self.objects_buildings_base)

    @staticmethod
    def landscape_amounts() -> range:
        return range(10, 30 + 1, 5)

    def landscapes(self) -> list[str]:
        landscapes: list[str] = self.landscapes_base
        if (
            "landscapes"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                landscapes.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "landscapes"
                    ]
                )
        return landscapes

    @staticmethod
    def bonus_objectives_base() -> list[str]:
        bonuses_base: list[str] = [
            'Allow a Mii to run up to another Mii',
            'Allow a Mii to style their own hair',
            "Answer a Mii's 'quick chat' question with a typed response",
            "Change the island's terrain using the Island Builder",
            'Create new clothing at the Studio Workshop',
            'Create a new exterior at the Studio Workshop',
            'Create a new food at the Studio Workshop',
            'Create a new interior at the Studio Workshop',
            'Create a new landscape at the Studio Workshop',
            'Create a new object at the Studio Workshop',
            'Create a new treasure at the Studio Workshop',
            'Create a new Mii based on an existing island Mii',
            'Create a new Mii from a Mii on console',
            'Create a new Mii from scratch',
            'Create a new Mii using prompts',
            'Create a new Mii with face paint',
            'Create a new Mii with the least in-use personality',
            'Delete an entry from the Island Dictionary',
            'Do a Group photoshoot at the Photo Studio',
            'Do a Pair photoshoot at the Photo Studio',
            'Do an All Residents photoshoot at the Photo Studio',
            "Edit a Mii's appearance",
            "Edit a Mii's voice",
            "Edit an existing creation at the Studio Workshop",
            'Give a Mii $10 in pocket money',
            'Give a Mii $50 in pocket money',
            'Give a Mii $100 in pocket money',
            'Give a Mii $250 in pocket money',
            'Give a Mii clothing as a level-up gift',
            'Grant a wish from the Wishing Fountain',
            'Help a Mii make up with an angry Mii',
            'Help a paralysed Mii using another Mii',
            'Help a paralysed Mii yourself',
            'Introduce a Mii to another Mii they are strangers to',
            'Let a Mii conduct a construction project',
            'Let a Mii place a single object on the island',
            "Listen to a Mii's random thought",
            "Look inside a Mii's dream",
            'Observe a dismissive conversation in the Restaurant',
            'Observe a Mii performing an action based on a prezzie',
            'Observe a normal conversation in the Restaurant',
            'Observe a romantic conversation in the Restaurant',
            'Observe a theatrical conversation in the Restaurant',
            'Observe a Mii spontaneously fall for another Mii',
            'Pet a Mii to dispel their anger',
            'Pet a Mii to dispel their sadness',
            'Play a game of Bowling',
            'Play a game of Coin Spin',
            'Play a game of Double Shadow Quiz',
            'Play a game of Latte Art Quiz',
            'Play a game of Moving Cups',
            'Play a game of No Repeats (in a group or not)',
            'Play a game of Odd One Out',
            'Play a game of Pixel Quiz',
            'Play a game of Poke the Ferris Wheel',
            'Play a game of Red Light, Green Light',
            'Play a game of Shadow Quiz',
            "Play a game of What's Missing",
            'Play a game of Zoom Quiz',
            'Remove a Mii',
            'Save and trim a Nintendo Switch video recording of the game',
            'Save your progress',
            'Sell extra copies of treasures at the Pawn Shop',
            "Solve a Mii's personal problem",
            "Solve a Mii's problem related to another Mii",
            "Solve a Mii's romantic problem",
            'Stock up on clothing at the Clothes Shop',
            'Stock up on food at the Supermarket',
            'Stock up on objects at the Island Design Centre',
            'Stock up on interiors at the Renovation Centre',
            'Watch old Mii News',
            'Watch the latest Mii News',
        ]
        tours: list[str] = [
            'Oceania',
            'Hawaii',
            'Kyoto',
            'Latin America',
            'Western Europe',
            'Southeast Asia',
            'Northern Europe',
            'USA',
            'East Asia',
            'Central/Eastern Europe',
            'Africa',
            'Mediterranean',
            'South Asia',
            'Famous Mountains',
            'World Caves',
            'World Castles',
            'Galapagos Islands',
            'Iconic Scenery',
            'Outer Space',
        ]
        bonuses_tours: list[str] = [
            f"Give a Mii a {tour} Tour travel ticket" for tour in tours
        ]
        return bonuses_base * 4 + bonuses_tours

    @staticmethod
    def bonus_objectives_time_consuming() -> list[str]:
        return [
            'Allow a Mii to move in with another Mii',
            'Collect donations at the Wishing Fountain',
            'Purchase an item from the Morning Market',
            'Purchase an item from the Afternoon Market',
            'Purchase a mystery bag from the Night Market',
            'Wake up a Mii sleeping in their bed',
            'Witness two Miis reveal their newborn Mii to you',
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = (
            self.archipelago_options.tomodachi_life_living_the_dream_weights.value
        )
        factor: int = 100
        objectives: list[GameObjectiveTemplate] = [
            GameObjectiveTemplate(
                label=f"Feed FOOD{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''} to any Mii",
                data={"FOOD": (self.food, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_food"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Dress any Mii in CLOTHING{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                data={"CLOTHING": (self.clothing, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_clothing"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Give any Mii the TREASURE treasure{' if owned' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                data={"TREASURE": (self.treasures, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_treasure"] * factor,
            ),
            GameObjectiveTemplate(
                label="Give the GIFT to any Mii on level up",
                data={"GIFT": (self.gifts, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_level_up_gift"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Renovate any Mii's home with the INTERIOR{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                data={"INTERIOR": (self.interiors, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_interior"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Place AMOUNT of OBJECT{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''} using the Island Builder",
                data={
                    "AMOUNT": (self.object_amounts, 1),
                    "OBJECT": (self.objects_non_buildings, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["place_objects"] * factor,
            ),
            GameObjectiveTemplate(
                # Do not require the player to buy more than one extra of each building, as they are very expensive
                label=f"Place or move second BUILDING{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''} using the Island Builder",
                data={"BUILDING": (self.objects_buildings, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["place_building"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Draw AMOUNT tiles of LANDSCAPE{' if owned' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''} using the Island Builder",
                data={
                    "AMOUNT": (self.landscape_amounts, 1),
                    "LANDSCAPE": (self.landscapes, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["place_landscapes"] * factor,
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["bonus"] * factor * 0.9),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_time_consuming, 1)},
                is_time_consuming=True,
                is_difficult=False,
                weight=int(weights["bonus"] * factor * 0.1),
            ),
        ]
        if len(self.exteriors()) > 0:
            objectives.append(
                GameObjectiveTemplate(
                    label=f"Renovate any Mii's home with the EXTERIOR exterior{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                    data={"EXTERIOR": (self.exteriors, 1)},
                    is_time_consuming=False,
                    is_difficult=False,
                    weight=weights["any_mii_named_exterior"] * factor,
                )
            )
        if len(self.archipelago_options.tomodachi_life_living_the_dream_miis.value) > 0:
            objectives.extend(
                [
                    GameObjectiveTemplate(
                        label="Feed MII",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_any_food"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Dress up MII",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_any_clothing"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Give MII any treasure",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_any_treasure"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Level up MII",
                        data={"MII": (self.miis, 1)},
                        # It may take a long time to level up a specific Mii
                        is_time_consuming=True,
                        is_difficult=False,
                        weight=weights["named_mii_any_level_up_gift"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Renovate the home of MII with any entire room interior",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=int(weights["named_mii_any_interior"] * factor / 3),
                    ),
                    GameObjectiveTemplate(
                        label="Renovate the home of MII with any wallpaper",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=int(weights["named_mii_any_interior"] * factor / 3),
                    ),
                    GameObjectiveTemplate(
                        label="Renovate the home of MII with any flooring",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=int(weights["named_mii_any_interior"] * factor / 3),
                    ),
                    GameObjectiveTemplate(
                        label=f"Feed FOOD{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''} to MII",
                        data={"FOOD": (self.food, 1), "MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_named_food"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label=f"Dress MII in CLOTHING{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                        data={"CLOTHING": (self.clothing, 1), "MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_named_clothing"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label=f"Give MII the TREASURE treasure{' if owned' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                        data={"MII": (self.miis, 1), "TREASURE": (self.treasures, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_named_treasure"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Give the GIFT to MII on level up",
                        data={"GIFT": (self.gifts, 1), "MII": (self.miis, 1)},
                        # It may take a long time to level up a specific Mii
                        is_time_consuming=True,
                        is_difficult=False,
                        weight=weights["named_mii_named_level_up_gift"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label=f"Renovate the home of MII with the INTERIOR{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                        data={"INTERIOR": (self.interiors, 1), "MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_named_interior"] * factor,
                    ),
                ]
            )
            if len(self.exteriors()) > 0:
                objectives.extend(
                    [
                        GameObjectiveTemplate(
                            label="Renovate the home of MII with any exterior",
                            data={"MII": (self.miis, 1)},
                            is_time_consuming=False,
                            is_difficult=False,
                            weight=weights["named_mii_any_exterior"] * factor,
                        ),
                        GameObjectiveTemplate(
                            label=f"Renovate the home of MII with the EXTERIOR exterior{' if unlocked' if self.archipelago_options.tomodachi_life_living_the_dream_skip_locked_items.value else ''}",
                            data={
                                "EXTERIOR": (self.exteriors, 1),
                                "MII": (self.miis, 1),
                            },
                            is_time_consuming=False,
                            is_difficult=False,
                            weight=weights["named_mii_named_exterior"] * factor,
                        ),
                    ]
                )
        return objectives
