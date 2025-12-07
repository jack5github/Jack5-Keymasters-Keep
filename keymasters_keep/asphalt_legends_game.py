"""
A Keymaster's Keep implementation of Asphalt Legends, created by Jack5. The following objective types are included:

- Daily/VIP goals and events
- Improve specific cars
- Bonus objectives

As with other Jack5-made implementations, the weights for each kind of objective can be customised using the `asphalt_legends_weights` YAML option.

For improving specific cars, the `asphalt_legends_cars` YAML option can be filled with the cars you own that you're able to upgrade or apply import parts to.
"""

from __future__ import annotations
from dataclasses import dataclass
from Options import OptionCounter, OptionList  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class AsphaltLegendsWeights(OptionCounter):
    """
    The weights to use for Asphalt Legends objective types. Defaults to only objectives that can be completed by new users. If at a high enough level to access VIP features, it is recommended to start with the following weights:

    ```yaml
    daily: 5
    vip: 2
    improve_car: 1
    bonus: 8
    ```
    """

    display_name: str = "Asphalt Legends Weights"
    default: dict[str, int] = {"daily": 5, "vip": 0, "improve_car": 1, "bonus": 8}


class AsphaltLegendsCars(OptionList):
    """
    The list of cars to use for the Asphalt Legends objective type `improve_car`. Defaults to a few early-game cars, add and remove cars as needed so all in the list are unlocked but not maxed out.
    """

    display_name: str = "Asphalt Legends Cars"
    default: list[str] = [
        "Mitsubishi Lancer Evolution",
        "Chevrolet Camaro LT",
        "Nissan 370Z Nismo",
        "Volkswagen XL Sport Concept",
        "DS Automobiles DS E-Tense",
        "Dodge Challenger 392 Hemi Scat Pack",
    ]


@dataclass
class AsphaltLegendsArchipelagoOptions:
    asphalt_legends_weights: AsphaltLegendsWeights
    asphalt_legends_cars: AsphaltLegendsCars


class AsphaltLegendsGame(Game):
    """
    Asphalt Legends is the ultimate arcade racing experience. It is constantly being updated with new and exciting challenges, from co-op game modes to new competitive challenges. With full-on cross-platform support, you can play how you want, seamlessly switching between Manual or TouchDrive controls using a controller, keyboard or touchscreen.

    It carries a beefy engine under the hood, making it the best-looking arcade racer on any screen. Choose from hundreds of supercars, including Lamborghinis, Ferraris, McLarens, and Porsches, and speed through beautifully rendered locations at heart-pounding speeds.
    """

    name: str = "Asphalt Legends"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.IOS  # Apple iOS
    platforms_other: list[KeymastersKeepGamePlatforms] = [
        KeymastersKeepGamePlatforms.AND,  # Android OS
        KeymastersKeepGamePlatforms.PC,
        KeymastersKeepGamePlatforms.PS4,  # Sony PlayStation 4
        KeymastersKeepGamePlatforms.PS5,  # Sony PlayStation 5
        KeymastersKeepGamePlatforms.SW,  # Nintendo Switch
        KeymastersKeepGamePlatforms.XONE,  # Microsoft Xbox One
        KeymastersKeepGamePlatforms.XSX,  # Microsoft Xbox Series X
    ]
    is_adult_only_or_unrated: bool = False
    options_cls: type[AsphaltLegendsArchipelagoOptions] = (
        AsphaltLegendsArchipelagoOptions
    )

    @staticmethod
    def daily_objectives() -> list[str]:
        return [
            "Claim a club event reward",
            "Claim a club milestone reward",
            "Claim a event collector/progression reward",
            "Claim a free pack",
            "Claim a reward from the For You section",
            "Claim a season reward",
            "Use a wild card on a car about to gain a star",
            "Customise a car",
            "Sell some import parts",
            "Claim the daily contract reward from Sponsorship",
            "Claim the daily goals goal combo",
            "Complete a season mission",
            "Buy something from the Legend Store",
            "Play the Overclock Showcase daily event",
            "Play the current Season Showcase daily event",
            "Play one of the Exclusive daily events",
            "Play or claim all rewards in the Daily Car Loot daily event",
            "Play or claim all rewards in the Class Cup daily event",
            "Play or claim all rewards in the Credits Heist daily event",
            "Play the Weekly Competition daily event",
            "Play a non-Gauntlet non-Show Room special event",
            "Play or autoplay a stage in the Show Room special event",
            "Play the World League multiplayer event",
            "Play the Season Series multiplayer event",
            "Play a private or local multiplayer match",
            "Play a Career Mode event",
        ]

    @staticmethod
    def vip_objectives() -> list[str]:
        return [
            "Claim a VIP pack",
            "Buy something from the VIP Market",
            "Play the Elite daily event",
            "Set a time in or challenge an opponent in the Gauntlet special event",
        ]

    @staticmethod
    def improve_car_objectives() -> list[str]:
        return ["Upgrade", "Apply an import part to"]

    @staticmethod
    def bonus_objectives() -> list[str]:
        return [
            "Barrel roll onto your back and crash",
            "Be forced into a 360 by a geyser",
            "Be slowed down by going off the track and still win the race",
            "Be unable to stop 360-ing and crash",
            "Break off a piece of a large environment object",
            "Crash into a pillar in the middle of the track",
            "Crash into part of the environment while mid-air",
            "Drift along a vertically-slanted part of the track",
            "Drift for 5 seconds without changing projected angle or speed",
            "Drift out of a 360",
            "Fall off the track",
            "Hit a parked car from the front or back",
            "Hit a parked car from the side",
            "Intentionally refrain from 360-ing off a ledge or jump",
            "Knockdown a police car (or an opponent as a police car)",
            "Knockdown an opponent as they land on you",
            "Knockdown an opponent by driving into them without using nitro",
            "Knockdown an opponent by landing on them",
            "Knockdown an opponent by shockwaving into them at the start of a race",
            "Knockdown an opponent with a 360",
            "Observe obvious AI rubber-banding",
            "Observe sub-optimal TouchDrive behaviour",
            "Play an entire race using TouchDrive",
            "Play an entire race without using TouchDrive",
            "Prolong a single nitro use with 2 consecutive nitro bottles",
            "Push a car off the track",
            "Ride the walls of a track",
            "Perform a 360 off a ramp that would otherwise cause a barrel roll",
            "Perform a 360 that continues for 2 consecutive jumps",
            "Perform a 360 which is immediately stopped by something",
            "Perform a shockwave into a perfect turbo",
            "Perform a shockwave out of a crash",
            "Perform a shockwave while doing a 360 in mid-air",
            "Run out of Asphalt tickets",
            "Run out of gas for a car",
            "Run out of Show Room tickets",
            "Start your second lap around the track",
            "Survive what could have been a crash",
            "Watch an ad for more credits (unless playing adless)",
            "Watch an ad for more tickets (unless playing adless)",
            "Win a race with TouchDrive without doing anything",
            "Wrestle for control of the road with an opponent",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.asphalt_legends_weights.value
        templates: list[GameObjectiveTemplate] = [
            GameObjectiveTemplate(
                label="DAILY",
                data={"DAILY": (self.daily_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["daily"],
            ),
            GameObjectiveTemplate(
                label="VIP",
                data={"VIP": (self.vip_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["vip"],
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["bonus"],
            ),
        ]
        cars: list[str] = self.archipelago_options.asphalt_legends_cars.value
        if len(cars) > 0:
            templates.append(
                GameObjectiveTemplate(
                    label="IMPROVE CAR if possible",
                    data={
                        "IMPROVE": (self.improve_car_objectives, 1),
                        "CAR": (lambda: cars, 1),
                    },
                    is_time_consuming=False,
                    is_difficult=False,
                    weight=weights["improve_car"],
                )
            )
        return templates
