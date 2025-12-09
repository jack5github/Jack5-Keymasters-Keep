"""
A Keymaster's Keep implementation of Trivia Tricks, created by Jack5. The following objective types are included:

- Play/win specific gamemodes with a certain number of players/CPUs (difficult)
- Play with/on specific settings/stages (time consuming)
- Answer questions from specific categories correctly
- Play/win against co-op bosses (difficult)
- Bonus objectives

(Objectives where the player has to win are considered difficult, and objectives for long games are considered time consuming.)

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `trivia_tricks_weights` YAML option.

Other YAML options are available for customising the occurrence of the available gamemodes and categories, the latter supporting adding Steam Workshop categories.
"""

from __future__ import annotations
from dataclasses import dataclass
from Options import OptionCounter, OptionList  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class TriviaTricksWeights(OptionCounter):
    """
    The weights to use for Trivia Tricks objective types. "twitch" is disabled by default. Note that "players_on_gamemode_win" and "coop_bosses_win" are classified as difficult, and will not appear if difficult objectives are disabled.
    """

    display_name: str = "Trivia Tricks Weights"
    default: dict[str, int] = {
        "players_on_gamemode": 2,
        "players_on_gamemode_win": 2,
        "settings": 4,
        "stages": 4,
        "answer_categories": 8,
        "coop_bosses": 1,
        "coop_bosses_win": 1,
        "twitch": 0,
        "bonus": 4,
    }


class TriviaTricksGamemodeWeights(OptionCounter):
    """
    The weights to use for gamemodes in Trivia Tricks objectives that use them.
    """

    display_name: str = "Trivia Tricks Gamemode Weights"
    default: dict[str, int] = {
        "Standard Trivia": 3,
        "Co-Op Vs Boss": 1,
        "Team Trivia": 2,
    }


class TriviaTricksCategories(OptionList):
    """
    The categories to use in Trivia Tricks objectives that use them. "Steam Workshop" is included by default, but can be replaced with the names of the Steam Workshop categories one is subscribed to, or removed entirely.
    """

    display_name: str = "Trivia Tricks Categories"
    default: list[str] = [
        "Animals",
        "Anime",
        "Art & Literature",
        "Film & TV",
        "Food & Drink",
        "Geography",
        "History",
        "Language",
        "Math",
        "Music",
        "Science & Technology",
        "Sports",
        "Video Games",
        "Steam Workshop",
    ]


@dataclass
class TriviaTricksArchipelagoOptions:
    trivia_tricks_weights: TriviaTricksWeights
    trivia_tricks_gamemode_weights: TriviaTricksGamemodeWeights
    trivia_tricks_categories: TriviaTricksCategories


class TriviaTricksGame(Game):
    """
    Trivia Tricks is an online multiplayer trivia game that supports online play of up to 8 players, or connecting controllers and smartphones to play locally with up to four friends.

    Additionally, play either competitively or co-operatively against trivia bosses, choose optional bonuses and risk points in high-stakes Chance Rounds. There are over 4500 questions across 13 categories from trivia classics (Music, Geography, Film & TV) to more niche subjects (Video Games, Anime).
    """

    name: str = "Trivia Tricks"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    is_adult_only_or_unrated: bool = False
    options_cls: type[TriviaTricksArchipelagoOptions] = TriviaTricksArchipelagoOptions

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

    def gamemodes(self) -> list[str]:
        return self._get_weighted_items(
            ["Standard Trivia", "Co-Op Vs Boss", "Team Trivia"],
            self.archipelago_options.trivia_tricks_gamemode_weights,
        )

    # Game lengths cannot be applied to Co-Op Vs Boss games
    @staticmethod
    def game_lengths_base() -> list[str]:
        return ["short (10 mins)", "medium (15 mins)"]

    @staticmethod
    def game_lengths_time_consuming() -> list[str]:
        return ["long (20 mins)"]

    # Settings cannot be applied to Co-Op Vs Boss games
    @staticmethod
    def settings_casual() -> list[str]:
        return [
            "answering time 35s",
            "visible answers on",
            "change answers on",
            "streak bonus off",
            "speed bonus off",
        ]

    @staticmethod
    def settings_comp() -> list[str]:
        return [
            "answering time 15s",
            "visible answers off",
            "change answers off",
            "streak bonus on",
            "speed bonus on",
        ]

    # Chance Rounds cannot be applied to Co-Op Vs Boss games
    @staticmethod
    def chance_rounds() -> list[str]:
        return ["no", "Normal", "No Items", "Chaotic"]

    # Categories cannot always be applied to Co-Op Vs Boss games

    @staticmethod
    def questions_number() -> range:
        return range(1, 3 + 1)

    @staticmethod
    def stages() -> list[str]:
        return ["Classic", "Island", "Halloween", "Christmas", "Space"]

    @staticmethod
    def bosses() -> list[str]:
        return [
            "King",
            "Nigel",
            "Robin",
            "Ganymede",
            "Negative",
            "Dash",
            "Sakura",
            "Summer",
        ]

    @staticmethod
    def players_number_base() -> range:
        return range(1, 7 + 1)

    @staticmethod
    def players_number_teams() -> range:
        return range(1, 7 + 1, 2)

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Attend Saturday Night Trivia",
            "Be positively affected by another player's Chance Round item",
            "Be negatively affected by another player's Chance Round item",
            "Buy a cosmetic from the Character Creator if one can be bought",
            "Change your answer at the last second and end up with the correct answer",
            "Change your answer at the last second and end up with the wrong answer",
            "Copy the answer choice of another player and end up with the correct answer",
            "Copy the answer choice of another player and end up with the wrong answer",
            "Create and save a new personally customised character",
            "Create and save a randomly generated character",
            "Get a speed bonus 2 times in a row",
            "Get a streak bonus 2 times in a row",
            "Fall from the top of the leaderboard to the bottom",
            "Like and favourite a Steam Workshop category",
            "Play a local game with at least 1 other player",
            "Subscribe to a new category from the Steam Workshop",
            "Turn the character around in the Character Creator",
            "Use a Chance Round item",
        ]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "Don't answer once each round",
            "Don't use Chance Round items",
            "Play as the default character",
            "Never answer with option 1",
            "Never answer with option 2",
            "Never answer with option 3",
            "Never answer with option 4",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.trivia_tricks_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Play a GAMEMODE game with PLAYERS or more other players or CPUs",
                data={
                    "GAMEMODE": (self.gamemodes, 1),
                    "PLAYERS": (self.players_number_base, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["players_on_gamemode"] * factor,
            ),
            GameObjectiveTemplate(
                label="Win a GAMEMODE game with PLAYERS or more other players or CPUs",
                data={
                    "GAMEMODE": (self.gamemodes, 1),
                    "PLAYERS": (self.players_number_base, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=weights["players_on_gamemode_win"] * factor,
            ),
            GameObjectiveTemplate(
                label="Play a LENGTH game with SETTINGS & CHANCE Chance Round",
                data={
                    "LENGTH": (self.game_lengths_base, 1),
                    "SETTINGS": (self.settings_casual, 3),
                    "CHANCE": (self.chance_rounds, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["settings"] * factor * (2 / 6)),
            ),
            GameObjectiveTemplate(
                label="Play a LENGTH game with SETTINGS & CHANCE Chance Round",
                data={
                    "LENGTH": (self.game_lengths_time_consuming, 1),
                    "SETTINGS": (self.settings_casual, 3),
                    "CHANCE": (self.chance_rounds, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=int(weights["settings"] * factor * (1 / 6)),
            ),
            GameObjectiveTemplate(
                label="Play a LENGTH game with SETTINGS & CHANCE Chance Round",
                data={
                    "LENGTH": (self.game_lengths_base, 1),
                    "SETTINGS": (self.settings_comp, 3),
                    "CHANCE": (self.chance_rounds, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["settings"] * factor * (2 / 6)),
            ),
            GameObjectiveTemplate(
                label="Play a LENGTH game with SETTINGS & CHANCE Chance Round",
                data={
                    "LENGTH": (self.game_lengths_time_consuming, 1),
                    "SETTINGS": (self.settings_comp, 3),
                    "CHANCE": (self.chance_rounds, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=int(weights["settings"] * factor * (1 / 6)),
            ),
            GameObjectiveTemplate(
                label="Play a game on the STAGE stage",
                data={"STAGE": (self.stages, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["stages"] * factor,
            ),
            GameObjectiveTemplate(
                label="Answer NUMBER CATEGORY question(s) correctly",
                data={
                    "NUMBER": (self.questions_number, 1),
                    "CATEGORY": (
                        lambda: self.archipelago_options.trivia_tricks_categories.value,
                        1,
                    ),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["answer_categories"] * factor,
            ),
            GameObjectiveTemplate(
                label="Play a Co-Op Vs Boss game against BOSS",
                data={"BOSS": (self.bosses, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["coop_bosses"] * factor,
            ),
            GameObjectiveTemplate(
                label="Win a Co-Op Vs Boss game against BOSS",
                data={"BOSS": (self.bosses, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=weights["coop_bosses_win"] * factor,
            ),
            GameObjectiveTemplate(
                label="Play a game with an active Twitch chat",
                data={},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["twitch"] * factor,
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["bonus"] * factor,
            ),
        ]
