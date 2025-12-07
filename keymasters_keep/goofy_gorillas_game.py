"""
A Keymaster's Keep implementation of Goofy Gorillas, created by Jack5. The following objective types are included:

- Play gamemodes on specific maps
- Play gamemodes with specific settings
- Get kills with items
- Beat time trial records on specific maps

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `goofy_gorillas_weights` YAML option.
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from Options import OptionCounter  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class GoofyGorillasWeights(OptionCounter):
    """
    The weights to use for Goofy Gorillas objective types.
    """

    display_name: str = "Goofy Gorillas Weights"
    default: dict[str, int] = {
        "game_on_map": 2,
        "game_with_items": 1,
        "game_with_settings": 1,
        "kills_with_items": 2,
        "time_trials": 1,
        "bonus": 2,
    }


@dataclass
class GoofyGorillasArchipelagoOptions:
    goofy_gorillas_weights: GoofyGorillasWeights


class GoofyGorillasGame(Game):
    """
    Goofy Gorillas is the biggest nostalgia-driven virtual jungle gym. It has a number of action-packed gamemodes in a selection of different venues, all designed for varying types of gameplay. Games range from all-out brawls using only Dodgeballs, to sardines in complete darkness. The game also uses positional proximity voice chat.

    Taking part in the gamemodes will earn you Goofy Points, which will increase your level and unlock cosmetics. Additionally, while there's no on-going action, you can take part in some small activities such as the Time Trial events, Four in a Row and the Gravity arcade game.
    """

    name: str = "Goofy Gorillas"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    is_adult_only_or_unrated: bool = False
    options_cls: type[GoofyGorillasArchipelagoOptions] = GoofyGorillasArchipelagoOptions

    @cached_property
    def maps_base(self) -> list[str]:
        return ["Refurbished"]

    @cached_property
    def maps_original(self) -> list[str]:
        return ["Original"]

    @cached_property
    def maps_the_complex(self) -> list[str]:
        return ["The Complex"]

    def all_maps(self) -> list[str]:
        return self.maps_base + self.maps_original + self.maps_the_complex

    @cached_property
    def gamemodes_base(self) -> list[str]:
        return [
            # Deathmatch supports all maps with the following settings:
            # Round Duration (default 10:00)
            # Score Limit (default 25)
            # Player Max Health (default 100)
            # Respawn Time (default 3s)
            # Camera Mode (Both, First-Person or Third-Person, default Both)
            # Item Pickups (default On)
            # Health Pickups (default On)
            # Visible Nametags (default On)
            # Add Random Walls (default On)
            # Games Room Access (default Off)
            # Player Collision (default On)
            # Fall Damage (default On)
            "Deathmatch",
            # Team Deathmatch supports all maps with the following settings:
            # Score Limit (default 40)
            # All other settings are the same as Deathmatch
            "Team Deathmatch",
            # Tag, You're It! supports all maps with the following settings:
            # Starting Tag Score (default 3:20)
            # Player Max Health (default 10)
            # Respawn Time (default 4s)
            # Friendly Nametag Distance (default Quite Close)
            # Add Tag Timer Pickups (default On)
            # All settings Camera Mode and below excluding Visible Nametags are the same as Deathmatch
            "Tag, You're It!",
            # Tag: After Hours is the same as Tag, You're It! with flashlights
            "Tag: After Hours",
            # King of the Castle supports all maps with the following settings:
            # Castle Relocations (default 6)
            # Player Max Health (default 100)
            # Respawn Time (default 3s)
            # All settings Camera Mode and below are the same as Deathmatch
            "King of the Castle",
        ]

    @cached_property
    def gamemodes_not_the_complex(self) -> list[str]:
        return [
            # Infector does not support The Complex map, and uses the following settings:
            # Round Duration (default 5:00)
            # Max Rounds (default 4)
            # Player Max Health (default 100)
            # Friendly Nametag Distance (default Quite Close)
            # All settings Camera Mode and below excluding Visible Nametags are the same as Deathmatch
            "Infector",
            # Infector: After Hours is the same as Infector with flashlights
            "Infector: After Hours",
        ]

    @cached_property
    def gamemodes_no_pickups(self) -> list[str]:
        return [
            # Weapons Race supports all maps with the following settings:
            # Round Duration (default 10:00)
            # Eliminations to Advance (default 3)
            # Player Max Health (default 80)
            # All settings Respawn Time and below excluding Pickups are the same as Deathmatch
            "Weapons Race",
            # Juggernaut supports all maps with the following settings:
            # Round Duration (default 3:00)
            # Max Rounds (default 5)
            # Juggernaut Health (default 2250)
            # Player Max Health (default 75)
            # Respawn Time (default 2s)
            # All settings Camera Mode and below excluding Health Pickups and Visible Nametags are the same as Deathmatch
            "Juggernaut",
        ]

    @cached_property
    def gamemodes_no_items(self) -> list[str]:
        return [
            # Prop Hunt does not support the Original map nor editing Enabled Items, and uses the following settings:
            # Round Duration (default 5:00)
            # Pre-Round Duration (default 30s)
            # Max Rounds (default 4)
            # Automatic Sound Taunts (default On)
            # Camera Mode (Both, First-Person or Third-Person, default Both)
            # Games Room Access (default Off)
            # Fall Damage (default Off)
            "Prop Hunt"
        ]

    def all_gamemodes(self) -> list[str]:
        return (
            self.gamemodes_base
            + self.gamemodes_not_the_complex
            + self.gamemodes_no_pickups
            + self.gamemodes_no_items
        )

    def all_gamemodes_not_original(self) -> list[str]:
        return (
            self.gamemodes_base
            + self.gamemodes_not_the_complex
            + self.gamemodes_no_pickups
        )

    def all_gamemodes_pickups(self) -> list[str]:
        return self.gamemodes_base + self.gamemodes_not_the_complex

    def all_gamemodes_not_the_complex(self) -> list[str]:
        return self.gamemodes_base + self.gamemodes_no_pickups + self.gamemodes_no_items

    @staticmethod
    def time_trials() -> list[str]:
        return ["Time Trial", "Fruit Frenzy"]

    @staticmethod
    def random_players() -> range:
        return range(2, 5 + 1)

    @cached_property
    def enabled_items(self) -> list[str]:
        return [
            "Squeaky Hammer",
            "Boxing Glove",
            "Dodgeball",
            "Goofy Rifle",
            "Goofy Dualies",
            "Goofy Revolver",
            "Magic Staff",
        ]

    @cached_property
    def floor_items(self) -> list[str]:
        return ["Banana Peel", "Stink Bomb"]

    def all_items(self) -> list[str]:
        return self.enabled_items + self.floor_items

    @staticmethod
    def settings_casual() -> list[str]:
        return [
            "max health 100",
            "respawn time 2s",
            "3rd-person camera only",
            "item pickups on",
            "health pickups on",
            "random walls on",
            "games room access on",
            "player collision off",
            "fall damage off",
        ]

    @staticmethod
    def settings_comp() -> list[str]:
        return [
            "max health 10",
            "respawn time 6s",
            "1st-person camera only",
            "item pickups off",
            "health pickups off",
            "random walls off",
            "games room access off",
            "player collision on",
            "fall damage on",
        ]

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Beat your Gravity high score",
            "Edit your character",
            "Find the blackboards on Refurbished",
            "Find the Goofy Galactic Experience on Original",
            "Go down the highest slide on Refurbished",
            "Go down the giant spiral slide on Original",
            "Headshot a player",
            "Host and play a game on a multiplayer lobby",
            "Kill a prop in Prop Hunt",
            "Level up",
            "Manually taunt in Prop Hunt and have no-one notice",
            "Play bowling on Original",
            "Score a basketball hoop on Original",
            "Score a soccer goal on Original",
            "Score a soccer goal on Refurbished",
            "See yourself on a TV screen",
            "Slide into the ball pit on Original",
            "Slip in the Leaky Loo",
            "Survive as a prop in Prop Hunt",
            "Survive as the Juggernaut",
            "Win as a normal player in Juggernaut",
            "Win Connect 4",
        ]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "Always have 4 or more players in the lobby",
            "Do not hide",
            "No character customisations",
            "No crouching",
            "No running",
            "Stay in view of other players",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.goofy_gorillas_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Play GAMEMODE on MAP",
                data={
                    "GAMEMODE": (self.all_gamemodes, 1),
                    "MAP": (lambda: self.maps_base, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_on_map"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE on MAP",
                data={
                    "GAMEMODE": (self.all_gamemodes_not_original, 1),
                    "MAP": (lambda: self.maps_original, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_on_map"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE on MAP",
                data={
                    "GAMEMODE": (self.all_gamemodes_not_the_complex, 1),
                    "MAP": (lambda: self.maps_the_complex, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_on_map"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with enabled item ENABLED",
                data={
                    "GAMEMODE": (self.all_gamemodes_not_original, 1),
                    "ENABLED": (lambda: self.enabled_items, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_items"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with enabled items ENABLED",
                data={
                    "GAMEMODE": (self.all_gamemodes_not_original, 1),
                    "ENABLED": (lambda: self.enabled_items, 2),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_items"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with enabled items ENABLED",
                data={
                    "GAMEMODE": (self.all_gamemodes_not_original, 1),
                    "ENABLED": (lambda: self.enabled_items, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_items"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with SETTING",
                data={
                    "GAMEMODE": (self.all_gamemodes_pickups, 1),
                    "SETTING": (self.settings_casual, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_settings"] * factor / 4),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with SETTINGS",
                data={
                    "GAMEMODE": (self.all_gamemodes_pickups, 1),
                    "SETTINGS": (self.settings_casual, 2),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_settings"] * factor / 4),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with SETTING",
                data={
                    "GAMEMODE": (self.all_gamemodes_pickups, 1),
                    "SETTING": (self.settings_comp, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_settings"] * factor / 4),
            ),
            GameObjectiveTemplate(
                label="Play GAMEMODE with SETTINGS",
                data={
                    "GAMEMODE": (self.all_gamemodes_pickups, 1),
                    "SETTINGS": (self.settings_comp, 2),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["game_with_settings"] * factor / 4),
            ),
            GameObjectiveTemplate(
                label="Kill PLAYERS players with ITEM",
                data={"PLAYERS": (self.random_players, 1), "ITEM": (self.all_items, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["kills_with_items"] * factor,
            ),
            GameObjectiveTemplate(
                label="Beat your TRIAL record on MAP",
                data={"TRIAL": (self.time_trials, 1), "MAP": (self.all_maps, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["time_trials"] * factor,
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
            ),
            GameObjectiveTemplate(
                label="Do not die by ITEM", data={"ITEM": (self.all_items, 1)}
            ),
        ]
