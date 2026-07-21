"""
A Keymaster's Keep implementation of games exported from Backloggery, created by Jack5. The following objective types are included:

- Play (for the first time) and make progress in specific games (difficult)
- Beat and complete specific games (difficult and time consuming)
- Unpause and replay specific games (difficult)
- Rate and write reviews for specific unreviewed games
- Bonus objectives

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `backloggery_weights` YAML option.

This is a more complex and intelligent alternative to the default **[Game Backlog (META)](https://silasary.github.io/kmk_tools/games/game_backlog_game/)** implementation. To get started, visit https://backloggery.com/!/settings/data and download the 'Game Library' and 'Reviews' (optional) CSV exports, then place them into the `keymasters_keep/backloggery/` folder. If renaming them, be sure to update the `backloggery_library_path` and `backloggery_reviews_path` YAML options. (`backloggery_demo_data` is enabled for implementation demonstration purposes, but is disabled in normal use.)
"""

from __future__ import annotations
from dataclasses import dataclass
import enum
from typing import Any, TypedDict

LIBRARY_DEFAULT_PATH: str = "keymasters_keep/backloggery/library_<date>.csv"
REVIEWS_DEFAULT_PATH: str = "keymasters_keep/backloggery/reviews_<date>.csv"

try:  # Archipelago imports are done here to support running this script as main
    import Options  # pyright: ignore[reportMissingImports]
    from ..enums import (  # pyright: ignore[reportMissingImports]
        KeymastersKeepGamePlatforms,
    )
    from ..game import Game  # pyright: ignore[reportMissingImports]
    from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
        GameObjectiveTemplate,
    )

    class BackloggeryWeights(Options.OptionCounter):
        """
        The weights to use for Backloggery objective types.
        """

        display_name: str = "Backloggery Weights"
        default: dict[str, int] = {
            "play_unplayed_game": 4,
            "progress_in_game": 3,
            "beat_unfinished_game": 2,
            "complete_beaten_game": 1,
            "play_paused_game": 1,
            "replay_game": 1,
            "rate_game": 1,
            "review_game": 1,
            "bonus": 1,
        }

    class BackloggeryLibraryPath(Options.FreeText):
        """
        The path to the Backloggery 'Game Library' CSV export relative to the Archipelago folder. '<date>' in the filename will match any date in 'YYYY-MM-DD' format, later dates taking priority. If this file does not exist, generation will fail.
        """

        display_name: str = "Backloggery Library Path"
        default: str = LIBRARY_DEFAULT_PATH

    class BackloggeryReviewsPath(Options.FreeText):
        """
        The path to the Backloggery 'Reviews' CSV export relative to the Archipelago folder. '<date>' in the filename will match any date in 'YYYY-MM-DD' format, later dates taking priority. If this file does not exist, generation will proceed with no reviews.
        """

        display_name: str = "Backloggery Reviews Path"
        default: str = REVIEWS_DEFAULT_PATH

    class BackloggeryDemoData(Options.Toggle):
        """
        Whether to use demo data (based on https://backloggery.com/demo) rather than a real Backloggery Game Library CSV export. Only for use in implementation demonstration (e.g., https://silasary.github.io/kmk_tools/games/backloggery_game).
        """

        display_name: str = "Backloggery Demo Data"

except ImportError:  # Main mode, define dummy classes

    class Game:
        pass

    class KeymastersKeepGamePlatforms(enum.Enum):
        META = 0


@dataclass
class BackloggeryArchipelagoOptions:
    try:
        backloggery_weights: BackloggeryWeights
        backloggery_library_path: BackloggeryLibraryPath
        backloggery_reviews_path: BackloggeryReviewsPath
        backloggery_demo_data: BackloggeryDemoData
    except ImportError:
        pass  # Main mode, no options


class BackloggeryLibraryGame(TypedDict):
    """
    A game entry in the Backloggery 'Game Library' CSV export.
    """

    Unique_Game_ID: str
    Title: str
    Platform: str
    Sub_Platform: str
    Status: str
    Priority: str
    Format: str
    Ownership: str
    Notes: str
    Child_Of: str
    Last_Updated: str
    # TODO: Inform Drumble of fields missing from the export


class BackloggeryReview(TypedDict):
    """
    A review entry in the Backloggery 'Reviews' CSV export.
    """

    Unique_Game_ID: str
    Title: str
    Platform: str
    Rating: str
    Difficulty: str
    Review: str


class BackloggeryGame(Game):
    """
    Backloggery is a website dedicated to assisting players in beating video games that they already own. Users create their "backlog" and track their progress as they play through their collection. Each game is assigned one of six main statuses: Unplayed, Unfinished, Beaten or Completed, Endless and None. Game entries do not depend on a central database by design.

    The website is the sole creation of Drumble, having been created during 2007. In 2024, the website was overhauled to modernise its appearance, performance and usability, including the addition of CSV exports. Progress on the site is tracked in a public Trello, and development is supported through Patreon.
    """

    name: str = "Backloggery"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.META
    is_adult_only_or_unrated: bool = False
    options_cls: type[BackloggeryArchipelagoOptions] = BackloggeryArchipelagoOptions

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._games_cache: list[BackloggeryLibraryGame] | None = None
        self._reviews_cache: list[BackloggeryReview] | None = None
        self._difficult_games_cache: list[str] | None = None

    def _read_csv(self, pattern: str, required: bool = False) -> list[dict[str, Any]]:
        """
        Reads a Backloggery CSV export.

        Args:
            pattern (str): The path to the CSV export relative to the Archipelago folder, where '<date>' in the filename is replaced with any date in 'YYYY-MM-DD' format.
            required (bool): Whether the file is required to exist.

        Returns:
            list[dict[str, Any]] | None: The contents of the CSV export, or None if the file does not exist.
        """
        from csv import DictReader
        import os
        import re

        pattern = re.escape(pattern)
        # After `re.escape()`, backslashes are escaped twice
        if os.sep == "\\":
            pattern = pattern.replace("\\\\", os.sep)
        pattern = pattern.replace("<date>", r"\d{4}-\d{2}-\d{2}")
        directory, pattern_path = os.path.split(pattern)
        paths: list[str] = os.listdir(directory)
        matching_paths: list[str] = []
        for path in paths:
            if re.match(pattern_path, path):
                matching_paths.append(os.path.join(directory, path))
        if len(matching_paths) == 0:
            if required:
                raise FileNotFoundError(f"No file exists that matches {pattern!r}")
            return []
        matching_paths.sort(reverse=True)
        data: list[dict[str, Any]]
        with open(matching_paths[0], "r", encoding="utf-8") as f:
            # The first two lines of Backloggery exports are irrelevant, discard them
            f.readline()
            f.readline()
            reader = DictReader(f)
            data = list(reader)
            data = [{re.sub("[\\s-]", "_", k): v for k, v in d.items()} for d in data]
        return data

    def _games(self) -> list[BackloggeryLibraryGame]:
        if self._games_cache is not None:
            return self._games_cache
        games: list[BackloggeryLibraryGame]
        if not hasattr(self, "archipelago_options"):  # Main mode
            games = self._read_csv(  # pyright: ignore[reportAssignmentType]
                LIBRARY_DEFAULT_PATH, True
            )
        elif not self.archipelago_options.backloggery_demo_data.value:
            games = self._read_csv(  # pyright: ignore[reportAssignmentType]
                self.archipelago_options.backloggery_library_path.value, True
            )  #
        else:  # Demo data
            games = [
                BackloggeryLibraryGame(
                    Unique_Game_ID='24088971',
                    Title='Altered Beast',
                    Platform='Sega Genesis',
                    Sub_Platform='',
                    Status='Unfinished',
                    Priority='Normal',
                    Format='Physical (Game Only)',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2025-12-05 05:46',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='4561638',
                    Title='Avenging Spirit',
                    Platform='Game Boy',
                    Sub_Platform='',
                    Status='Unfinished',
                    Priority='Now Playing',
                    Format='Physical',
                    Ownership='Own',
                    Notes='Games in your now playing will "fade" when not updated for two weeks.',
                    Child_Of='',
                    Last_Updated='2024-05-21 02:00',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='4561639',
                    Title='Bionic Commando',
                    Platform='Game Boy',
                    Sub_Platform='',
                    Status='Completed',
                    Priority='Normal',
                    Format='Physical',
                    Ownership='Own',
                    Notes='Arguably better than the fantastic NES version',
                    Child_Of='',
                    Last_Updated='2024-05-21 03:35',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516261',
                    Title='Blood Omen: Legacy of Kain',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='List Steam games separately or group them under PC using sub-platforms.',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:26',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514197',
                    Title='Castlevania',
                    Platform='Nintendo Entertainment System',
                    Sub_Platform='',
                    Status='Completed',
                    Priority='Normal',
                    Format='',
                    Ownership='Own',
                    Notes="One of my favorite series and it got off to an amazing start.  It just doesn't get more classic than this.",
                    Child_Of='',
                    Last_Updated='2024-09-30 07:40',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516185',
                    Title='Dragon Age 2',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Completed',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='Clear on normal with a Rogue Archer.\n\nEnjoyed it overall, but it has a lot of glaring flaws.',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:05',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='23772121',
                    Title='Dungeon Crawl Stone Soup',
                    Platform='PC',
                    Sub_Platform='',
                    Status='Unfinished',
                    Priority='Ongoing',
                    Format='',
                    Ownership='Own',
                    Notes='Playing as a poltergeist, haunting armor and smacking goblins with it.',
                    Child_Of='',
                    Last_Updated='2025-09-02 02:32',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516233',
                    Title='The Elder Scrolls V: Skyrim',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Unfinished',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='[Lv.4  Arcane Sniper] Playing with a ton of mods, namely Frostfall and Realistic Needs & Disease, to make things harder because I hate myself.',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:29',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516251',
                    Title='Factorio',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Unplayed',
                    Priority='High',
                    Format='Digital',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:41',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514211',
                    Title='Final Fight 2',
                    Platform='Super Nintendo Entertainment System',
                    Sub_Platform='',
                    Status='Beaten',
                    # Changed from demo data in order to demonstrate `games_to_unpause()`
                    Priority='Paused',
                    Format='Physical (Game Only)',
                    Ownership='Own',
                    Notes='Finished on normal with Marc. Might do Expert for the full ending sometime.',
                    Child_Of='',
                    Last_Updated='2024-09-30 07:46',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516242',
                    Title='The Goonies II',
                    Platform='Nintendo Entertainment System',
                    Sub_Platform='',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='Physical',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:38',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516157',
                    Title='Guild Wars 2',
                    Platform='PC',
                    Sub_Platform='',
                    Status='Endless',
                    Priority='Ongoing',
                    Format='',
                    Ownership='Own',
                    Notes="I'll finish crafting that legendary hammer someday....",
                    Child_Of='',
                    Last_Updated='2024-10-01 02:20',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516222',
                    Title='Half-Life 2',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Beaten',
                    Priority='Now Playing',
                    Format='Digital',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:19',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516223',
                    Title='Half-Life 2: Episode One',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Beaten',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='',
                    Child_Of='22516222',
                    Last_Updated='2024-10-01 02:19',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516227',
                    Title='Half-Life 2: Episode Two',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='Damn you, Steam sales, you got one last shot in.',
                    Child_Of='22516222',
                    Last_Updated='2024-10-01 02:20',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514217',
                    Title='Mario Kart Wii',
                    Platform='Wii',
                    Sub_Platform='',
                    # Changed from demo data in order to demonstrate `games_to_replay()`
                    Status='Replay',
                    Priority='Normal',
                    Format='',
                    Ownership='Physical (Complete In Box)',
                    Notes='Still my favorite Mario Kart.  ~8300VR',
                    Child_Of='',
                    Last_Updated='2024-09-30 07:49',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516288',
                    Title='Mega Man 5',
                    Platform='Nintendo Entertainment System',
                    Sub_Platform='',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:55',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514213',
                    Title='Metroid Prime Trilogy',
                    Platform='Wii',
                    Sub_Platform='',
                    Status='None',
                    Priority='Normal',
                    Format='Physical (Complete In Box)',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-09-30 07:47',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514214',
                    Title='Metroid Prime',
                    Platform='Wii',
                    Sub_Platform='',
                    Status='Completed',
                    Priority='Normal',
                    Format='Physical (Complete In Box)',
                    Ownership='Own',
                    Notes='',
                    Child_Of='22514213',
                    Last_Updated='2024-09-30 07:47',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514215',
                    Title='Metroid Prime 2: Echoes',
                    Platform='Wii',
                    Sub_Platform='',
                    Status='Completed',
                    Priority='Normal',
                    Format='Physical (Complete In Box)',
                    Ownership='Own',
                    Notes='May the light of Aether shine forever on our enemies.',
                    Child_Of='22514213',
                    Last_Updated='2024-09-30 07:48',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514216',
                    Title='Metroid Prime 3: Corruption',
                    Platform='Wii',
                    Sub_Platform='',
                    Status='Beaten',
                    Priority='Normal',
                    Format='Physical (Complete In Box)',
                    Ownership='Own',
                    Notes='Finished on Veteran in 17:09',
                    Child_Of='22514213',
                    Last_Updated='2024-09-30 07:48',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514203',
                    Title='Parasite Eve',
                    Platform='PlayStation',
                    Sub_Platform='',
                    Status='Completed',
                    Priority='Normal',
                    Format='',
                    Ownership='Own',
                    Notes="[Progress: ||Chrysler Building - Floor 77||] Very fun and stylish game! Can't say I recommend the post-game though.",
                    Child_Of='',
                    Last_Updated='2024-09-30 07:42',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514206',
                    Title='Phantasy Star II',
                    Platform='Sega Genesis',
                    Sub_Platform='',
                    Status='Completed',
                    Priority='Normal',
                    Format='Physical',
                    Ownership='Own',
                    Notes='Even as a fan of auto-battle systems, this seemed like a step back from PS1.',
                    Child_Of='',
                    Last_Updated='2024-09-30 07:43',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516255',
                    Title='RayStorm',
                    Platform='PlayStation',
                    Sub_Platform='',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='Physical',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:42',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514209',
                    Title='The Secret of Monkey Island: Special Edition',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Completed',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='Fun little game.  The vagueness of the first hints in the hint system were just the right amount of vague to nudge you in the right direction.',
                    Child_Of='',
                    Last_Updated='2024-09-30 07:44',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22514192',
                    Title='Stardew Valley',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Completed',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='[Year 3] Restored the community center, passed the evaluation, got all (non-marriage) heart events, and finished the final bundle.',
                    Child_Of='',
                    Last_Updated='2024-09-30 07:39',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516238',
                    Title='Sweet Home',
                    Platform='Nintendo Entertainment System',
                    Sub_Platform='',
                    Status='Unfinished',
                    Priority='Normal',
                    Format='Physical (Unlicensed Repro)',
                    Ownership='Own',
                    Notes="This is such a great horror RPG. I can't recommend it enough.",
                    Child_Of='',
                    Last_Updated='2024-10-01 02:36',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516268',
                    Title='Tear Ring Saga',
                    Platform='PlayStation',
                    Sub_Platform='',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='',
                    Ownership='Own',
                    Notes='Fire Emblem with the serial numbers filed off.',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:49',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516256',
                    Title="Tecmo's Deception: Invitation to Darkness",
                    Platform='PlayStation',
                    Sub_Platform='',
                    Status='Unfinished',
                    Priority='Normal',
                    Format='Physical',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:43',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22706407',
                    Title='Teenage Mutant Ninja Turtles: Fall of the Footclan',
                    Platform='Game Boy',
                    Sub_Platform='',
                    Status='Beaten',
                    Priority='Normal',
                    Format='Physical (Game Only)',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-11-22 09:41',
                ),
                BackloggeryLibraryGame(
                    Unique_Game_ID='22516231',
                    Title='Trine',
                    Platform='PC',
                    Sub_Platform='Steam',
                    Status='Unplayed',
                    Priority='Normal',
                    Format='Digital',
                    Ownership='Own',
                    Notes='',
                    Child_Of='',
                    Last_Updated='2024-10-01 02:28',
                ),
            ]
        self._games_cache = games
        return games

    def _reviews(self) -> list[BackloggeryReview]:
        if self._reviews_cache is not None:
            return self._reviews_cache
        reviews: list[BackloggeryReview]
        if not hasattr(self, "archipelago_options"):  # Main mode
            reviews = self._read_csv(  # pyright: ignore[reportAssignmentType]
                REVIEWS_DEFAULT_PATH
            )
        elif not self.archipelago_options.backloggery_demo_data.value:
            reviews = self._read_csv(  # pyright: ignore[reportAssignmentType]
                self.archipelago_options.backloggery_reviews_path.value
            )
        else:  # Demo data
            reviews = [
                BackloggeryReview(
                    Unique_Game_ID='4561639',
                    Title='Bionic Commando',
                    Platform='Game Boy',
                    Rating='5',
                    Difficulty='',
                    Review='',
                ),
                BackloggeryReview(
                    Unique_Game_ID='22514192',
                    Title='Stardew Valley',
                    Platform='PC',
                    Rating='4.5',
                    Difficulty='Relaxing',
                    Review="""
Super fun farming game. I've not played a Harvest Moon yet so I don't have much to compare it too. Only complaint is it starts to feel a bit too repetitive and aimless after year 2, but I'm not sure how they could fix that. 

Highly recommended.
                    """.strip(),
                ),
            ]
        self._reviews_cache = reviews
        return reviews

    def _difficult_games(self) -> list[str]:
        self._difficult_games_cache = [
            r["Unique_Game_ID"]
            for r in self._reviews()
            if r["Difficulty"] in ["Too Hard", "Unfair"]
        ]
        return self._difficult_games_cache

    def _get_game_title(
        self, game: BackloggeryLibraryGame, title_only: bool = False
    ) -> str:
        title: str = ""
        if game["Child_Of"] != "":
            parent: BackloggeryLibraryGame = next(
                (g for g in self._games() if g["Unique_Game_ID"] == game["Child_Of"])
            )
            title += f"{self._get_game_title(parent, True)} - "
        title += game["Title"]
        if not title_only:
            title += f" ({game['Platform']}"
            if game["Sub_Platform"] != "":
                title += f", {game['Sub_Platform']}"
            title += ")"
        return title

    def _game_is_active(self, game: BackloggeryLibraryGame) -> bool:
        return game["Priority"] not in ["Paused", "Shelved"]

    def _game_is_owned(self, game: BackloggeryLibraryGame) -> bool:
        return game["Ownership"] not in ["Wishlist", "Played It", "Formerly Owned"]

    def _game_is_difficult(self, game: BackloggeryLibraryGame, difficult: bool) -> bool:
        return (game["Unique_Game_ID"] in self._difficult_games()) == difficult

    def games_to_play(self, difficult: bool) -> list[BackloggeryLibraryGame]:
        return [
            g
            for g in self._games()
            if g["Status"] == "Unplayed"
            and self._game_is_active(g)
            and self._game_is_owned(g)
            and self._game_is_difficult(g, difficult)
        ]

    def games_to_progress_in(self, difficult: bool) -> list[BackloggeryLibraryGame]:
        return [
            g
            for g in self._games()
            # Endless games are included in this list
            if g["Status"] not in ["Unplayed", "Completed", "None"]
            and self._game_is_active(g)
            and self._game_is_owned(g)
            and self._game_is_difficult(g, difficult)
        ]

    def games_to_beat(self, difficult: bool) -> list[BackloggeryLibraryGame]:
        return [
            g
            for g in self._games()
            if g["Status"] == "Unfinished"
            and self._game_is_active(g)
            and self._game_is_owned(g)
            and self._game_is_difficult(g, difficult)
        ]

    def games_to_complete(self, difficult: bool) -> list[BackloggeryLibraryGame]:
        return [
            g
            for g in self._games()
            if g["Status"] == "Beaten"
            and self._game_is_active(g)
            and self._game_is_owned(g)
            and self._game_is_difficult(g, difficult)
        ]

    def games_to_unpause(self, difficult: bool) -> list[BackloggeryLibraryGame]:
        return [
            g
            for g in self._games()
            if g["Priority"] == "Paused"
            and self._game_is_owned(g)
            and self._game_is_difficult(g, difficult)
        ]

    def games_to_replay(self, difficult: bool) -> list[BackloggeryLibraryGame]:
        return [
            g
            for g in self._games()
            if g["Priority"] == "Replay"
            and self._game_is_owned(g)
            and self._game_is_difficult(g, difficult)
        ]

    def games_to_rate(self) -> list[BackloggeryLibraryGame]:
        games: list[BackloggeryLibraryGame] = self._games()
        unrated_ids: list[str] = [
            r["Unique_Game_ID"]
            for r in self._reviews()
            if r["Rating"] == "" or r["Difficulty"] == ""
        ]
        return [
            g
            for g in games
            if g["Unique_Game_ID"] in unrated_ids and self._game_is_owned(g)
        ]

    def games_to_review(self) -> list[BackloggeryLibraryGame]:
        games: list[BackloggeryLibraryGame] = self._games()
        unreviewed_ids: list[str] = [
            r["Unique_Game_ID"] for r in self._reviews() if r["Review"] == ""
        ]
        return [
            g
            for g in games
            if g["Unique_Game_ID"] in unreviewed_ids and self._game_is_owned(g)
        ]

    def games_str(self, games: list[BackloggeryLibraryGame]) -> list[str]:
        are_low_or_high: bool = False
        try:
            next(g for g in games if g["Priority"] in ["Low", "High"])
            are_low_or_high = True
        except:
            pass
        game_strs: list[str] = []
        for game in games:
            game_str: str = self._get_game_title(game)
            game_strs.append(game_str)
            if not are_low_or_high:
                continue
            if game["Priority"] != "Low":  # Low priority games are half as likely
                game_strs.append(game_str)
            if game["Priority"] == "High":  # High priority games are twice as likely
                game_strs.append(game_str)
                game_strs.append(game_str)
        return game_strs

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Check and update the games in one of your lists",
            "Check and update your High priority games",
            "Check and update your Low priority games",
            "Check your Multitap timeline",
            "Create a new list",
            "Remove fading games from your Now Playing",
            "Update your profile's About section",
            "Update your profile's avatar",
            "Update your profile's banner",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.backloggery_weights.value
        factor: int = 100
        templates: list[GameObjectiveTemplate] = []
        for objective in [
            (
                "Play GAME for the first time",
                self.games_to_play,
                "play_unplayed_game",
                True,
                False,
            ),
            (
                "Make progress in GAME",
                self.games_to_progress_in,
                "progress_in_game",
                True,
                False,
            ),
            ("Beat GAME", self.games_to_beat, "beat_unfinished_game", True, True),
            (
                "Complete GAME",
                self.games_to_complete,
                "complete_beaten_game",
                True,
                True,
            ),
            (
                "Unpause and return to GAME",
                self.games_to_unpause,
                "unpause_paused_game",
                True,
                False,
            ),
            ("Start replaying GAME", self.games_to_replay, "replay_game", True, False),
            (
                "Set review ratings for GAME",
                self.games_to_rate,
                "rate_game",
                False,
                False,
            ),
            (
                "Write a review for GAME",
                self.games_to_review,
                "review_game",
                False,
                False,
            ),
        ]:
            if objective[3]:  # May be difficult
                games_base: list[BackloggeryLibraryGame] = objective[1](False)
                games_difficult: list[BackloggeryLibraryGame] = objective[1](True)
                if len(games_base) + len(games_difficult) == 0:
                    continue
                base_ratio: float = len(games_base) / (
                    len(games_base) + len(games_difficult)
                )
                difficult_ratio: float = 1 - base_ratio
                if len(games_base) != 0:
                    templates.append(
                        GameObjectiveTemplate(
                            label=objective[0],
                            data={"GAME": (lambda g=games_base: self.games_str(g), 1)},
                            is_time_consuming=objective[4],
                            is_difficult=False,
                            weight=int(weights[objective[2]] * factor * base_ratio),
                        )
                    )
                if len(games_difficult) != 0:
                    templates.append(
                        GameObjectiveTemplate(
                            label=objective[0],
                            data={
                                "GAME": (lambda g=games_difficult: self.games_str(g), 1)
                            },
                            is_time_consuming=objective[4],
                            is_difficult=True,
                            weight=int(
                                weights[objective[2]] * factor * difficult_ratio
                            ),
                        )
                    )
            else:
                games: list[BackloggeryLibraryGame] = objective[1]()
                if len(games) == 0:
                    continue
                templates.append(
                    GameObjectiveTemplate(
                        label=objective[0],
                        data={"GAME": (lambda g=games: self.games_str(g), 1)},
                        is_time_consuming=objective[4],
                        is_difficult=False,
                        weight=weights[objective[2]] * factor,
                    )
                )
        templates.append(
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["bonus"] * factor,
            )
        )
        return templates


if __name__ == "__main__":
    """
    The main script, run when executing `python -m keymasters_keep.backloggery_game` in the project root. Prints the most recent Backloggery game library and reviews data to the console using pandas.
    """
    import pandas

    pandas.set_option("display.width", None)
    pandas.set_option("display.max_colwidth", None)
    pandas.set_option("display.max_columns", None)
    pandas.set_option("display.max_rows", None)
    data: list[BackloggeryLibraryGame] | list[BackloggeryReview] = (
        BackloggeryGame()._games()
    )
    df = pandas.DataFrame(data)
    df.set_index("Unique_Game_ID", inplace=True)
    print(df)
    data = BackloggeryGame()._reviews()
    df = pandas.DataFrame(data)
    df.set_index("Unique_Game_ID", inplace=True)
    print(df)
