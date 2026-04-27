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

WARNING: This implementation is incomplete, as it does not support all of the items in the game. Jack5 has only added the items that he has unlocked, as he was unable to find an items database online. Once a database is found, this implementation will be updated.
"""

from dataclasses import dataclass
from functools import cached_property
from Options import (  # pyright: ignore[reportMissingImports]
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


class TomodachiLifeLTDTrash(Toggle):
    """
    Whether to allow trash treasures ('Box of tissues' and 'Roll of toilet paper') to appear as part of Tomodachi Life objectives.
    """

    display_name: str = "Tomodachi Life: Living the Dream Trash"


class TomodachiLifeLTDMiis(OptionList):
    """
    The list of names of Miis living in a given copy of Tomodachi Life: Living the Dream, to use for objectives that require a specific Mii. If empty, specific Mii objectives will not appear. Defaults to ["a male Mii", "a female Mii", "a non-binary Mii"].
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
    tomodachi_life_living_the_dream_trash: TomodachiLifeLTDTrash
    tomodachi_life_living_the_dream_miis: TomodachiLifeLTDMiis
    tomodachi_life_living_the_dream_creations: TomodachiLifeLTDCreations


@dataclass
class LTDItem:
    """
    An item from Tomodachi Life.

    Args:
        name (str): The name of the item.
        cost (float | int): The cost of the item.
    """

    name: str
    cost: float | int


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

    # TODO: Only 81/465 foods have been implemented, use item database to populate the rest

    @cached_property
    def food_mains(self) -> list[LTDItem]:
        return [
            LTDItem('Avocado', 1),
            LTDItem('Baked beans', 2.5),
            LTDItem('Beans on toast', 1.5),
            LTDItem('Boiled octopus', 3),
            LTDItem('Brussels sprouts', 1),
            LTDItem('Caprese salad', 8.7),
            LTDItem('Celery', 1.3),
            LTDItem('Cheese', 2),
            LTDItem('Cheeseburger', 3),
            LTDItem('Chilli bowl', 7.6),
            LTDItem('Cornflakes', 4),
            LTDItem('Curry with rice', 7),
            LTDItem('Filet mignon', 50),
            LTDItem('Fried chicken', 4.5),
            LTDItem('Fried egg', 3.8),
            LTDItem('Full English', 8),
            LTDItem('Gherkins', 2),
            LTDItem('Ginseng', 50),
            LTDItem('Grated carrot', 1.5),
            LTDItem('Hash browns', 1.5),
            LTDItem('Hot dog', 2.8),
            LTDItem('Kimchi fried rice', 6),
            LTDItem('Lasagne', 6.5),
            LTDItem('Lobster', 9.8),
            LTDItem('Macaroni and cheese', 5.8),
            LTDItem('Minestrone', 7),
            LTDItem('Monjayaki', 6.2),
            LTDItem('Natto', 1),
            LTDItem('Okonomiyaki', 7.8),
            LTDItem('Olives', 3),
            LTDItem('Onion rings', 5.4),
            LTDItem('Oyster', 6.8),
            LTDItem('Paella', 8.8),
            LTDItem('Pesto pasta', 7.3),
            LTDItem('Porcini mushrooms', 1.3),
            LTDItem('Pork bun', 1.2),
            LTDItem('Roasted lamb leg', 17),
            LTDItem('Rollmop herrings', 5.4),
            LTDItem('Sandwich', 3.3),
            LTDItem('Sausage', 2),
            LTDItem('Scrambled eggs', 1.5),
            LTDItem('Sea bream sashimi', 38),
            LTDItem('Spaghetti peperoncino', 7.8),
            LTDItem('Steak', 19.8),
            LTDItem('Sushi', 15.8),
            LTDItem('Tacos', 4.8),
            LTDItem('Tomato', 1.4),
            LTDItem('Xiaolongbao', 7.8),
        ]

    @cached_property
    def food_desserts(self) -> list[LTDItem]:
        return [
            LTDItem('Apple', 1.5),
            LTDItem('Apple crumble', 6.8),
            LTDItem('Beef jerky', 3),
            LTDItem('Black Forest gateau', 4.5),
            LTDItem('Boiled sweet', 0.5),
            LTDItem('Butter cookie', 1.8),
            LTDItem('Caramelised nuts', 5.7),
            LTDItem('Chocolate egg', 3.5),
            LTDItem('Chocolate sundae', 7.8),
            LTDItem('Cinnamon roll', 1.3),
            LTDItem('Coconut', 5.5),
            LTDItem('Colomba pasquale', 7.8),
            LTDItem('Cracker', 1.5),
            LTDItem('Frozen yoghurt', 1.8),
            LTDItem('Fudge', 4),
            LTDItem('Liquorice', 0.7),
            LTDItem('Macadamia nuts', 5),
            LTDItem('Mango', 9),
            LTDItem('Oatmeal cookie', 2.2),
            LTDItem('Pastel de nata', 2.8),
            LTDItem('Popcorn', 2.5),
            LTDItem('Raisin bread', 1.5),
            LTDItem('Soft ice cream', 2.5),
            LTDItem('Soufflé', 5),
            LTDItem('Tompouce', 5),
            LTDItem('Torrijas', 7),
            LTDItem('Watermelon slice', 2),
        ]

    @cached_property
    def food_drinks(self) -> list[LTDItem]:
        return [
            LTDItem('Bubble tea', 5.5),
            LTDItem('Green juice', 2),
            LTDItem('Orange juice', 2),
            LTDItem('Smoothie', 2.5),
            LTDItem('Tap water', 0.9),
            LTDItem('Yerba mate', 5.4),
        ]

    # TODO: Only 494/8365 clothes have been implemented, use item database to populate the rest

    @cached_property
    def clothing_sets(self) -> list[LTDItem]:
        return [
            LTDItem('Aerobics outfit', 38.9),
            LTDItem('Art explosion combo', 40),
            LTDItem('Baseball uniform', 60),
            LTDItem('Bow and blazer outfit', 37.4),
            LTDItem('Bow and shirt outfit', 34.4),
            LTDItem('Bunny costume', 56),
            LTDItem('Cardboard robot outfit', 12),
            LTDItem('Casual cardigan combo', 37.4),
            LTDItem('Casual jacket combo', 33.8),
            LTDItem('Cheerleader set', 41),
            LTDItem('Collarless coat combo', 44.2),
            LTDItem('Colourful plaid combo', 60.8),
            LTDItem('Colourful shirt combo', 40.4),
            LTDItem('Combat shorts combo', 31.5),
            LTDItem('Compression set', 44.2),
            LTDItem('Construction worker outfit', 48.2),
            LTDItem('Cosmic combo', 56.7),
            LTDItem('Cow costume', 45),
            LTDItem('Cyberpunk set', 46.6),
            LTDItem('Dotted shirt combo', 33.6),
            LTDItem('Duffle coat and skirt combo', 58.2),
            LTDItem('Fizzy drink costume', 31),
            LTDItem('Flower costume', 45),
            LTDItem('Frog costume', 52.6),
            LTDItem('Gingham combo', 33.7),
            LTDItem('Gym outfit', 48.5),
            LTDItem('Hamster costume', 51),
            LTDItem('Heart-heavy combo', 42.4),
            LTDItem("Hemp leaf men's yukata set", 45.8),
            LTDItem('Inspirational T-shirt combo', 32.2),
            LTDItem('Jockey uniform', 57.2),
            LTDItem('Kung fu outfit', 35),
            LTDItem('Lace polo neck combo', 62.9),
            LTDItem('Lemon enthusiast outfit', 29),
            LTDItem('Long-sleeved striped combo', 53),
            LTDItem('Long-sleeved tee & skirt set', 44.9),
            LTDItem('Loose T-shirt dress combo', 42.3),
            LTDItem('Lumberjack combo', 33.5),
            LTDItem('Marathon outfit', 34.7),
            LTDItem('Mii logo T-shirt combo', 33.7),
            LTDItem('Monkey costume', 46),
            LTDItem('Motorcycling combo', 65.5),
            LTDItem('Necktie and suit set', 42.5),
            LTDItem('Nerd outfit', 66.6),
            LTDItem('Paisley jacket combo', 34.6),
            LTDItem('Patchwork maxi skirt combo', 53.1),
            LTDItem('Pea jacket outfit', 56.7),
            LTDItem('Phantom thief outfit', 100),
            LTDItem('Photo print T-shirt combo', 26.5),
            LTDItem('Pilot uniform', 42.4),
            LTDItem('Plain collarless shirt combo', 34.8),
            LTDItem('Plain dress combo', 33.9),
            LTDItem('Plain dress set', 110.1),
            LTDItem('Plain dress shirt combo', 33.4),
            LTDItem('Plain jumper combo', 31.2),
            LTDItem('Plain skirt suit', 43.1),
            LTDItem('Plain T-shirt combo', 30.9),
            LTDItem('Polo-neck jumper combo', 37.8),
            LTDItem('Punky skirt combo', 44.5),
            LTDItem('Qipao set', 55.6),
            LTDItem('Shampoo bathrobe combo', 32.2),
            LTDItem('Sheep costume', 50),
            LTDItem('Short-sleeved cardie combo', 32.9),
            LTDItem('Sleeveless shirt outfit', 32.4),
            LTDItem('Sporty tracksuit set', 32),
            LTDItem('Star T-shirt combo', 32),
            LTDItem('Striped long-sleeved set', 41.9),
            LTDItem('Subdued kimono set', 59.5),
            LTDItem('Summer cardigan combo', 34),
            LTDItem('Sunny-side-up T-shirt combo', 32),
            LTDItem('Triangles T-shirt combo', 33.4),
            LTDItem('Two piece skirt suit', 117.6),
            LTDItem('Urban hiking combo', 49.1),
            LTDItem('Vintage flower dress combo', 58.5),
            LTDItem('Vintage plaid shirt combo', 33.2),
            LTDItem('Wedding dress set', 1162.1),
            LTDItem('Wedding suit set', 221.5),
        ]

    @cached_property
    def clothing_shirts(self) -> list[LTDItem]:
        return [
            LTDItem('Accent-striped polo shirt', 11),
            LTDItem('Anorak jacket', 13),
            LTDItem('Balmacaan coat', 18),
            LTDItem('Basic vest', 12),
            LTDItem('Big number T-shirt', 11.5),
            LTDItem('Blazer with bow', 15),
            LTDItem('Business vest with bow', 14),
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
            LTDItem('Inspirational T-shirt', 11),
            LTDItem('Jockey outfit', 17),
            LTDItem('Kung fu shirt', 15),
            LTDItem('Lace polo neck', 14.3),
            LTDItem('Leopard T-shirt', 16.5),
            LTDItem('Letterman cardigan', 12),
            LTDItem('Long-sleeved striped T-shirt', 13),
            LTDItem('Mackintosh raincoat', 11.5),
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
            LTDItem('Rectangular Mii logo T-shirt', 15),
            LTDItem('Rock band T-shirt', 13.4),
            LTDItem('Rugby jersey', 12),
            LTDItem('Running vest', 11.5),
            LTDItem('Safety vest', 14),
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
            LTDItem('Suit jacket', 20),
            LTDItem('Summer cardigan', 11),
            LTDItem('Sunny-side-up T-shirt', 12),
            LTDItem('Tailcoat', 150),
            LTDItem('Tailored jacket', 11.5),
            LTDItem('Tennis jumper', 11),
            LTDItem('Tiger baseball jacket', 12),
            LTDItem('Tracksuit top', 11),
            LTDItem('Triangles T-shirt', 11.8),
            LTDItem('Tweed jacket', 25),
            LTDItem('University jumper', 13),
            LTDItem('Vintage plaid shirt', 12),
            LTDItem('Waistcoat and T-shirt', 13),
            LTDItem('Wide-striped shirt', 12.5),
            LTDItem('Workwear jacket', 13),
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
            LTDItem('Cheerleading uniform', 29),
            LTDItem('Dreamy dress', 32.5),
            LTDItem('Dungaree dress', 25),
            LTDItem('Dungarees', 25.6),
            LTDItem('Flapper dress', 50),
            LTDItem('Flower dress', 27),
            LTDItem("Hemp leaf men's yukata", 37.8),
            LTDItem('Kandora', 39),
            LTDItem('Karate gi', 27.5),
            LTDItem('Katrina dress', 41),
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
            LTDItem('Chino shorts', 8.1),
            LTDItem('Chinos', 10),
            LTDItem('Combat shorts', 8.4),
            LTDItem('Combat trousers', 9.4),
            LTDItem('Corduroy trousers', 9),
            LTDItem('Cosmic shorts', 15),
            LTDItem('Cropped wide-leg trousers', 9.5),
            LTDItem('Cyberpunk trousers', 20),
            LTDItem('Denim maxi skirt', 10.2),
            LTDItem('Distressed jeans', 9.5),
            LTDItem('Dotted bubble shorts', 10),
            LTDItem('Fab jeans', 11),
            LTDItem('Frilled mini skirt', 11),
            LTDItem('Gym shorts', 11),
            LTDItem('Japanese monpe trousers', 8.5),
            LTDItem('Japanese pattern trousers', 15),
            LTDItem('Jeans', 9.2),
            LTDItem('Joggers', 8.2),
            LTDItem('Knitted skirt', 9.8),
            LTDItem('Lace pencil skirt', 14),
            LTDItem('Lemon pattern skirt', 12),
            LTDItem('Leopard pattern maxi skirt', 12),
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
            LTDItem('Bunny ears ribbon bow', 14),
            LTDItem('Cardboard box hat', 5),
            LTDItem('Cow hood', 20),
            LTDItem('Dog hood', 25),
            LTDItem('Drinking straw', 7),
            LTDItem('Floral kanzashi haripin', 32),
            LTDItem('Flower hair pin', 8.7),
            LTDItem('Flower headdress', 21.3),
            LTDItem('Flower hood', 20),
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
            LTDItem('Plaid beret', 20),
            LTDItem('Plain baseball cap', 10),
            LTDItem('Plain beanie', 10),
            LTDItem('Plate armour helmet', 420),
            LTDItem('Pop-out eye glasses', 12.3),
            LTDItem('Propeller cap', 11),
            LTDItem('Rabbit hood', 23),
            LTDItem('Shampoo bubbles hat', 12),
            LTDItem('Sheep hood', 25),
            LTDItem('Snap hair clip', 5.8),
            LTDItem('Snorkelling set', 18),
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
            LTDItem('Buttonhole flower', 49),
            LTDItem('Chain necklace', 16),
            LTDItem('Cow tail', 12),
            LTDItem('Fairy wings', 18),
            LTDItem('Happy flowers', 5),
            LTDItem('Headphones', 16),
            LTDItem('Lanyard with name badge', 14),
            LTDItem('Magic symbol', 21),
            LTDItem('Pearl brooch', 38),
            LTDItem('Pearl necklace', 50),
            LTDItem('Practical rucksack', 14),
            LTDItem('Ring necklace', 30),
            LTDItem('Rose corsage', 30),
            LTDItem('Rose petals', 17),
            LTDItem('Rosette', 15),
            LTDItem('Rosette pin', 50),
            LTDItem('Spiky choker', 12),
            LTDItem('Star necklace', 17),
            LTDItem('Studded rucksack', 21),
            LTDItem('Triple-chain necklace', 35),
            LTDItem('Turtle shell', 25),
            LTDItem('Whistle', 6),
            LTDItem('Wooden bead necklace', 18),
        ]

    @cached_property
    def clothing_socks(self) -> list[LTDItem]:
        return [
            LTDItem('Ankle socks', 4.8),
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
            LTDItem('Retro plaid socks', 5.3),
            LTDItem('Ruffled socks', 5.8),
            LTDItem('Sheer dotted socks', 5.1),
            LTDItem('Stockings', 5.1),
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
            LTDItem('Roman sandals', 5.9),
            LTDItem('Rubber slippers', 5.5),
            LTDItem('Rubber-toed high-tops', 7.8),
            LTDItem('Rubber-toed trainers', 7.1),
            LTDItem('Shoes with colourful socks', 6.5),
            LTDItem('Shoes with stripy socks', 8.5),
            LTDItem('Shower slippers', 5.3),
            LTDItem('Side stripe trainers', 7.2),
            LTDItem('Slip-ons', 6.9),
            LTDItem('Slippers', 5.2),
            LTDItem('Strappy pumps', 6.9),
            LTDItem('Studded dress shoes', 11),
            LTDItem('Track spikes', 6),
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
            LTDItem('Cardboard robot suit', 7),
            LTDItem('Car outfit', 40),
            LTDItem('Corn on the cob outfit', 26),
            LTDItem('Cow outfit', 25),
            LTDItem('Dustbin outfit', 18),
            LTDItem('Fizzy drink outfit', 24),
            LTDItem('Froggy outfit', 26.6),
            LTDItem('Hamster outfit', 25),
            LTDItem('Heavy metal outfit', 31.5),
            LTDItem('Monkey outfit', 26),
            LTDItem('Pig outfit', 28),
            LTDItem('Playing card outfit', 21),
            LTDItem('Police car outfit', 45),
            LTDItem('Sheep outfit', 25),
            LTDItem('Train outfit', 43),
        ]

    # TODO: Only 107/247 treasures have been implemented, use item database to populate the rest

    @cached_property
    def treasures_base(self) -> list[LTDItem]:
        return [
            LTDItem('9-volt battery', 3.4),
            LTDItem('Alpaca', 120),
            LTDItem('Balloon animal', 5),
            LTDItem('Bird feather', 5),
            LTDItem('Botanical field guide', 25),
            LTDItem('Bottle of perfume', 51),
            LTDItem('Bouquet', 40),
            LTDItem('Box of tissues', 1.2),
            LTDItem('Call bell', 5),
            LTDItem('Ceremonial mountain of buns', 33),
            LTDItem('Chess piece', 3),
            LTDItem('Chick', 15),
            LTDItem('Compass', 5.3),
            LTDItem('Crystal ball', 75.5),
            LTDItem('Cut-glass ornament', 50),
            LTDItem('Dating sim game', 53),
            LTDItem('Die', 1),
            LTDItem('Disco ball', 200),
            LTDItem('Embroidered decoration', 33),
            LTDItem('Flamingo', 150),
            LTDItem('Globe', 34),
            LTDItem('Gold ingot', 1000),
            LTDItem('Hand mirror', 17),
            LTDItem('Hedgehog', 20),
            LTDItem('Historical bust', 67),
            LTDItem('Horror film', 15),
            LTDItem('Horror game', 62),
            LTDItem('Hourglass', 3.2),
            LTDItem('Insect collection', 81),
            LTDItem('Jōmon-era pottery', 130),
            LTDItem('Kettle', 9),
            LTDItem('Koala cuddly toy', 36),
            LTDItem('Lightbulb', 5.5),
            LTDItem('Lion', 200),
            LTDItem('Loofah', 2),
            LTDItem('Love story', 8),
            LTDItem('Lump of amber', 200),
            LTDItem('Magnifying glass', 10),
            LTDItem('Moon-shaped lamp', 19),
            LTDItem('Mysterious solution', 1.5),
            LTDItem('Octopus', 20),
            LTDItem('Pair of binoculars', 34),
            LTDItem('Penguin', 150),
            LTDItem('Picture postcard set', 18),
            LTDItem('Piece of coral', 53),
            LTDItem('Pig', 120),
            LTDItem('Puzzle game', 38),
            LTDItem('Rabbit', 45),
            LTDItem('Racing game', 55),
            LTDItem('Reggae album', 25),
            LTDItem('Restaurant album', 12),
            LTDItem("Rock 'n' roll album", 25),
            LTDItem('Roll of toilet paper', 1),
            LTDItem('Romantic drama', 15),
            LTDItem('Rose', 10),
            LTDItem('Rubber duck', 4),
            LTDItem('Shark', 150),
            LTDItem('Ship in a bottle', 45),
            LTDItem('Solar panel', 150),
            LTDItem('Spinning top', 7),
            LTDItem('Stick', 0.3),
            LTDItem('Stopwatch', 16),
            LTDItem('Tap', 4),
            LTDItem('Tawashi scrub brush', 1),
            LTDItem('Treasure map', 99),
            LTDItem('UFO', 58),
            LTDItem('Unicorn', 300),
            LTDItem('Vacuum tube', 18),
            LTDItem('Variety show', 15),
            LTDItem('Water flea', 1),
            LTDItem('Weak-looking elastic cord', 1),
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

    # TODO: Only 46/272 interior sets have been implemented, use item database to populate the rest

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

    # TODO: Only 92/365 objects have been implemented, use item database to populate the rest

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
            bool: Whether the item is trash. This is always false if `tomodachi_life_living_the_dream_trash` is true.
        """
        return (
            not self.archipelago_options.tomodachi_life_living_the_dream_trash.value
            and item.name in ['Box of tissues', 'Roll of toilet paper']
        )

    ITEM_MAX_WEIGHT: int = 4

    def get_item_strings(self, items: list[LTDItem]) -> list[str]:
        """
        Converts a list of Tomodachi Life: Living the Dream items with names and costs into a list of strings. The strings are duplicated based on the costs of the items, to ensure that cheaper items are found more commonly in the list.

        Args:
            items (list[LTDItem]): The list of items to convert.

        Returns:
            list[str]: The weighted list of strings.
        """
        # Get all items for the given region, also get min and max costs
        min_cost: float = float("inf")
        max_cost: float = 0
        for item in items:
            if self.item_is_trash(item):
                continue
            min_cost = min(min_cost, item.cost)
            max_cost = max(max_cost, item.cost)
        # Duplicate items based on their costs, cheaper items appear more frequently
        cost_diff: float = max_cost - min_cost
        if cost_diff == 0:
            return [item.name for item in items if not self.item_is_trash(item)]
        weighted_items: list[str] = []
        for item in items:
            if self.item_is_trash(item):
                continue
            item_weight: int = (
                round(((max_cost - item.cost) / cost_diff) * (self.ITEM_MAX_WEIGHT - 1))
                + 1
            )
            for _ in range(item_weight):
                weighted_items.append(item.name)
        return weighted_items

    def miis(self) -> list[str]:
        return self.archipelago_options.tomodachi_life_living_the_dream_miis.value

    def foods(self) -> list[str]:
        foods: list[str] = self.get_item_strings(
            [*self.food_mains, *self.food_desserts, *self.food_drinks]
        )
        if (
            "food"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                foods.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "food"
                    ]
                )
        return foods

    def clothing(self) -> list[str]:
        clothing: list[str] = self.get_item_strings(
            [
                *self.clothing_sets,
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
        if (
            "interiors"
            in self.archipelago_options.tomodachi_life_living_the_dream_creations.value.keys()
        ):
            for _ in range(self.ITEM_MAX_WEIGHT):
                interiors.extend(
                    self.archipelago_options.tomodachi_life_living_the_dream_creations.value[
                        "interiors"
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
    def object_amounts() -> range:
        return range(1, 5 + 1)

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
            'Allow a Mii to style their own hair',
            "Answer a Mii's quick chat question",
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
            'Give a Mii $10 in pocket money',
            'Give a Mii $50 in pocket money',
            'Give a Mii $100 in pocket money',
            'Give a Mii $250 in pocket money',
            'Give a Mii clothing as a level-up gift',
            'Grant a wish from the Wishing Fountain',
            'Help a paralysed Mii using another Mii',
            'Help a paralysed Mii yourself',
            'Introduce a Mii to another Mii they are strangers to',
            'Let a Mii place an object themselves',
            "Listen to a Mii's random thought",
            "Look in a Mii's dream",
            'Observe a normal conversation in the Restaurant',
            'Observe a theatrical conversation in the Restaurant',
            'Observe a Mii performing an action based on a prezzie',
            'Observe a Mii spontaneously fall for another Mii',
            'Pet a Mii to dispel their anger',
            'Pet a Mii to dispel their sadness',
            'Play a game with a Mii',
            'Remove a Mii',
            'Save and trim a Nintendo Switch video recording of the game',
            'Save your progress',
            'Sell treasures at the Pawn Shop',
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
                label="Feed FOOD to any Mii",
                data={"FOOD": (self.foods, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_food"] * factor,
            ),
            GameObjectiveTemplate(
                label="Dress any Mii in CLOTHING",
                data={"CLOTHING": (self.clothing, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_clothing"] * factor,
            ),
            GameObjectiveTemplate(
                label="Give any Mii the TREASURE treasure",
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
                label="Renovate any Mii's home with the INTERIOR interior",
                data={"INTERIOR": (self.interiors, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["any_mii_named_interior"] * factor,
            ),
            GameObjectiveTemplate(
                label="Place AMOUNT new copies of OBJECT using the Island Builder",
                data={
                    "AMOUNT": (self.object_amounts, 1),
                    "OBJECT": (self.objects_non_buildings, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["place_objects"] * factor,
            ),
            GameObjectiveTemplate(
                label="Place new BUILDING using the Island Builder",
                data={"BUILDING": (self.objects_buildings, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["place_building"] * factor,
            ),
            GameObjectiveTemplate(
                label="Draw AMOUNT tiles of LANDSCAPE using the Island Builder",
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
                    label="Renovate any Mii's home with the EXTERIOR exterior",
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
                        label="Renovate the home of MII with any interior",
                        data={"MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_any_interior"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Feed FOOD to MII",
                        data={"FOOD": (self.foods, 1), "MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_named_food"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Dress MII in CLOTHING",
                        data={"CLOTHING": (self.clothing, 1), "MII": (self.miis, 1)},
                        is_time_consuming=False,
                        is_difficult=False,
                        weight=weights["named_mii_named_clothing"] * factor,
                    ),
                    GameObjectiveTemplate(
                        label="Give MII the TREASURE treasure",
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
                        label="Renovate the home of MII with the INTERIOR interior",
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
                            label="Renovate the home of MII with the EXTERIOR exterior",
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
