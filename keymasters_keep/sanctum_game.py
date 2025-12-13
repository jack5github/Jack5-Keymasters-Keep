"""
A Keymaster's Keep implementation of Sanctum, created by Jack5 for Zeroman95. The following objective types are included:

- Clear difficulties on specific levels in Story/Survival mode
- Clear specific levels with specific gamemodes/weapons/towers
- Clear a number of waves in gamemodes on specific levels (difficult and time consuming)
- Bonus objectives

(Objectives with 20+ waves are considered time consuming, and objectives with 30 waves or Hard or Insane difficulties are considered difficult.)

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `sanctum_weights` YAML option.

Other YAML options are available for customising the occurrence of the available gamemodes and levels.
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from Options import OptionCounter, OptionList  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class SanctumWeights(OptionCounter):
    """
    The weights to use for Sanctum objective types.
    """

    display_name: str = "Sanctum Weights"
    default: dict[str, int] = {
        "story_difficulty_on_level": 3,
        "weapons_on_level": 2,
        "towers_on_level": 1,
        "gamemode_on_level": 1,
        "gamemode_on_level_waves": 3,
        "weapons_towers_on_level": 2,
        "gamemode_towers_on_level": 1,
        "kill_lumes": 4,
        "bonus": 4,
    }


class SanctumGamemodeWeights(OptionCounter):
    """
    The weights to use for gamemodes in Sanctum objectives that use them.
    """

    display_name: str = "Sanctum Gamemode Weights"
    default: dict[str, int] = {"Standard": 1, "Bounty": 1, "Pre-Built": 1, "Stamina": 1}


class SanctumOwnedDLCs(OptionList):
    """
    The list of DLCs that are owned by the player, which controls which levels are available in Sanctum objectives in addition to `sanctum_level_weights`. Defaults to no DLC. Supported DLCs are "Map Pack 1", "Map Pack 2", "X-Mas Carnage" and "Yogscave".
    """

    display_name: str = "Sanctum Owned DLCs"
    default: list[str] = []


class SanctumLevelWeights(OptionCounter):
    """
    The weights to use for levels in Sanctum objectives that use them. Levels that belong to DLCs that are not included in `sanctum_owned_dlcs` will not appear.
    """

    display_name: str = "Sanctum Level Weights"
    default: dict[str, int] = {
        "Mine": 1,
        "Bridge": 1,
        "Arc": 1,
        "Glade": 1,
        "Complex": 1,
        "Facility": 1,
        "Whirlpool": 1,
        "AfterMath": 1,
        "AfterShock": 1,
        "Cavern": 1,
        "Slums": 1,
        "Yogscave": 1,
        "Christmas": 1,
        "Corporation": 1,
        "Invasion": 1,
        "Chasm": 1,
    }


@dataclass
class SanctumArchipelagoOptions:
    sanctum_weights: SanctumWeights
    sanctum_gamemode_weights: SanctumGamemodeWeights
    sanctum_owned_dlcs: SanctumOwnedDLCs
    sanctum_level_weights: SanctumLevelWeights


class SanctumGame(Game):
    """
    Sanctum is a first-person shooter tower defense video game. In it, players take on the role of Skye, an elite soldier sent out to protect her home town, Elysion One, from hordes of mysterious alien creatures.

    To be successful in the task, the player will have to defend a "core" on each level. To accomplish this, the player builds defensive structures, and assists their structures by fending off the enemies themselves.
    """

    name: str = "Sanctum"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    is_adult_only_or_unrated: bool = False
    options_cls: type[SanctumArchipelagoOptions] = SanctumArchipelagoOptions

    def _get_weighted_items(self, items: list[str], option: OptionCounter) -> list[str]:
        """
        Duplicates items in a list for their weights in an option.

        Args:
            items (list[str]): The items to duplicate.
            option (OptionCounter): The option containing the weights.

        Returns:
            list[str]: The duplicated items.
        """
        weighted_items: list[str] = []
        for item in items:
            weight: int = option.value[item]
            if weight > 0:
                weighted_items.extend([item] * weight)
        return weighted_items

    @staticmethod
    def difficulties_base() -> list[str]:
        return ["Easy", "Medium"]

    @staticmethod
    def difficulties_difficult_story() -> list[str]:
        return ["Hard", "Insane"]

    @staticmethod
    def difficulties_difficult_survival() -> list[str]:
        return ["Hard"]

    def gamemodes(self) -> list[str]:
        return self._get_weighted_items(
            ["Standard", "Bounty", "Pre-Built", "Stamina"],
            self.archipelago_options.sanctum_gamemode_weights,
        )

    @cached_property
    def levels_base_any(self) -> list[str]:
        return ["Mine", "Bridge", "Arc", "Glade", "Facility", "Whirlpool"]

    @cached_property
    def levels_base_no_floors(self) -> list[str]:
        return ["Complex"]

    @cached_property
    def levels_map_pack_1_any(self) -> list[str]:
        return ["AfterMath", "AfterShock", "Cavern", "Slums"]

    @cached_property
    def levels_map_pack_1_no_anti_air(self) -> list[str]:
        return ["Cavern"]

    @cached_property
    def levels_map_pack_2_any(self) -> list[str]:
        return ["Corporation"]

    @cached_property
    def levels_map_pack_2_no_anti_air(self) -> list[str]:
        return ["Invasion", "Chasm"]

    @cached_property
    def levels_yogscast(self) -> list[str]:
        return ["Yogscave"]

    @cached_property
    def levels_xmas_carnage(self) -> list[str]:
        return ["Christmas"]

    def levels(self, anti_air: bool = True, floors: bool = True) -> list[str]:
        levels: list[str] = list(self.levels_base_any)
        if not anti_air and not floors:
            levels.extend(self.levels_base_no_floors)
        if "Map Pack 1" in self.archipelago_options.sanctum_owned_dlcs.value:
            levels.extend(self.levels_map_pack_1_any)
            if not anti_air:
                levels.extend(self.levels_map_pack_1_no_anti_air)
        if "Map Pack 2" in self.archipelago_options.sanctum_owned_dlcs.value:
            levels.extend(self.levels_map_pack_2_any)
            if not anti_air:
                levels.extend(self.levels_map_pack_2_no_anti_air)
        if "X-Mas Carnage" in self.archipelago_options.sanctum_owned_dlcs.value:
            levels.extend(self.levels_xmas_carnage)
        if "Yogscave" in self.archipelago_options.sanctum_owned_dlcs.value:
            levels.extend(self.levels_yogscast)
        return self._get_weighted_items(
            levels, self.archipelago_options.sanctum_level_weights
        )

    def levels_no_anti_air(self) -> list[str]:
        return self.levels(anti_air=False)

    def levels_no_floors(self) -> list[str]:
        return self.levels(anti_air=False, floors=False)

    @staticmethod
    def weapons() -> list[str]:
        return ["Assault", "Sniper", "Shotgun", "Freeze", "Rex", "Tesla"]

    @cached_property
    def towers_any_list(self) -> list[str]:
        return [
            "Holo",
            "Gatling",
            "Penetrator",
            "Lightning",
            "Mortar",
            "Scatter Laser",
            "Violator",
            "Kairos",
            "Accelerator",
            "Drone",
        ]

    @cached_property
    def towers_anti_air_list(self) -> list[str]:
        return ["Anti-Air"]

    @cached_property
    def towers_floors_list(self) -> list[str]:
        return ["Ampfield", "Killing Floor", "Slowfield"]

    def towers(self, anti_air: bool = True, floors: bool = True) -> list[str]:
        towers: list[str] = list(self.towers_any)
        if anti_air:
            towers.extend(self.towers_anti_air_list)
        if floors:
            towers.extend(self.towers_floors_list)
        return towers

    def towers_no_anti_air(self) -> list[str]:
        return self.towers(anti_air=False)

    def towers_no_floors(self) -> list[str]:
        return self.towers(anti_air=False, floors=False)

    @staticmethod
    def lumes_base() -> list[str]:
        # Dodger, Glider and Spore Pod do not appear on levels that do not use Anti-Air
        return [
            "Blocker",
            "Bobble Head",
            "Charger",
            "Dodger",
            "Glider",
            "Hoverer",
            "Runner",
            "Soaker",
            "Spitter",
            "Spore Pod",
            "Walker",
        ]

    @staticmethod
    def lumes_base_number() -> range:
        return range(10, 20 + 1)

    @staticmethod
    def lumes_big_walker_number() -> range:
        return range(3, 5 + 1)

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Beat a level using your guns on wave 1 only",
            "Beat a level without changing the paths of Lumes (enemies)",
            "Beat a level without deploying Block Towers",
            "Beat a level without using the Anti-Air Turrets",
            "Beat a level without teleporting",
            "Beat a wave without using your guns",
            "Complete the Tutorial",
            "Hold 1000 resources at once",
            "Fall off the edge of the map",
            "Lose the final wave of a level in singleplayer",
        ]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "Do not jump over towers",
            "Play with another player",
            "Use only 2 weapons per level",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.sanctum_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Beat Story mode at DIFFICULTY difficulty on LEVEL",
                data={
                    "DIFFICULTY": (self.difficulties_base, 1),
                    "LEVEL": (self.levels, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["story_difficulty_on_level"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Beat Story mode at DIFFICULTY difficulty on LEVEL",
                data={
                    "DIFFICULTY": (self.difficulties_difficult_story, 1),
                    "LEVEL": (self.levels, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["story_difficulty_on_level"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with weapons WEAPONS",
                data={"LEVEL": (self.levels, 1), "WEAPONS": (self.weapons, 3)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["weapons_on_level"] * factor,
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with towers TOWERS",
                data={"LEVEL": (self.levels, 1), "TOWERS": (self.towers, 3)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["weapons_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with towers TOWERS",
                data={
                    "LEVEL": (self.levels_no_anti_air, 1),
                    "TOWERS": (self.towers_no_anti_air, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["weapons_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with towers TOWERS",
                data={
                    "LEVEL": (self.levels_no_floors, 1),
                    "TOWERS": (self.towers_no_floors, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["weapons_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat GAMEMODE gamemode on LEVEL",
                data={"GAMEMODE": (self.gamemodes, 1), "LEVEL": (self.levels, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["gamemode_on_level"] * factor,
            ),
            GameObjectiveTemplate(
                label="Beat 10 waves of GAMEMODE gamemode on LEVEL",
                data={"GAMEMODE": (self.gamemodes, 1), "LEVEL": (self.levels, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["gamemode_on_level_waves"] * factor * (1 / 3)),
            ),
            GameObjectiveTemplate(
                label="Beat 20 waves of GAMEMODE gamemode on LEVEL",
                data={"GAMEMODE": (self.gamemodes, 1), "LEVEL": (self.levels, 1)},
                is_time_consuming=True,
                is_difficult=False,
                weight=int(weights["gamemode_on_level_waves"] * factor * (1 / 3)),
            ),
            GameObjectiveTemplate(
                label="Beat 30 waves of GAMEMODE gamemode on LEVEL",
                data={"GAMEMODE": (self.gamemodes, 1), "LEVEL": (self.levels, 1)},
                is_time_consuming=True,
                is_difficult=True,
                weight=int(weights["gamemode_on_level_waves"] * factor * (1 / 3)),
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with weapons WEAPONS & towers TOWERS",
                data={
                    "LEVEL": (self.levels, 1),
                    "WEAPONS": (self.weapons, 3),
                    "TOWERS": (self.towers, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["weapons_towers_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with weapons WEAPONS & towers TOWERS",
                data={
                    "LEVEL": (self.levels_no_anti_air, 1),
                    "WEAPONS": (self.weapons, 3),
                    "TOWERS": (self.towers_no_anti_air, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["weapons_towers_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat LEVEL with weapons WEAPONS & towers TOWERS",
                data={
                    "LEVEL": (self.levels_no_floors, 1),
                    "WEAPONS": (self.weapons, 3),
                    "TOWERS": (self.towers_no_floors, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["weapons_towers_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat GAMEMODE gamemode on LEVEL with towers TOWERS",
                data={
                    "GAMEMODE": (self.gamemodes, 1),
                    "LEVEL": (self.levels, 1),
                    "TOWERS": (self.towers, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["gamemode_towers_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat GAMEMODE gamemode on LEVEL with towers TOWERS",
                data={
                    "GAMEMODE": (self.gamemodes, 1),
                    "LEVEL": (self.levels_no_anti_air, 1),
                    "TOWERS": (self.towers_no_anti_air, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["gamemode_towers_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Beat GAMEMODE gamemode on LEVEL with towers TOWERS",
                data={
                    "GAMEMODE": (self.gamemodes, 1),
                    "LEVEL": (self.levels_no_floors, 1),
                    "TOWERS": (self.towers_no_floors, 3),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["gamemode_towers_on_level"] * factor / 3),
            ),
            GameObjectiveTemplate(
                label="Kill NUMBER LUMEs",
                data={
                    "NUMBER": (self.lumes_base_number, 1),
                    "LUME": (self.lumes_base, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["kill_lumes"] * factor * (11 / 12)),
            ),
            GameObjectiveTemplate(
                label="Kill NUMBER Big Walkers",
                data={"NUMBER": (self.lumes_big_walker_number, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["kill_lumes"] * factor * (1 / 12)),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["gamemode_towers_on_level"] * factor,
            ),
        ]

    def optional_game_constraint_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="CONSTRAINT", data={"CONSTRAINT": (self.constraints, 1)}
            )
        ]
