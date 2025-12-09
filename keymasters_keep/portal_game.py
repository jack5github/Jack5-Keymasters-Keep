"""
A Keymaster's Keep implementation of Portal, created by Jack5. The following objective types are included:

- Complete specific chambers / Reach specific locations / Defeat GLaDOS
- Detach cameras in specific chambers
- Find radio "dinosaur" noises in specific chambers (difficult)
- Place in challenges (difficult)
- Bonus objectives

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `portal_weights` YAML option.

For challenges, the weight of each challenge can be customised using the `portal_challenge_weights` YAML option.
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


class PortalWeights(OptionCounter):
    """
    The weights to use for Portal objective types. Note that "dinosaur_in_chamber", "complete_advanced_chamber", two-thirds of "challenges" and half of "bonus" are classified as difficult, and will not appear if difficult objectives are disabled.
    """

    display_name: str = "Portal Weights"
    default: dict[str, int] = {
        "complete_chamber": 5,
        "cameras_in_chamber": 5,
        "dinosaur_in_chamber": 5,
        "escape_sequence": 5,
        "glados": 1,
        "complete_chamber_advanced": 5,
        "challenges": 5,
        "bonus": 5,
    }


class PortalChallengeWeights(OptionCounter):
    """
    The weights to use for challenge types in Portal objectives.
    """

    display_name: str = "Portal Challenge Weights"
    default: dict[str, int] = {"Least Portals": 1, "Least Steps": 1, "Least Time": 1}


@dataclass
class PortalArchipelagoOptions:
    portal_weights: PortalWeights
    portal_challenge_weights: PortalChallengeWeights


class PortalGame(Game):
    """
    Portal is a single player game from Valve. Set in the mysterious Aperture Science Laboratories, Portal has been called one of the most innovative new games on the horizon and will offer gamers hours of unique gameplay.

    The game is designed to change the way players approach, manipulate, and surmise the possibilities in a given environment; similar to how Half-Life 2's Gravity Gun innovated new ways to leverage an object in any given situation. Players must solve physical puzzles and challenges by opening portals to maneuvering objects, and themselves, through space.
    """

    name: str = "Portal"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    platforms_other: list[KeymastersKeepGamePlatforms] = [
        KeymastersKeepGamePlatforms.PS3,  # Sony PlayStation 3
        KeymastersKeepGamePlatforms.SW,  # Nintendo Switch
        KeymastersKeepGamePlatforms.X360,  # Microsoft Xbox 360
    ]
    is_adult_only_or_unrated: bool = False
    options_cls: type[PortalArchipelagoOptions] = PortalArchipelagoOptions

    @cached_property
    def chapters_and_cameras(self) -> list[tuple[int, int]]:
        # Enumerating through this list will give the chamber numbers
        return [
            (1, 0),
            (1, 0),
            (1, 3),
            (1, 3),
            (2, 2),
            (2, 3),
            (2, 0),
            (2, 0),
            (3, 0),
            (3, 0),
            (4, 1),
            (4, 1),
            (4, 0),
            (5, 3),
            (6, 0),
            (7, 5),
            (8, 4),
            (9, 2),
            (10, 2),
            (11, 3),
        ]

    def chambers(self) -> list[str]:
        return [
            f"Test Chamber {index:02d}"
            for index in range(len(self.chapters_and_cameras))
        ]

    def complete_chamber_objectives(self) -> list[str]:
        return [
            f"Test Chamber {index:02d} starting from Chapter {chapter}"
            for index, (chapter, _) in enumerate(self.chapters_and_cameras)
        ]

    def detach_camera_objectives(self) -> list[str]:
        objectives: list[str] = []
        for index, (_, cameras) in enumerate(self.chapters_and_cameras):
            if cameras > 0:
                objectives.append(f"{cameras} cameras from Test Chamber {index:02d}")
        return objectives

    @staticmethod
    def escape_locations() -> list[str]:
        return [
            "fire pit",
            "giant fan",
            "Testchamber 09 observation room",
            "broken pipe to Testchamber 09",
            "bottom of Testchamber 09 elevator",
            "5 vertical pistons",
            "small, fast, horizontal pistons",
            "giant horizontal pistons",
            "pipe over goo",
            "Rattmann's den",
            "3 turrets behind doors",
            "friendly turret",
            "rocket turret",
            "glass pipe breakable by rocket",
            "giant room with turrets behind doors"
            "top of giant room with turrets behind doors",
            "long catwalk",
            "GLaDOS' chamber",
        ]

    @cached_property
    def advanced_and_challenge_chambers(self) -> range:
        return range(13, 18 + 1)

    def advanced_chambers(self) -> list[str]:
        return [
            f"Test Chamber {index:02d}: Advanced"
            for index in self.advanced_and_challenge_chambers
        ]

    def challenge_chambers(self) -> list[str]:
        return [
            f"Test Chamber {index:02d}"
            for index in self.advanced_and_challenge_chambers
        ]

    def challenges(self) -> list[str]:
        weighted_challenges: list[str] = []
        for (
            challenge
        ) in self.archipelago_options.portal_challenge_weights.default.keys():
            weight: int = self.archipelago_options.portal_challenge_weights.value[
                challenge
            ]
            if weight > 0:
                weighted_challenges.extend([challenge] * weight)
        return weighted_challenges

    @staticmethod
    def bonus_objectives_base() -> list[str]:
        return [
            "Create an infinite loop with portals",
            "Die by a High Energy Pellet",
            "Die by a turret",
            "Die by a rocket turret",
            "Die by descending into the fire pit",
            "Die by GLaDOS' neurotoxin",
            "Die by goo",
            "Explore Rattmann's den on Test Chamber 16",
            "Explore Rattmann's den on Test Chamber 17",
            "Explore Rattmann's den on Test Chamber 18",
            "Explore one of Rattmann's dens during the escape sequence",
            "Flush the toilet within the Relaxation Vault",
            "Incinerate the Companion Cube",
            "Incinerate yourself on Test Chamber 17",
            "Incinerate yourself within GLaDOS' Chamber",
            "Kill all turrets on Test Chamber 16",
            "Listen to the developer commentary for a chapter",
        ]

    @staticmethod
    def bonus_objectives_difficult() -> list[str]:
        return [
            "Become softlocked on Test Chamber 12",
            "Break the glass window with a prop during the escape sequence",
            "Complete Test Chamber 09 without using the portal gun",
            "Complete Test Chamber 13 without catching the High Energy Pellet",
            "Complete Test Chamber 16 without killing any turrets",
            "Fling to the exit elevator on Test Chamber 07",
            "Keep the two turrets lowered during the escape sequence alive",
            "Leave Test Chamber 00 with the exit door closed",
            "Perform the portal standing glitch",
            "Skip breaking the pipe during the escape sequence",
            "Skip past the Complimentary Victory Lift on Test Chamber 06",
            "Skip past the Complimentary Victory Lift on Test Chamber 14",
            "Skip past the Complimentary Victory Lift on Test Chamber 15",
            "Throw the cube onto the button from up high on Test Chamber 12",
            "Trap yourself in the High Energy Pellet catcher on Test Chamber 15",
            "Trap yourself in the High Energy Pellet catcher on Test Chamber 18",
        ]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "Avoid moving turrets where possible",
            "Avoid picking up cubes where possible",
            "Go as fast as possible",
            "Open as few blue portals as possible",
            "Open as few orange portals as possible",
            "Open as few portals as possible",
            "Take as few steps as possible",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.portal_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Complete CHAMBER",
                data={"CHAMBER": (self.complete_chamber_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["complete_chamber"] * factor,
            ),
            GameObjectiveTemplate(
                label="Detach CAMERAS",
                data={"CAMERAS": (self.detach_camera_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["cameras_in_chamber"] * factor,
            ),
            GameObjectiveTemplate(
                label="Find radio dinosaur noise on CHAMBER",
                data={"CHAMBER": (self.chambers, 1)},
                is_time_consuming=False,
                # While not time consuming, some of the radio dinosaur noises require bringing the radio to a very specific location, which would be difficult for normal players
                is_difficult=True,
                weight=weights["dinosaur_in_chamber"] * factor,
            ),
            GameObjectiveTemplate(
                label="Reach LOCATION during escape sequence",
                data={"LOCATION": (self.escape_locations, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["escape_sequence"] * factor,
            ),
            GameObjectiveTemplate(
                label="Defeat GLaDOS",
                data={},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["glados"] * factor,
            ),
            GameObjectiveTemplate(
                label="Complete ADVANCED",
                data={"ADVANCED": (self.advanced_chambers, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=weights["complete_chamber_advanced"] * factor,
            ),
            GameObjectiveTemplate(
                label="Get 3rd place in CHALLENGE on CHAMBER",
                data={
                    "CHALLENGE": (self.challenges, 1),
                    "CHAMBER": (self.challenge_chambers, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["challenges"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Get 2nd place in CHALLENGE on CHAMBER",
                data={
                    "CHALLENGE": (self.challenges, 1),
                    "CHAMBER": (self.challenge_chambers, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["challenges"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Get 1st place in CHALLENGE on CHAMBER",
                data={
                    "CHALLENGE": (self.challenges, 1),
                    "CHAMBER": (self.challenge_chambers, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["challenges"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["bonus"] * factor / 2,
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=weights["bonus"] * factor / 2,
            ),
        ]

    def optional_game_constraint_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="CONSTRAINT", data={"CONSTRAINT": (self.constraints, 1)}
            )
        ]
