"""
A Keymaster's Keep implementation of R.E.P.O., created by Jack5 with help from Zeroman95. The following objective types are included:

- Kill specific monsters
- Survive specific locations
- Purchase specific items
- Salvage specific valuables
- Bonus objectives

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `repo_weights` YAML option.
"""

from __future__ import annotations
from dataclasses import dataclass
from Options import OptionCounter  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class RepoWeights(OptionCounter):
    """
    The weights to use for R.E.P.O. objective types.
    """

    display_name: str = "R.E.P.O. Weights"
    default: dict[str, int] = {
        "kill_monster": 3,
        "survive_location": 1,
        "purchase_item": 3,
        "salvage_valuable": 6,
        "bonus": 3,
    }


@dataclass
class RepoArchipelagoOptions:
    repo_weights: RepoWeights


class RepoGame(Game):
    """
    R.E.P.O. is an online co-op horror game featuring physics, proximity voice chat and scary monsters. You and up to 5 friends venture into terrifying environments to extract valuable objects using your physics-based grabbing tool.

    Even the monsters are affected by Newton's law of gravity, but know when to stay quiet. Use teamwork to make sure that the precious cargo will safely reach its destination. Robotic enhancements increase your chances.
    """

    name: str = "R.E.P.O."
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    is_adult_only_or_unrated: bool = False
    options_cls: type[RepoArchipelagoOptions] = RepoArchipelagoOptions

    @staticmethod
    def monsters_base() -> list[str]:
        """
        The list of base monsters in R.E.P.O., specifically those that have an orb size of Medium or lower and are not significantly dangerous. Monster comments by Zeroman95.

        Returns:
            list[str]: The list of base monsters.
        """
        return [
            "Apex Predator (Duck)",  # Super easy to kill with a weapon as long as you keep bashing at it.
            "Bella (Tricycle)",  # Killable, does fight back.
            "Birthday Boy",  # Easy to kill, as long as you do not pop its balloons.
            "Gnome",  # The easiest enemy to defeat in the game, simply grab it and throw it at a wall or on the ground to shatter it.
            "Shadow Child",  # Easy to kill, as long as you do not look at it; it can deal damage without touching you. Once it's fallen over, after a few moments it will spirit itself away.
            "Spewer",  # Spewers are easy to kill, just make sure it doesn't touch your face.
            "Tick",  # Ticks only have 10 hit points meaning if anything hits them it is basically instant death for them. HOWEVER, if it drained someone's hit points it can reach up to 100 hit points, meaning it will take a couple hits to defeat.
            "Animal (6 Legs)",  # Irritatingly annoying. This thing moves quick and if it bumps into you, it will knock you over. It is possible to kill, that is, if you can hit it first.
            "Banger (Skull)",  # Killable but not recommended. If a Banger is defeated the explosives will go off dealing moderate damage.
            "Chef (Frog)",  # This little guy can deal a lot of damage to valuables and even your face. Once it spots a target it will pull out cleavers to jump at you like a ninja to deal damage. Once hit with a weapon, it gets knocked over, giving you the opportunity to bash at it and kill it.
            "Headgrab (Goblin)",
            "Hidden",  # This is an invisible creature that will grab the nearest semibot and run with them. Indeed killable, has been done it many times with a frying pan. Watch your reticle in the middle of the screen. If it goes yellow that means something is there.
            "Mentalist (Alien)",  # This thing is a MONSTER to defeat, because once you try to get near it, it will activate zero gravity, then after a few moments, will bash everything into the ground dealing 50 or so damage. If you manage to BONK it on the head, you can knock it down for a moment... or just shoot it from afar.
            "Oogly (Spotlight)",
            "Rugrat (Baby)",  # If you are moving the C.A.R.T. around and you spot this thing, alert your teammates as soon as possible and run away with the C.A.R.T. if you can. Other then that, it is pretty easy to defeat. Just bonk it on the head to knock it down and get your teammates to throw it up and down into the ground to damage said Rugrat.
            "Upscream",  # This thing is terrifying if you don't notice it sneak up on you. If it gets near you it will launch you across the room, which will probably lead to death pits. If you can manage to hit it with a weapon it will become defenseless for a moment, allowing you to damage it even more.
        ]

    @staticmethod
    def monsters_difficult() -> list[str]:
        """
        The list of difficult monsters in R.E.P.O., specifically those that have an orb size of Large or are significantly dangerous. Monster comments by Zeroman95.

        Returns:
            list[str]: The list of difficult monsters.
        """
        return [
            # **Significantly Dangerous Monsters**
            "Elsa (Dog)",  # Has 600 hit points so it will take MANY MANY hits before it dies. Even then, once it is in monster form it kills quick.
            "Peeper (Eye)",  # Killable, but once it has its eye on you it is almost impossible to kill. It's better bring a gun to shoot it instead of trying to hit it with a melee weapon such as a frying pan.
            "Bowtie (Marshmallow)",  # Has 200 hit points. A bastard to knock down, and not only that, it will fan you away dealing damage.
            "Gambit (Roulette)",  # You can definitely kill it, has been done once. However, that is not recommended, considering the fact that once it LATCHES onto you, you are forced to do its minigame unless you get help from another teammate.
            "Heart Hugger (Flytrap)",  # THIS THING IS NOT FRIENDLY EVEN THOUGH IT SHOWS THAT IT IS. Whatever you do, DO NOT GO NEAR THIS THING. It will EAT YOU UP IN A MATTER OF SECONDS. It is killable, though again, NOT recommended.
            # **Large Monsters**
            "Cleanup Crew (Heads)",  # This guy is brutal if he spots you; he will keep throwing explosive heads at you to kill you. It is almost never recommended to kill this guy with a melee weapon, for as soon as he is defeated he will EXPLODE.
            "Clown (Laser)",  # Almost impossible to knock down with a melee weapon, so it is best to throw a grenade at him or shoot him from afar. Has a lot of health.
            "Headman",  # Almost impossible to knock over. Melee is almost never recommended for this thing at all. Has plenty of health. A single pistol shot won't kill it, but a grenade can.
            "Huntsman (Blind Man)",  # Huntsman can be pretty easy to defeat as long as you stay silent. If you don't stay quiet then it's bye bye, for that GUN he has does 100 damage, so without Health Upgrades he can instantly kill you. It's best to use a gun from afar, or if you can, sneak up behind him with a melee and hit him hard.
            "Loom (Black Dress)",  # Looms know where you and your teammates are at ALL times, so if you see her and have no form of weapon, good luck, you are going to need it. HOWEVER, if you have a form of weapon, fight her. Be careful using melee though, she can clap at you, dealing instant kill damage without Health Upgrades.
            "Reaper (Scarecrow)",  # Reaper (Scarecrow looking thing) - Reaper is difficult to defeat if you are not careful. As soon as you fight back, Reapers swipe quicker and faster, so kill quick or be the one that is being killed.
            "Robe",  # ROBES ARE THE MOST TERRIFYING THING IN THE GAME. If it gets its hands on you it's lights out. Robe's hand attack does 100 damage meaning that without Health Upgrades, this thing can easily kill you. You can knock it over with a melee weapon but not when it's looking at you. Other then that, use a gun or grenade.
            "Trudge (Flesh)",  # IF you plan on fighting this thing, it will do everything in its power to use its magnets to pull you towards it and smash you with a mace. However it is slow and you can wait patiently for it to go away before continuing. Best way to fight it? Use a gun or grenade. Melee is NOT recommended for this thing unless it is knocked down, which is almost impossible.
        ]

    @staticmethod
    def repo_locations() -> list[str]:
        return [
            "Swiftbroom Academy",
            "Headman Manor",
            "McJannek Station",
            "Museum of Human Art",
        ]

    @staticmethod
    def shop_items() -> list[str]:
        return [
            "Strength Upgrade",
            "Range Upgrade",
            "Stamina Upgrade",
            "Sprint Speed Upgrade",
            "Crouch Rest Upgrade",  # "Ooooh... CrOUch rest UPgrADE!?"
            "Health Upgrade",
            "Map Player Count Upgrade",
            "Tumble Launch Upgrade",
            "Tumble Wings Upgrade",
            "Extra Jump Upgrade",
            "Death Head Battery Upgrade",
            "Tumble Climb Upgrade",
            "Small Health Pack",
            "Medium Health Pack",
            "Large Health Pack",
            "Baseball Bat",
            "Frying Pan",
            "Sledge Hammer",
            "Sword",
            "Inflatable Hammer",
            "Prodzap",
            "Gun",
            "Shotgun",
            "Tranq Gun",
            "Pulse Pistol",
            "Photon Blaster",
            "Boltzap",
            "C.A.R.T. Cannon",
            "C.A.R.T. Laser",
            "Grenade",
            "Shockwave Grenade",
            "Stun Grenade",
            "Human Grenade",
            "Duct Taped Grenade",
            "Shockwave Mine",
            "Trapzap",
            "Explosive Mine",
            "Rubber Duck",
            "Recharge Drone",
            "Indestructible Drone",
            "Roll Drone",
            "Feather Drone",
            "Zero Gravity Drone",
            "Pocket C.A.R.T.",
            "C.A.R.T.",
            "Valuable Tracker",
            "Extraction Tracker",
            "Energy Crystal",
            "Zero Gravity Orb",
            "Duck Bucket",
            "Phase Bridge",
        ]

    @staticmethod
    def valuables_base() -> list[str]:
        """
        The list of base valuables in R.E.P.O., specifically those that have a size of Medium or lower and are not traps.

        Returns:
            list[str]: The list of base valuables.
        """
        return [
            "emerald bracelet",
            "goblet",
            "ocarina",
            "pocket watch",
            "uranium mug (small)",
            "coffee cup",
            "eraser",
            "keycard",
            "phone",
            "pills",
            "smartwatch",
            "stapler",
            "uranium petri dish",
            "USB stick",
            "banana bow",
            "cool brain",
            "fish",
            "golden tooth",
            "gold fish",
            "Ruben doll",
            "silverfish",
            "toast",
            "tooth",
            "bird skull",
            "bug",
            "diamond",
            "eyeball",
            "glowing jar",
            "small gem",
            "small potion",
            "enemy valuable (soul orb)",
            "surplus valuable (money bag)",
            "doll",
            "globe",
            "instrument (sextant)",
            "money",
            "small vase",
            "uranium plate",
            "bonsai tree",
            "calculator",
            "camera (modern)",
            "HDD",
            "VHS",
            "cocktail",
            "cube ball",
            "cubic tower",
            "duck man",
            "flesh blob (blue cap)",
            "lady bug (sculpture)",
            "pimple guy",
            "toy car",
            "toy plane",
            "wire figure",
            "crown",
            "fortune card",
            "gem box",
            "levitation potion",
            "love potion",
            "pendant (box with hole)",
            "red mushroom",
            "kettle",
            "magnifying glass",
            "map",
            "old camera",
            "ship in a bottle",
            "trophy",
            "vase",
            "3D printer",
            "computer (case)",
            "fire extinguisher",
            "flashlight",
            "laptop",
            "sample six pack (biohazard)",
            "sample (metal vial)",
            "scale (electronic)",
            "cubic sculpture (glass)",
            "gumball machine",
            "handface",
            "monkey box (toy)",
            "pacifier",
            "teeth bot",
            "crystal",
            "crystal ball",
            "Eye of Orpigox",
            "goblin head",
            "poison chalice",
            "power crystal",
            "star wand",
            "tentacle",
            "time glass",
        ]

    @staticmethod
    def valuables_difficult() -> list[str]:
        """
        The list of difficult valuables in R.E.P.O., specifically those that have a size of Big or higher or are traps.

        Returns:
            list[str]: The list of difficult valuables.
        """
        return [
            # **Trap Valuables**
            "chomp book",
            "frog (wind up)",
            "music box",
            "toy monkey",
            "propane tank",
            "bottle (with cork)",
            "clown doll",
            "fan",
            "gramophone",
            "radio",
            # **Big Valuables**
            "big vase (black)",
            "chunky vase (brown)",
            "diamond display",
            "telescope",
            "television",
            "barrel (explosive)",
            "big sample (cork vial)",
            "creature leg (in box)",
            "flamethrower",
            "guitar",
            "icepick",
            "ice saw",
            "sample cooler (medium biohazard)",
            "baby head",
            "egg (face)",
            "gem burger",
            "golden swirl (poop)",
            "museum boombox",
            "uranium mug deluxe (big)",
            "cauldron box (cardboard)",
            "Cube of Knowledge",
            "forever candle",
            "master potion (red)",
            "spider potion",
            "unicorn horn",
            "animal crate (this way up)",
            "dinosaur (statue)",
            "piano",
            "centrifuge",
            "ice block",
            "snow bike",
            "wide sample cooler (biohazard)",
            "horse (statue)",
            "tray (tea set)",
            "vinyl",
            "worm",
            "alchemy station",
            "dragon skull",
            "goblin arm",
            "griffin statue",
            "harp",
            "painting",
            "heavy water (deuterium oxide)",
            "jackhammer",
            "science station (biohazard computer)",
            "milk",
            "tall guy (statue)",
            "Dumgolf's staff",
            "wizard sword",
            "coffin",
            "golden statue",
            "grandfather clock",
            "cryo pod",
            "server rack",
            "blender",
            "traffic light",
            "troll finger",
            "wizard broom",
        ]

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Attract a monster away from fellow semibots",
            "Become King of the Losers",
            "Break a valuable",
            "Die to a monster",
            "Die to an extraction point",
            "Discover an extraction point",
            "Dive roll into another semibot",
            "Dunk another semibot in a Service Station toilet",
            "Fall to your death",
            "Finish a singleplayer game",
            "Force heal another semibot",
            "Heal yourself",
            "Hide from a monster",
            "Join a public game",
            "Kill another semibot in the Service Station",
            "Kill another semibot with the Baseball Bat",
            "Knock down another semibot with a weapon",
            "Knock down another semibot with a valuable",
            "Play the tutorial",
            "Play with 3 other semibots",
            "Ragequit",
            "Reach the attic in the Service Station",
            "Rescue a dead semibot using an extraction point",
            "Return to the vehicle to charge a weapon",
            "Run from a monster",
            "Sneak past a monster",
            "Survive until the Crescent Moon",
            "Take on C.A.R.T.-pushing duty",
            "Turn on Item Unequip Auto Hold gameplay setting",
            "Upgrade yourself",
        ]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "No charging weapons mid-location unless required",
            "No hiding unless required",
            "No running unless required",
            "No upgrades unless required",
            "No waiting for more cash if extraction is possible",
            "Objectives cannot be completed until after the Crescent Moon",
            "Ragequit if a valuable is broken",
            "Ragequit if you die",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.repo_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Kill MONSTER",
                data={"MONSTER": (self.monsters_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["kill_monster"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Kill MONSTER",
                data={"MONSTER": (self.monsters_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["kill_monster"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Survive LOCATION",
                data={"LOCATION": (self.repo_locations, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["survive_location"] * factor,
            ),
            GameObjectiveTemplate(
                label="Purchase ITEM",
                data={"ITEM": (self.shop_items, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["purchase_item"] * factor,
            ),
            GameObjectiveTemplate(
                label="Salvage VALUABLE",
                data={"VALUABLE": (self.valuables_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["salvage_valuable"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Salvage VALUABLE",
                data={"VALUABLE": (self.valuables_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["salvage_valuable"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["bonus"] * factor,
            ),
        ]

    def optional_game_constraint_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="CONSTRAINT", data={"CONSTRAINT": (self.constraints, 1)}
            )
        ]
