"""
A Keymaster's Keep implementation of Garry's Mod, created by Jack5. The following objective types are included:

- Play on specific gamemodes/maps
- Kill players/NPCs with specific weapons/tools
- Spawn specific props/NPCs
- Pose NPCs on/with specific maps/props
- Bonus objectives

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `garrys_mod_weights` YAML option.

Objectives rely on user-defined lists of gamemodes, maps, weapons, tools, props and NPCs. The defaults for the related options come pre-filled with content bundled with the game and a few extras, but the options are meant to be customised as players explore the Steam Workshop.
"""

from __future__ import annotations
from dataclasses import dataclass
from Options import OptionCounter, OptionList  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class GarrysModWeights(OptionCounter):
    """
    The weights to use for Garry's Mod objective types. Defaults to objective type weights that work best with multiple gamemodes.

    If only playing Sandbox, it is recommended to start with the following weights:

    ```yaml
    gamemodes: 0
    maps: 4
    gamemode_in_map: 0
    weapons: 4
    player_models: 1
    props: 4
    tools: 4
    npcs: 1
    pose_npcs_in_map: 1
    pose_npc_with_props: 1
    kill_npc_with_weapon: 1
    bonus: 4
    ```

    If not playing Sandbox, start with the following instead:

    ```yaml
    gamemodes: 8
    maps: 8
    gamemode_in_map: 4
    weapons: 4
    player_models: 1
    props: 0
    tools: 0
    npcs: 0
    pose_npcs_in_map: 0
    pose_npc_with_props: 0
    kill_npc_with_weapon: 0
    bonus: 0
    ```
    """

    display_name: str = "Garry's Mod Weights"
    default: dict[str, int] = {
        "gamemodes": 8,
        "maps": 8,
        # Due to the unlikelihood of gamemodes supporting every map and weapon, the weight for "gamemode_in_map" and "weapons" are lower than normal
        "gamemode_in_map": 4,
        "weapons": 4,
        # Changing player models all the time is a bit much, so this weight is much lower than normal
        "player_models": 1,
        # All of the below weights specifically relate to Sandbox, so they should be lower than normal
        "props": 4,
        "tools": 4,
        "npcs": 1,
        "pose_npcs_in_map": 1,
        "pose_npc_with_props": 1,
        "kill_npc_with_weapon": 1,
        "bonus": 4,
    }


class GarrysModGamemodes(OptionList):
    """
    The list of gamemodes to use for Garry's Mod objectives that use them. Defaults to the two pre-installed gamemodes plus a few most-subscribed ones that can be played on any map, add and remove as needed.
    """

    display_name: str = "Garry's Mod Gamemodes"
    default: list[str] = [
        "Sandbox",
        "Trouble in Terrorist Town",
        "Prop Hunt",
        "Murder",
        "Guess Who",
        "Hide and Seek",
        "Cops and Runners",
        "You Touched it Last",
    ]


class GarrysModMaps(OptionList):
    """
    The list of maps to use for the Garry's Mod objectives that use them. Defaults to the two pre-installed maps plus a few most-subscribed "gm_" maps that offer various scenery, add and remove as needed.
    """

    display_name: str = "Garry's Mod Maps"
    default: list[str] = [
        "gm_construct",
        "gm_flatgrass",
        "gm_bigcity",
        "gm_fork",
        "gm_lair",
        "gm_mallparking",
        "gm_blackmesa_sigma",
        "gm_valley",
        "gm_atomic",
        "gm_bigisland",
    ]


class GarrysModPlayerModels(OptionList):
    """
    The list of player models to use for the Garry's Mod objectives that use them. Defaults to the pre-installed player models, add and remove as needed.
    """

    display_name: str = "Garry's Mod Player Models"
    default: list[str] = [
        "Alyx Vance",
        "Dr. Arne Magnusson",
        "Barney Calhoun",
        "Burnt Corpse",
        "Chell",
        "Citizen (Female)",
        "Citizen (Male)",
        "Combine Elite Soldier",
        "Combine Soldier",
        "Combine Soldier (Topless)",
        "Corpse",
        "Counter-Strike: Source Hostage",
        "Counter-Strike: Source Counter-Terrorist (Gas Mask)",
        "Counter-Strike: Source Counter-Terrorist (Riot)",
        "Counter-Strike: Source Counter-Terrorist (SWAT)",
        "Counter-Strike: Source Counter-Terrorist (Urban)",
        "Counter-Strike: Source Terrorist (Arctic)",
        "Counter-Strike: Source Terrorist (Guerilla)",
        "Counter-Strike: Source Terrorist (Phoenix)",
        "Counter-Strike: Source Terrorist (Sunglasses)",
        "Day of Defeat: Source Soldier (American)",
        "Day of Defeat: Source Soldier (German)",
        "Eli Vance",
        "Father Grigori",
        "G-Man",
        "Dr. Isaac Kleiner",
        "Dr. Judith Mossman",
        "Metro-Police",
        "Nova Prospekt Guard",
        "Odessa Cubbage",
        "Rebel (Female)",
        "Rebel (Male)",
        "Rebel Medic (Female)",
        "Rebel Medic (Male)",
        "Skeleton",
        "Wallace Breen",
        "Zombie (Classic)",
        "Zombie (Fast)",
        "Zombine",
    ]


class GarrysModProps(OptionList):
    """
    The list of prop types to use for the Garry's Mod objectives that use them. Defaults to some of the most recogniseable pre-installed prop types, add and remove as needed.
    """

    display_name: str = "Garry's Mod Props"
    default: list[str] = [
        "water barrel",
        "tall gas canister",
        "explosive barrel",
        "brown barrel",
        "propane canister",
        "bench",
        "concrete barrier",
        "metal fence",
        "prison cell door",
        "fountain",
        "bathtub",
        "bedframe",
        "mattress",
        "couch",
        "wooden cupboard",
        "wooden table",
        "wooden dresser",
        "toilet",
        "sink",
        "washing machine",
        "fridge",
        "stove",
        "teapot",
        "cooking pot",
        "radiator",
        "gravestone",
        "plastic crate",
        "metal ladder",
        "bridge",
        "globe",
        "corrugated metal sheet",
        "helicopter bomb",
        "pole",
        "leather chair",
        "wooden chair",
        "metal chair",
        "standing lamp",
        "lockers",
        "vending machine",
        "wooden crate",
        "cardboard box",
        "cinder block",
        "sawblade",
        "metal bucket",
        "fuel canister",
        "plastic bucket",
        "soda can",
        "push cart",
        "Ravenholm sign",
        "plastic trash bin",
        "traffic cone",
        "dumpster",
        "wooden pallet",
        "animal carrier",
        "sign",
        "clock",
        "metal trash bin",
        "tyre",
        "barricade",
        "buoy",
        "shipping container",
        "gas pump",
        "horizontal cooling tank",
        "shelves",
        "countertop",
        "wheel",
        "wooden fence",
        "skull",
        "Fast Zombie legs",
        "Fast Zombie torso",
        "cash register",
        "dentist chair",
        "stool",
        "baby doll",
        "cleaver",
        "playground carousel",
        "playground slide",
        "playground tic-tac-toe block",
        "horse statue",
        "numbered road sign",
        "picture road sign",
        "briefcase",
        "television",
        "Wallace Breen bust",
        "Combine interface",
        "bicycle",
        "garbage bag",
        "coffee mug",
        "glass bottle",
        "metal can",
        "milk bottle",
        "milk carton",
        "detergent bottle",
        "boot",
        "terracotta",
        "watermelon",
        "wheelbarrow",
        "binder",
        "chessboard",
        "radio",
        "clipboard",
        "desk lamp",
        "framed photo",
        "hula doll",
        "computer monitor",
        "keyboard",
        "payphone box",
        "car door",
        "balloon",
        "camera",
        "dynamite",
        "bomb",
        "portable lamp",
        "burger",
        "hot dog",
        "Garry's Mod logo",
        "headcrab",
        "road ramp",
        "traffic light",
        "torpedo",
        "Facepunch logo",
        "recursive monitor",
        "electric guitar",
        "soccer ball",
        "concrete pipe",
        "donut",
        "egg",
        "triangular metal sheet",
        "metal cylinder",
        "metal dome",
        "metal frame",
        "glass sheet",
        "glass cylinder",
        "glass dome",
        "wooden cylinder",
        "wooden dome",
        "wooden frame",
        "plastic sheet",
        "plastic blocks",
        "plastic ramp",
        "plastic cylinder",
        "plastic dome",
        "steel square beam",
        "steel I-beam",
        "gear",
        "gear teeth",
        "coaster train",
        "roller coaster part",
        "metal ball",
        "ball track part",
        "train tracks",
        "airplane",
        "commentary node",
        "giant letter",
        "ammo crate",
        "wooden boat",
        "train",
        "destroyed car",
        "generator",
        "rock",
    ]


class GarrysModWeapons(OptionList):
    """
    The list of weapons, specifically those that can harm players, NPCs and props, to use for the Garry's Mod objectives that use them. This list also includes entities that are functionally weapons when paired with the Gravity Gun. Defaults to the pre-installed weapons, add and remove as needed.
    """

    display_name: str = "Garry's Mod Weapons"
    default: list[str] = [
        ".357 Magnum",
        "Pulse-Rifle",
        "Crossbow",
        "Crowbar",
        "Frag Grenade",
        "Gravity Gun",
        "9mm Pistol",
        "RPG Launcher",
        "Shotgun",
        "S.L.A.M.",
        "SMG",
        "Stunstick",
        "Manhack Gun",
        "Fists",
        "Flechette Gun",
        "Medkit",
        "Combine Mine",
        "Resistance Mine",
        "Helicopter Bomb",
    ]


class GarrysModTools(OptionList):
    """
    The list of tools, which include weapons, vehicles, entities and anything else interesting, to use for the Garry's Mod objectives that use them. Defaults to the pre-installed tools, add and remove as needed.
    """

    display_name: str = "Garry's Mod Tools"
    default: list[str] = [
        "Bugbait",
        "Camera",
        "Tool Gun",
        "Physics Gun",
        "Fog Editor",
        "Sky Editor",
        "Sun Editor",
        "Bouncy Ball",
        "Chair",
        "Airboat",
        "Jalopy",
        "Jeep",
        "Prisoner Pod",
    ]


class GarrysModNPCs(OptionList):
    """
    The list of NPCs, only including those that can be killed, to use for the Garry's Mod objectives that use them. Defaults to the pre-installed NPCs, add and remove as needed.
    """

    display_name: str = "Garry's Mod NPCs"
    default: list[str] = [
        "Crow",
        "Father Grigori",
        "Pigeon",
        "Seagull",
        "Enemy Rebel",
        "Shield Scanner",
        "Combine Soldier",
        "Combine Elite Soldier",
        "Nova Prospekt Guard",
        "Prison Shotgun Guard",
        "Shotgun Soldier",
        "Combine Gunship",
        "City Scanner",
        "Hunter-Chopper",
        "Hunter",
        "Manhack",
        "Metro-Police",
        "Stalker",
        "Strider",
        "Combine Turret",
        "Alyx Vance",
        "Barney Calhoun",
        "Wallace Breen",
        "Citizen",
        "Rebel Medic",
        "Rebel",
        "Refugee",
        "Dog",
        "Eli Vance",
        "G-Man",
        "Dr. Isaac Kleiner",
        "Dr. Arne Magnusson",
        "Dr. Judith Mossman",
        "Odessa Cubbage",
        "Vortigaunt",
        "Vortigaunt Slave",
        "Uriah",
        "Antlion",
        "Antlion Grub",
        "Antlion Worker",
        "Antlion Guard",
        "Antlion Guardian",
        "Barnacle",
        "Fast Zombie",
        "Fast Zombie Torso",
        "Headcrab",
        "Poison Headcrab",
        "Fast Headcrab",
        "Poison Zombie",
        "Zombie",
        "Zombie Torso",
        "Zombine",
    ]


@dataclass
class GarrysModArchipelagoOptions:
    garrys_mod_weights: GarrysModWeights
    garrys_mod_gamemodes: GarrysModGamemodes
    garrys_mod_maps: GarrysModMaps
    garrys_mod_player_models: GarrysModPlayerModels
    garrys_mod_props: GarrysModProps
    garrys_mod_weapons: GarrysModWeapons
    garrys_mod_tools: GarrysModTools
    garrys_mod_npcs: GarrysModNPCs


class GarrysModGame(Game):
    """
    Garry's Mod is a physics sandbox, there aren't any predefined aims or goals. You spawn objects and weld them together to create your own contraptions; whether that's a car, a rocket, a catapult or something that doesn't have a name yet, that's up to you. You can do it offline, or join the thousands of players who play online each day.

    The Garry's Mod community is a tremendous source of content and has added hundreds of unique modes to the game. The game has one of the most vibrant Steam Community Workshops. It has everything from new tools to improve your builds, to guns that fire rainbow-tinged nuclear blasts from space.
    """

    name: str = "Garry's Mod"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    platforms_other: list[KeymastersKeepGamePlatforms] = [
        KeymastersKeepGamePlatforms.MOD  # Modded Game
    ]
    is_adult_only_or_unrated: bool = False
    options_cls: type[GarrysModArchipelagoOptions] = GarrysModArchipelagoOptions

    def gamemodes(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_gamemodes.value) > 0:
            return self.archipelago_options.garrys_mod_gamemodes.value
        return self.archipelago_options.garrys_mod_gamemodes.default

    @staticmethod
    def play_minutes() -> range:
        return range(5, 30 + 1, 5)

    def maps(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_maps.value) > 0:
            return self.archipelago_options.garrys_mod_maps.value
        return self.archipelago_options.garrys_mod_maps.default

    def player_models(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_player_models.value) > 0:
            return self.archipelago_options.garrys_mod_player_models.value
        return self.archipelago_options.garrys_mod_player_models.default

    def props(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_props.value) > 0:
            return self.archipelago_options.garrys_mod_props.value
        return self.archipelago_options.garrys_mod_props.default

    def weapons(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_weapons.value) > 0:
            return self.archipelago_options.garrys_mod_weapons.value
        return self.archipelago_options.garrys_mod_weapons.default

    @staticmethod
    def kills_number() -> range:
        return range(2, 5 + 1)

    def tools(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_tools.value) > 0:
            return self.archipelago_options.garrys_mod_tools.value
        return self.archipelago_options.garrys_mod_tools.default

    def npcs(self) -> list[str]:
        if len(self.archipelago_options.garrys_mod_npcs.value) > 0:
            return self.archipelago_options.garrys_mod_npcs.value
        return self.archipelago_options.garrys_mod_npcs.default

    @staticmethod
    def spawns_number() -> list[int]:
        return [i**2 for i in range(1, 5 + 1)]

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Add a trail to an entity",
            "Attach a rope between two entities",
            "Change the colour of an entity",
            "Change the game settings before starting one",
            "Change the physical properties of an entity",
            "Change the mounted games",
            "Change the NPC weapon override",
            "Change the visual material of an entity",
            "Change your spray image",
            "Check the Problems menu",
            "Click the Clean up everything button",
            "Commit suicide",
            "Create a dupe",
            "Create a save",
            "Customise your crosshair",
            "Disable collisions for an entity",
            "Duplicate an entity",
            "Enter noclip",
            "Host a peer-to-peer multiplayer game",
            "Inflate a model with the Tool Gun",
            "Join a multiplayer game from the Server List",
            "Like and favourite a Steam Workshop add-on",
            "Load a save",
            "Kill another player in a multiplayer game",
            "Kill yourself on accident",
            "Paint a surface",
            "Play with 3 other players",
            "Reach the spawn limit for a type of entity in a multiplayer game",
            "Remove an entity with the Tool Gun",
            "Spawn a balloon with the Tool Gun",
            "Spawn a button with the Tool Gun",
            "Spawn a camera with the Tool Gun",
            "Spawn a dupe",
            "Spawn a hoverball with the Tool Gun",
            "Spawn a lamp or light with the Tool Gun",
            "Spawn a thruster with the Tool Gun",
            "Spawn a wheel with the Tool Gun",
            "Spawn an emitter with the Tool Gun",
            "Spawn dynamite with the Tool Gun",
            "Subscribe to a Steam Workshop add-on",
            "Toggle NPC thinking",
            "Toggle NPCs ignoring players",
            "Toggle the Minecraftify option",
            "Unsubscribe from an unused Steam Workshop add-on",
            "Use a post processing effect",
            "Use the in-game text chat",
            "Use the in-game voice chat",
            "Use the Tool Gun Eye Poser",
            "Use the Tool Gun Face Poser",
            "Use the Tool Gun Finger Poser",
            "Weld two entities together",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.garrys_mod_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Play GAMEMODE for MINUTES minutes",
                data={
                    "GAMEMODE": (self.gamemodes, 1),
                    "MINUTES": (self.play_minutes, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["gamemodes"] * factor,
            ),
            GameObjectiveTemplate(
                label="Play on map MAP for MINUTES minutes",
                data={"MAP": (self.maps, 1), "MINUTES": (self.play_minutes, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["maps"] * factor,
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE on map MAP if possible",
                data={"GAMEMODE": (self.gamemodes, 1), "MAP": (self.maps, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["gamemode_in_map"] * factor,
            ),
            GameObjectiveTemplate(
                label="Use player model PLAYERMODEL",
                data={"PLAYERMODEL": (self.player_models, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["player_models"] * factor,
            ),
            GameObjectiveTemplate(
                label="Spawn PROP prop",
                data={"PROP": (self.props, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["props"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Spawn PROPS props",
                data={"PROP": (self.props, 2)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["props"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Spawn PROPS props",
                data={"PROP": (self.props, 3)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["props"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Kill AMOUNT players or NPCs with WEAPON",
                data={"AMOUNT": (self.kills_number, 1), "WEAPON": (self.weapons, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["weapons"] * factor,
            ),
            GameObjectiveTemplate(
                label="Use tool TOOL",
                data={"TOOL": (self.tools, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["tools"] * factor,
            ),
            GameObjectiveTemplate(
                label="Spawn AMOUNT CHARACTER NPC(s)",
                data={"AMOUNT": (self.spawns_number, 1), "CHARACTER": (self.npcs, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["npcs"] * factor,
            ),
            GameObjectiveTemplate(
                label="Pose CHARACTER in map MAP",
                data={"CHARACTER": (self.npcs, 1), "MAP": (self.maps, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["pose_npcs_in_map"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Pose CHARACTERS in map MAP",
                data={"CHARACTERS": (self.npcs, 2), "MAP": (self.maps, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["pose_npcs_in_map"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Pose CHARACTER with PROPS props",
                data={"CHARACTER": (self.npcs, 1), "PROPS": (self.props, 2)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["pose_npc_with_props"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Pose CHARACTER with PROPS props",
                data={"CHARACTER": (self.npcs, 1), "PROPS": (self.props, 3)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["pose_npc_with_props"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Pose CHARACTER with PROPS props",
                data={"CHARACTER": (self.npcs, 1), "PROPS": (self.props, 4)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["pose_npc_with_props"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Kill AMOUNT CHARACTER NPC(s) with WEAPON",
                data={
                    "AMOUNT": (self.spawns_number, 1),
                    "CHARACTER": (self.npcs, 1),
                    "WEAPON": (self.weapons, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["kill_npc_with_weapon"] * factor,
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
        return []  # Being so open-ended, Garry's Mod cannot have any constraints
