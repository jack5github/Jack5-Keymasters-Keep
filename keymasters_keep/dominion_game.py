from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from Options import OptionCounter  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class DominionWeights(OptionCounter):
    """
    The weights to use for Dominion objective types. Note that "win_with_card" and half of "win_against_ai" are classified as difficult, and will not appear if difficult objectives are disabled. Defaults to only objectives that can be completed in real life. If playing the 2021 version of Dominion by Temple Gates Games, it is recommended to use the following weights:

    ```yaml
    setup_with_cards: 1
    play_card: 8
    win_with_card: 1
    win_against_ai: 1
    bonus: 2
    ```
    """

    display_name: str = "Dominion Weights"
    default: dict[str, int] = {
        "setup_with_cards": 1,
        "play_card": 8,
        "win_with_card": 1,
        "win_against_ai": 0,
        "bonus": 0,
    }


class DominionExpansionWeights(OptionCounter):
    """
    The weights to use for expansions in Dominion objectives. Expansions are based on the 2021 version of Dominion by Temple Gates Games, where "...1st Edition" expansions only contain cards exclusive to them. Weights are proportional to the number of cards in their respective expansions. Defaults to only including the base game.
    """

    display_name: str = "Dominion Expansion Weights"
    default: dict[str, int] = {
        "Base": 1,
        "Base 1st Edition": 0,
        "Intrigue": 0,
        "Intrigue 1st Edition": 0,
        "Seaside": 0,
        "Seaside 1st Edition": 0,
        "Alchemy": 0,
        "Prosperity": 0,
        "Prosperity 1st Edition": 0,
        "Cornucopia": 0,
        "Cornucopia 1st Edition": 0,
        "Hinterlands": 0,
        "Hinterlands 1st Edition": 0,
        "Dark Ages": 0,
        "Guilds": 0,
        "Guilds 1st Edition": 0,
        "Adventures": 0,
        "Empires": 0,
        "Nocturne": 0,
        "Renaissance": 0,
        "Menagerie": 0,
        "Allies": 0,
        "Plunder": 0,
        "Rising Sun": 0,
        "Black Market": 0,
        "Promo Pack 1": 0,
        "Promo Pack 2": 0,
        "Marchland": 0,
    }


@dataclass
class DominionArchipelagoOptions:
    dominion_weights: DominionWeights
    dominion_expansion_weights: DominionExpansionWeights


class DominionGame(Game):
    name: str = "Dominion"
    platform: KeymastersKeepGamePlatforms = (
        KeymastersKeepGamePlatforms.BOARD  # Board Game (Physical)
    )
    platforms_other: list[KeymastersKeepGamePlatforms] = [
        KeymastersKeepGamePlatforms.AND,  # Android OS
        KeymastersKeepGamePlatforms.IOS,  # Apple iOS
        KeymastersKeepGamePlatforms.PC,
    ]
    is_adult_only_or_unrated: bool = False
    options_cls: type[DominionArchipelagoOptions] = DominionArchipelagoOptions

    @cached_property
    def kingdoms_base(self) -> list[str]:
        return [
            "Cellar",
            "Chapel",
            "Moat",
            "Harbinger",
            "Merchant",
            "Vassal",
            "Village",
            "Workshop",
            "Bureaucrat",
            "Gardens",
            "Militia",
            "Moneylender",
            "Poacher",
            "Remodel",
            "Smithy",
            "Throne Room",
            "Bandit",
            "Council Room",
            "Festival",
            "Laboratory",
            "Library",
            "Market",
            "Mine",
            "Sentry",
            "Witch",
            "Artisan",
        ]

    @cached_property
    def standard_base(self) -> list[str]:
        return ["Copper", "Silver", "Gold"]

    @cached_property
    def standard_base_not_playable(self) -> list[str]:
        return ["Estate", "Duchy", "Province", "Curse"]

    @cached_property
    def kingdoms_base_1st_ed(self) -> list[str]:
        return ["Chancellor", "Woodcutter", "Feast", "Spy", "Thief", "Adventurer"]

    @cached_property
    def kingdoms_intrigue(self) -> list[str]:
        return [
            "Courtyard",
            "Lurker",
            "Pawn",
            "Masquerade",
            "Shanty Town",
            "Steward",
            "Swindler",
            "Wishing Well",
            "Baron",
            "Bridge",
            "Conspirator",
            "Diplomat",
            "Ironworks",
            "Mill",
            "Mining Village",
            "Secret Passage",
            "Courtier",
            "Duke",
            "Minion",
            "Patrol",
            "Replace",
            "Torturer",
            "Trading Post",
            "Upgrade",
            "Farm",
            "Nobles",
        ]

    @cached_property
    def kingdoms_intrigue_1st_ed(self) -> list[str]:
        return [
            "Secret Chamber",
            "Great Hall",
            "Coppersmith",
            "Scout",
            "Saboteur",
            "Tribute",
        ]

    @cached_property
    def kingdoms_seaside(self) -> list[str]:
        return [
            "Haven",
            "Lighthouse",
            "Native Village",
            "Astrolabe",
            "Fishing Village",
            "Lookout",
            "Monkey",
            "Sailor",
            "Sea Chart",
            "Smugglers",
            "Warehouse",
            "Blockade",
            "Caravan",
            "Cutpurse",
            "Island",
            "Salvager",
            "Tide Pools",
            "Treasure Map",
            "Bazaar",
            "Corsair",
            "Merchant Ship",
            "Outpost",
            "Pirate",
            "Sea Witch",
            "Tactician",
            "Treasury",
            "Wharf",
        ]

    @cached_property
    def kingdoms_seaside_1st_ed(self) -> list[str]:
        return [
            "Embargo",
            "Pearl Diver",
            "Ambassador",
            "Navigator",
            "Pirate Ship",
            "Sea Hag",
            "Explorer",
            "Ghost Ship",
        ]

    @cached_property
    def kingdoms_alchemy(self) -> list[str]:
        return [
            "Transmute",
            "Vineyard",
            "Herbalist",
            "Apothecary",
            "Scrying Pool",
            "University",
            "Alchemist",
            "Familiar",
            "Philosopher's Stone",
            "Golem",
            "Apprentice",
            "Possession",
        ]

    @cached_property
    def standard_alchemy(self) -> list[str]:
        return ["Potion"]

    @cached_property
    def kingdoms_prosperity(self) -> list[str]:
        return [
            "Anvil",
            "Watchtower",
            "Bishop",
            "Clerk",
            "Investment",
            "Monument",
            "Quarry",
            "Tiara",
            "Worker's Village",
            "Charlatan",
            "City",
            "Collection",
            "Crystal Ball",
            "Magnate",
            "Mint",
            "Rabble",
            "Vault",
            "War Chest",
            "Grand Market",
            "Hoard",
            "Bank",
            "Expand",
            "Forge",
            "King's Court",
            "Peddler",
        ]

    @cached_property
    def standard_prosperity(self) -> list[str]:
        return ["Platinum"]

    @cached_property
    def standard_prosperity_not_playable(self) -> list[str]:
        return ["Colony"]

    @cached_property
    def kingdoms_prosperity_1st_ed(self) -> list[str]:
        return [
            "Loan",
            "Trade Route",
            "Talisman",
            "Counting House",
            "Royal Seal",
            "Contraband",
            "Mountebank",
            "Venture",
            "Goons",
        ]

    @cached_property
    def kingdoms_cornucopia(self) -> list[str]:
        return [
            "Hamlet",
            "Shop",
            "Menagerie",
            "Farmhands",
            "Remake",
            "Young Witch",
            "Carnival",
            "Ferryman",
            "Horn of Plenty",
            "Hunting Party",
            "Jester",
            "Joust",
            "Fairgrounds",
        ]  # Rewards are not included

    @cached_property
    def kingdoms_cornucopia_1st_ed(self) -> list[str]:
        return [
            "Fortune Teller",
            "Farming Village",
            "Horse Traders",
            "Tournament",
            "Harvest",
        ]  # Prizes are not included

    @cached_property
    def kingdoms_hinterlands(self) -> list[str]:
        return [
            "Crossroads",
            "Fool's Gold",
            "Develop",
            "Guard Dog",
            "Oasis",
            "Scheme",
            "Tunnel",
            "Jack of all Trades",
            "Nomads",
            "Spice Merchant",
            "Trader",
            "Trail",
            "Weaver",
            "Berserker",
            "Cartographer",
            "Cauldron",
            "Haggler",
            "Highway",
            "Inn",
            "Margrave",
            "Souk",
            "Stables",
            "Wheelwright",
            "Witch's Hut",
            "Border Village",
            "Farmland",
        ]

    @cached_property
    def kingdoms_hinterlands_1st_ed(self) -> list[str]:
        return [
            "Duchess",
            "Oracle",
            "Noble Brigand",
            "Nomad Camp",
            "Silk Road",
            "Cache",
            "Embassy",
            "Ill-Gotten Gains",
            "Mandarin",
        ]

    @cached_property
    def kingdoms_dark_ages(self) -> list[str]:
        return [
            "Poor House",
            "Beggar",
            "Squire",
            "Vagrant",
            "Forager",
            "Hermit",
            "Market Square",
            "Sage",
            "Storeroom",
            "Urchin",
            "Armory",
            "Death Cart",
            "Feodum",
            "Fortress",
            "Ironmonger",
            "Marauder",
            "Procession",
            "Rats",
            "Scavenger",
            "Wandering Minstrel",
            "Band of Misfits",
            "Bandit Camp",
            "Catacombs",
            "Count",
            "Counterfeit",
            "Cultist",
            "Craverobber",
            "Junk Dealer",
            "Knights",
            "Mystic",
            "Pillage",
            "Rebuild",
            "Rogue",
            "Altar",
            "Hunting Grounds",
        ]  # Knights, Ruins, Shelters and other cards are not included

    @cached_property
    def kingdoms_guilds(self) -> list[str]:
        return [
            "Candlestick Maker",
            "Farrier",
            "Stonemason",
            "Infirmary",
            "Advisor",
            "Plaza",
            "Herald",
            "Baker",
            "Butcher",
            "Footpad",
            "Journeyman",
            "Merchant Guild",
            "Soothsayer",
        ]

    @cached_property
    def kingdoms_guilds_1st_ed(self) -> list[str]:
        return ["Doctor", "Masterpiece", "Taxman"]

    @cached_property
    def kingdoms_adventures(self) -> list[str]:
        return [
            "Coin of the Realm",
            "Page",
            "Peasant",
            "Ratcatcher",
            "Raze",
            "Amulet",
            "Caravan Guard",
            "Dungeon",
            "Gear",
            "Guide",
            "Duplicate",
            "Magpie",
            "Messenger",
            "Miser",
            "Port",
            "Ranger",
            "Transmogrify",
            "Artificer",
            "Bridge Troll",
            "Distant Lands",
            "Giant",
            "Haunted Woods",
            "Lost City",
            "Relic",
            "Royal Carriage",
            "Storyteller",
            "Swamp Hag",
            "Treasure Trove",
            "Wine Merchant",
            "Hireling",
        ]  # Travellers are not included

    @cached_property
    def events_adventures(self) -> list[str]:
        return [
            "Alms",
            "Borrow",
            "Quest",
            "Save",
            "Scouting Party",
            "Travelling Fair",
            "Bonfire",
            "Expedition",
            "Ferry",
            "Plan",
            "Mission",
            "Pilgrimage",
            "Ball",
            "Raid",
            "Seaway",
            "Trade",
            "Lost Arts",
            "Training",
            "Inheritance",
            "Pathfinding",
        ]

    @cached_property
    def kingdoms_empires(self) -> list[str]:
        return [
            "Engineer",
            "City Quarter",
            "Overlord",
            "Royal Blacksmith",
            "Encampment",
            "Plunder",
            "Patrician",
            "Emporium",
            "Settlers",
            "Bustling Village",
            "Castles",
            "Catapult",
            "Rocks",
            "Chariot Race",
            "Enchantress",
            "Farmers' Market",
            "Gladiator",
            "Fortune",
            "Sacrifice",
            "Temple",
            "Villa",
            "Archive",
            "Capital",
            "Charm",
            "Crown",
            "Forum",
            "Groundskeeper",
            "Legionary",
            "Wild Hunt",
            "Castle-type card",  # Merged as all are on a single pile
        ]

    @cached_property
    def events_empires(self) -> list[str]:
        return [
            "Triumph",
            "Annex",
            "Donate",
            "Advance",
            "Delve",
            "Tax",
            "Banquet",
            "Ritual",
            "Salt the Earth",
            "Wedding",
            "Windfall",
            "Conquest",
            "Dominate",
        ]

    @cached_property
    def landmarks_empires(self) -> list[str]:
        return [
            "Aqueduct",
            "Arena",
            "Bandit Fort",
            "Basilica",
            "Baths",
            "Battlefield",
            "Colonnade",
            "Defiled Shrine",
            "Fountain",
            "Keep",
            "Labyrinth",
            "Mountain Pass",
            "Museum",
            "Obelisk",
            "Orchard",
            "Palace",
            "Tomb",
            "Tower",
            "Triumphal Arch",
            "Wall",
            "Wolf Den",
        ]

    @cached_property
    def kingdoms_nocturne(self) -> list[str]:
        return [
            "Druid",
            "Faithful Hound",
            "Guardian",
            "Monastery",
            "Pixie",
            "Tracker",
            "Changeling",
            "Fool",
            "Ghost Town",
            "Leprechaun",
            "Night Watchman",
            "Secret Cave",
            "Bard",
            "Blessed Village",
            "Cemetery",
            "Conclave",
            "Devil's Workshop",
            "Exorcist",
            "Necromancer",
            "Shepherd",
            "Skulk",
            "Cobbler",
            "Crypt",
            "Cursed Village",
            "Den of Sin",
            "Idol",
            "Pooka",
            "Sacred Grove",
            "Tormentor",
            "Tragic Hero",
            "Vampire",
            "Werewolf",
            "Raider",
        ]  # Heirlooms, Boons, Hexes, States and other cards are not included

    @cached_property
    def kingdoms_renaissance(self) -> list[str]:
        return [
            "Border Guard",
            "Ducat",
            "Lackeys",
            "Acting Troupe",
            "Cargo Ship",
            "Experiment",
            "Improve",
            "Flag Bearer",
            "Hideout",
            "Inventor",
            "Mountain Village",
            "Patron",
            "Priest",
            "Research",
            "Silk Merchant",
            "Old Witch",
            "Recruiter",
            "Scepter",
            "Scholar",
            "Sculptor",
            "Seer",
            "Spices",
            "Swashbuckler",
            "Treasurer",
            "Villain",
        ]  # Artifacts are not included

    @cached_property
    def projects_renaissance(self) -> list[str]:
        return [
            "Cathedral",
            "City Gate",
            "Pageant",
            "Sewers",
            "Star Chart",
            "Exploration",
            "Fair",
            "Silos",
            "Sinister Plot",
            "Academy",
            "Capitalism",
            "Fleet",
            "Guildhall",
            "Piazza",
            "Road Network",
            "Barracks",
            "Crop Rotation",
            "Innovation",
            "Canal",
            "Citadel",
        ]

    @cached_property
    def kingdoms_menagerie(self) -> list[str]:
        return [
            "Black Cat",
            "Sleigh",
            "Supplies",
            "Camel Train",
            "Goatherd",
            "Scrap",
            "Sheepdog",
            "Snowy Village",
            "Stockpile",
            "Bounty Hunter",
            "Cardinal",
            "Cavalry",
            "Groom",
            "Hostelry",
            "Village Green",
            "Barge",
            "Coven",
            "Displace",
            "Falconer",
            "Gatekeeper",
            "Hunting Lodge",
            "Kiln",
            "Livery",
            "Mastermind",
            "Paddock",
            "Sanctuary",
            "Fisherman",
            "Destrier",
            "Wayfarer",
            "Animal Fair",
        ]

    @cached_property
    def events_menagerie(self) -> list[str]:
        return [
            "Delay",
            "Desperation",
            "Gamble",
            "Pursue",
            "Ride",
            "Toil",
            "Enhance",
            "March",
            "Transport",
            "Banish",
            "Bargain",
            "Invest",
            "Seize the Day",
            "Commerce",
            "Demand",
            "Stampede",
            "Reap",
            "Enclave",
            "Alliance",
            "Populate",
        ]

    @cached_property
    def ways_menagerie(self) -> list[str]:
        animals: list[str] = [
            "Butterfly",
            "Camel",
            "Chameleon",
            "Frog",
            "Goat",
            "Horse",
            "Mole",
            "Monkey",
            "Mouse",
            "Mule",
            "Otter",
            "Owl",
            "Ox",
            "Pig",
            "Rat",
            "Seal",
            "Sheep",
            "Squirrel",
            "Turtle",
            "Worm",
        ]
        return [f"Way of the {animal}" for animal in animals]

    @cached_property
    def kingdoms_allies(self) -> list[str]:
        return [
            "Bauble",
            "Townsfolk-type card",  # Merged as all are on a single pile
            "Sycophant",
            "Augur-type card",  # Merged as all are on a single pile
            "Clash-type card",  # Merged as all are on a single pile
            "Fort-type card",  # Merged as all are on a single pile
            "Importer",
            "Merchant Camp",
            "Odyssey-type card",  # Merged as all are on a single pile
            "Sentinel",
            "Underling",
            "Wizard-type card",  # Merged as all are on a single pile
            "Broker",
            "Carpenter",
            "Courier",
            "Innkeeper",
            "Royal Galley",
            "Town",
            "Barbarian",
            "Capital City",
            "Contract",
            "Emissary",
            "Galleria",
            "Guildmaster",
            "Highwayman",
            "Hunter",
            "Modify",
            "Skirmisher",
            "Specialist",
            "Swap",
            "Marquis",
        ]

    @cached_property
    def allies_allies(self) -> list[str]:
        return [
            "Architect's Guild",
            "Band of Nomads",
            "Cave Dwellers",
            "City-State",
            "Coastal Haven",
            "Circle of Witches",
            "Crafter's Guild",
            "Desert Guides",
            "Family of Inventors",
            "Fellowship of Scribes",
            "Forest Dwellers",
            "Gang of Pickpockets",
            "Island Folk",
            "League of Bankers",
            "League of Shopkeepers",
            "Market Towns",
            "Mountain Folk",
            "Order of Astrologers",
            "Order of Masons",
            "Peaceful Cult",
            "Plateau Shepherds",
            "Trappers' Lodge",
            "Woodworkers' Guild",
        ]

    @cached_property
    def kingdoms_plunder(self) -> list[str]:
        return [
            "Cage",
            "Grotto",
            "Jewelled Egg",
            "Search",
            "Shaman",
            "Secluded Shrine",
            "Siren",
            "Stowaway",
            "Taskmaster",
            "Abundance",
            "Cabin Boy",
            "Crucible",
            "Flagship",
            "Fortune Hunter",
            "Gondola",
            "Harbor Village",
            "Landing Party",
            "Mapmaker",
            "Maroon",
            "Rope",
            "Swamp Shacks",
            "Tools",
            "Buried Treasure",
            "Crew",
            "Cutthroat",
            "Enlarge",
            "Figurine",
            "First Mate",
            "Frigate",
            "Longship",
            "Mining Road",
            "Pendant",
            "Pickaxe",
            "Pilgrim",
            "Quartermaster",
            "Silver Mine",
            "Trickster",
            "Wealthy Village",
            "Sack of Loot",
            "King's Cache",
        ]  # Loots are not included

    @cached_property
    def events_plunder(self) -> list[str]:
        return [
            "Bury",
            "Avoid",
            "Deliver",
            "Peril",
            "Rush",
            "Foray",
            "Launch",
            "Mirror",
            "Prepare",
            "Scrounge",
            "Journey",
            "Maelstrom",
            "Looting",
            "Invasion",
            "Prosper",
        ]

    @cached_property
    def kingdoms_rising_sun(self) -> list[str]:
        return [
            "Fishmonger",
            "Snake Witch",
            "Aristocrat",
            "Craftsman",
            "Riverboat",
            "Root Cellar",
            "Alley",
            "Change",
            "Ninja",
            "Poet",
            "River Shrine",
            "Rustic Village",
            "Gold Mine",
            "Kitsune",
            "Litter",
            "Rice Broker",
            "Tea House",
            "Ronin",
            "Tanuki",
            "Imperial Envoy",
            "Samurai",
            "Mountain Shrine",
            "Rice",
            "Daimyo",
            "Artist",
        ]

    @cached_property
    def prophecies_rising_sun(self) -> list[str]:
        return [
            "Approaching Army",
            "Biding Time",
            "Bureaucracy",
            "Divine Wind",
            "Enlightenment",
            "Flourishing Trade",
            "Good Harvest",
            "Great Leader",
            "Growth",
            "Harsh Winter",
            "Kind Emperor",
            "Panic",
            "Progress",
            "Rapid Expansion",
            "Sickness",
        ]

    @cached_property
    def events_rising_sun(self) -> list[str]:
        return [
            "Amass",
            "Asceticism",
            "Credit",
            "Foresight",
            "Kintsugi",
            "Practice",
            "Sea Trade",
            "Receive Tribute",
            "Gather",
            "Continue",
        ]

    @cached_property
    def kingdoms_black_market(self) -> list[str]:
        return ["Black Market"]

    @cached_property
    def kingdoms_promo_1(self) -> list[str]:
        return ["Envoy", "Governor", "Prince", "Stash", "Walled Village"]

    @cached_property
    def kingdoms_promo_2(self) -> list[str]:
        return ["Captain", "Church", "Dismantle", "Sauna", "Avanto"]

    @cached_property
    def events_promo_2(self) -> list[str]:
        return ["Summon"]

    @cached_property
    def kingdoms_marchland(self) -> list[str]:
        return ["Marchland"]

    def _all_cards(self, playable: bool = False) -> list[str]:
        weights: dict[str, int] = (
            self.archipelago_options.dominion_expansion_weights.value
        )
        all_cards: list[str] = []
        for key, cards_of_types in [
            (
                "Base",
                (
                    [self.kingdoms_base, self.standard_base]
                    if playable
                    else [
                        self.kingdoms_base,
                        self.standard_base,
                        self.standard_base_not_playable,
                    ]
                ),
            ),
            ("Base 1st Edition", [self.kingdoms_base_1st_ed]),
            ("Intrigue", [self.kingdoms_intrigue]),
            ("Intrigue 1st Edition", [self.kingdoms_intrigue_1st_ed]),
            ("Seaside", [self.kingdoms_seaside]),
            ("Seaside 1st Edition", [self.kingdoms_seaside_1st_ed]),
            ("Alchemy", [self.kingdoms_alchemy, self.standard_alchemy]),
            (
                "Prosperity",
                (
                    [self.kingdoms_prosperity, self.standard_prosperity]
                    if playable
                    else [
                        self.kingdoms_prosperity,
                        self.standard_prosperity,
                        self.standard_prosperity_not_playable,
                    ]
                ),
            ),
            ("Prosperity 1st Edition", [self.kingdoms_prosperity_1st_ed]),
            ("Cornucopia", [self.kingdoms_cornucopia]),
            ("Cornucopia 1st Edition", [self.kingdoms_cornucopia_1st_ed]),
            ("Hinterlands", [self.kingdoms_hinterlands]),
            ("Hinterlands 1st Edition", [self.kingdoms_hinterlands_1st_ed]),
            ("Dark Ages", [self.kingdoms_dark_ages]),
            ("Guilds", [self.kingdoms_guilds]),
            ("Guilds 1st Edition", [self.kingdoms_guilds_1st_ed]),
            ("Adventures", [self.kingdoms_adventures, self.events_adventures]),
            (
                "Empires",
                (
                    [self.kingdoms_empires, self.events_empires]
                    if playable
                    else [
                        self.kingdoms_empires,
                        self.events_empires,
                        self.landmarks_empires,
                    ]
                ),
            ),
            ("Nocturne", [self.kingdoms_nocturne]),
            ("Renaissance", [self.kingdoms_renaissance, self.projects_renaissance]),
            (
                "Menagerie",
                [self.kingdoms_menagerie, self.events_menagerie, self.ways_menagerie],
            ),
            ("Allies", [self.kingdoms_allies, self.allies_allies]),
            ("Plunder", [self.kingdoms_plunder, self.events_plunder]),
            (
                "Rising Sun",
                [
                    self.kingdoms_rising_sun,
                    self.prophecies_rising_sun,
                    self.events_rising_sun,
                ],
            ),
            ("Black Market", [self.kingdoms_black_market]),
            ("Promo Pack 1", [self.kingdoms_promo_1]),
            ("Promo Pack 2", [self.kingdoms_promo_2, self.events_promo_2]),
            ("Marchland", [self.kingdoms_marchland]),
        ]:
            for cards_of_type in cards_of_types:
                if key in weights.keys():
                    all_cards.extend(cards_of_type * weights[key])
        return all_cards

    def all_playable(self) -> list[str]:
        return self._all_cards(True)

    def all_setup(self) -> list[str]:
        return self._all_cards()

    @staticmethod
    def ai_number() -> range:
        return range(1, 3 + 1)

    @staticmethod
    def ai_difficulty_base() -> list[str]:
        return ["Very Easy", "Easy"]

    @staticmethod
    def ai_difficulty_difficult() -> list[str]:
        return ["Medium", "Hard"]

    @staticmethod
    def bonus_objectives_base() -> list[str]:
        return [
            "Ban a card in the Collection",
            "Earn an achievement by playing against an AI",
            "Earn an achievement by playing against another player",
            "Play a quick play online match",
            "Play a tutorial in the Learn section",
            "Play an async enrollment online match",
            "Play an online match via a lobby",
            "Play the daily challenge",
            "Read the rules in the Learn section",
            "Resign from a game with an AI",
            "Win the daily challenge",
        ]

    @staticmethod
    def bonus_objectives_campaigns() -> list[str]:
        return ["Play a campaign game", "Win a campaign game"]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "Do not collect victory tokens",
            "Do not play cards you don't own",
            "Do not trash cards",
            "Resign from games if you gain a Curse",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.dominion_weights.value
        factor: int = 100
        templates: list[GameObjectiveTemplate] = [
            GameObjectiveTemplate(
                label="Set up and play game with CARDS",
                data={"CARDS": (self.all_setup, 2)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["setup_with_cards"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Set up and play game with CARDS",
                data={"CARDS": (self.all_setup, 3)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["setup_with_cards"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Set up and play game with CARDS",
                data={"CARDS": (self.all_setup, 4)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["setup_with_cards"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play CARD",
                data={"CARD": (self.all_playable, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["play_card"] * factor),
            ),
            GameObjectiveTemplate(
                label="Win with CARD",
                data={"CARD": (self.all_playable, 1)},
                is_time_consuming=False,
                # Difficult due to the unlikelihood of a card appearing and being able to win with it
                is_difficult=True,
                weight=int(weights["win_with_card"] * factor),
            ),
            GameObjectiveTemplate(
                label="Win against NUMBER DIFFICULTY AI",
                data={
                    "NUMBER": (self.ai_number, 1),
                    "DIFFICULTY": (self.ai_difficulty_base, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["win_against_ai"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Win against NUMBER DIFFICULTY AI",
                data={
                    "NUMBER": (self.ai_number, 1),
                    "DIFFICULTY": (self.ai_difficulty_difficult, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["win_against_ai"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["bonus"] * factor * 0.8),
            ),
        ]
        if any(
            w > 0
            for e, w in self.archipelago_options.dominion_expansion_weights.value.items()
            if "Base" not in e
        ):
            templates.append(
                GameObjectiveTemplate(
                    label="BONUS",
                    data={"BONUS": (self.bonus_objectives_campaigns, 1)},
                    is_time_consuming=False,
                    is_difficult=False,
                    weight=int(weights["bonus"] * factor * 0.2),
                )
            )
        return templates

    def optional_game_constraint_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="CONSTRAINT", data={"CONSTRAINT": (self.constraints, 1)}
            )
        ]
