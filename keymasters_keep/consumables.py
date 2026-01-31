"""
A Keymaster's Keep implementation of the meta concept of consumables, created by Jack5.

Unlike other Jack5-made implementations, the weights of each consumable cannot be controlled by the user, as the weights are calculated based on the expected rarity of each consumable. Instead, use the `consumables_min_rarity`, `consumables_max_rarity` and `consumables_banned_types` options to control which consumables appear.

Pull requests to add new consumables to the standard rotation or just give names and inspirations to existing ones are welcome! You can test your custom consumables before submitting them (or just keep them to yourself) with the `consumables_custom_consumables` option.
"""

from __future__ import annotations
from dataclasses import dataclass
import enum
from functools import cached_property
from typing import Any


class ConsumableRarity(enum.Enum):
    common = 0  # Smallest reward, no control
    uncommon = 1  # Small reward, very little control
    rare = 2  # Medium reward, little control
    very_rare = 3  # Large reward, some control
    epic = 4  # Larger reward, more control
    super_epic = 5  # Huge reward, even more control
    legendary = 6  # Gigantic reward, all the control


MAX_RARITY: int = max([rarity.value for rarity in ConsumableRarity])

try:  # Archipelago imports are done here to support running this script as main
    import Options  # pyright: ignore[reportMissingImports]
    import Utils  # pyright: ignore[reportMissingImports]
    from ..enums import (  # pyright: ignore[reportMissingImports]
        KeymastersKeepGamePlatforms,
    )
    from ..game import Game  # pyright: ignore[reportMissingImports]
    from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
        GameObjectiveTemplate,
    )

    class ConsumablesMinRarity(Options.Range):
        """
        The minimum rarity required for consumables to appear. Increasing this will raise the overall power of consumables.
        """

        display_name: str = "Consumables Minimum Rarity"
        range_start: int = 0
        range_end: int = MAX_RARITY
        default: int = 0

    class ConsumablesMaxRarity(Options.Range):
        """
        The maximum rarity allowed for consumables to appear. Reducing this will lower the overall power of consumables.
        """

        display_name: str = "Consumables Maximum Rarity"
        range_start: int = 0
        range_end: int = MAX_RARITY
        default: int = MAX_RARITY

    class ConsumablesBannedTypes(Options.OptionList):
        """
        The list of consumable types banned from appearing. A consumable's types can be found in the `consumables()` method of the source code. "on_hint" and "on_shop" are banned by default, "on_hint" in order to get players used to the concept of consumables, and "on_shop" as it is uncommon for players of Keymaster's Keep to have shops enabled. To allow these conditional consumables to appear, set this to an empty list.
        """

        display_name: str = "Consumables Banned Types"
        default: list[str] = ["on_hint", "on_shop"]

    # TODO: Accept a true list of dictionaries as opposed to a string
    class ConsumablesCustomConsumables(Options.FreeText):
        """
        YAML lists of user-made consumables to add to the game, passed as strings. Custom consumables obey the `consumables_min_rarity`, `consumables_max_rarity` and `consumables_banned_types` options. Each item in a YAML list should be a dictionary with the following keys:
            - `name` (str) - The name of the consumable.
            - `description` (str) - The description of the consumable.
            - `rarity` (str | int) - The rarity of the consumable, as it is represented in the `ConsumableRarity` enum.
            - `types` (list[str]): The types of the consumable, used in filtering. Defaults to None.
            - `creators` (list[str]) - The people that came up with the idea for the consumable.
        """

        display_name: str = "Consumables Custom Consumables"
        default: str = "[]"

    class ConsumablesShowNames(Options.DefaultOnToggle):
        """
        Whether to show consumable names at the start of their descriptions.
        """

        display_name: str = "Consumables Show Names"

    class ConsumablesShowRarities(Options.DefaultOnToggle):
        """
        Whether to show consumable rarities at the end of their descriptions.
        """

        display_name: str = "Consumables Show Rarities"

    # TODO: Make this default to on once more consumables have been added
    class ConsumablesShowCreators(Options.Toggle):
        """
        Whether to show consumable creators at the end of their descriptions.
        """

        display_name: str = "Consumables Show Creators"

except ImportError:  # Main mode, define dummy classes

    class Game:
        pass

    class KeymastersKeepGamePlatforms(enum.Enum):
        META = 0


@dataclass
class ConsumablesArchipelagoOptions:
    try:
        consumables_min_rarity: ConsumablesMinRarity
        consumables_max_rarity: ConsumablesMaxRarity
        consumables_banned_types: ConsumablesBannedTypes
        consumables_custom_consumables: ConsumablesCustomConsumables
        consumables_show_names: ConsumablesShowNames
        consumables_show_rarities: ConsumablesShowRarities
        consumables_show_creators: ConsumablesShowCreators
    except ImportError:
        pass  # Main mode, no options


class Consumable:
    """
    A consumable for Keymaster's Keep. When designing consumables, give no more than 5 of the reward of choice, and no more than 2 of pivotal objects such as areas or hinted items.
    """

    def __init__(
        self,
        name: str,
        description: str,
        rarity: ConsumableRarity,
        types: list[str],
        inspiration: str | None = None,
        creators: list[str] = ["Jack5"],
        conditionals: list[ConsumableConditional] | None = None,
    ) -> None:
        """
        Initialises a new Consumable instance.

        Args:
            name (str): The name of the consumable.
            description (str): The description of the consumable.
            rarity (ConsumableRarity): The rarity of the consumable.
            types (list[str]): The types of the consumable, used in filtering.
            inspiration (str | None, optional): The inspiration for the consumable. Defaults to None.
            creators (list[str]): The people that came up with the idea for the consumable. Defaults to ["Jack5"].
            conditionals (list[ConsumableConditional] | None, optional): Conditionals related to the consumable that form new consumables. Defaults to None.
        """
        self.name: str = name
        self.description: str = description
        self.rarity: ConsumableRarity = rarity
        self.types: list[str] = types
        self.inspiration: str | None = inspiration
        self.creators: list[str] = creators
        self.conditionals: list[ConsumableConditional] | None = conditionals

    def __str__(self, show_rarity: bool, show_name: bool, show_creators: bool) -> str:
        """
        Returns a string representation of a Consumable instance.

        Args:
            show_rarity (bool): Whether to show the rarity of the consumable.
            show_name (bool): Whether to show the name of the consumable.
            show_creators (bool): Whether to show the creators of the consumable.

        Returns:
            str: The string representation of the Consumable instance.
        """
        consumable_str: str = ""
        if show_name:
            consumable_str += f"{self.name}: "
        consumable_str += self.description
        if show_rarity:
            consumable_str += f" [{self.rarity.value}]"
        if show_creators:
            consumable_str += f" | {', '.join(self.creators)}"
        return consumable_str


class ConsumableConditional:
    """
    A conditional that applies to the use of a consumable, thereby creating a new consumable.
    """

    def __init__(
        self,
        name: str,
        condition: str,
        types: list[str],
        rarity: ConsumableRarity | None = None,
        inspiration: str | None = None,
        creators: list[str] | None = None,
    ) -> None:
        """
        Initialises a new ConsumableConditional instance.

        Args:
            name (str): The name of the consumable.
            condition (str): The condition that must be met for the consumable to be used. This is followed by a comma, then the description of the parent consumable with the first letter made lowercase.
            types (list[str]): The types of the consumable, used in filtering. The parent's types are always inherited, and "conditional" is always added.
            rarity (ConsumableRarity | None, optional): The rarity of the consumable. This is generally lower than the parent consumable due to the need to fulfil the condition. If None, it is inherited from the parent consumable. Defaults to None.
            inspiration (str | None, optional): The inspiration for the consumable. Defaults to None.
            creators (list[str] | None, optional): The people that came up with the idea for the consumable. If None, they are inherited from the parent consumable. Defaults to None.
        """
        self.name: str = name
        self.condition: str = condition
        types.append("conditional")
        self.types: list[str] = types
        self.rarity: ConsumableRarity | None = rarity
        self.inspiration: str | None = inspiration
        self.creators: list[str] | None = creators

    def __str__(self, show_rarity: bool, show_name: bool, show_creators: bool) -> str:
        """
        Returns the string representation of a ConsumableConditional instance. This method is not used when consumables are generated, refer to `Consumable.__str__` instead.

        Args:
            show_rarity (bool): Whether to show the rarity of the consumable.
            show_name (bool): Whether to show the name of the consumable.
            show_creators (bool): Whether to show the creators of the consumable.

        Returns:
            str: The string representation of the ConsumableConditional instance.
        """
        consumable_str: str = "(Conditional) "
        if show_name:
            consumable_str += f"{self.name}: "
        consumable_str += self.condition
        if self.rarity is not None and show_rarity:
            consumable_str += f" [{self.rarity.value}]"
        if self.creators is not None and show_creators:
            consumable_str += f" | {', '.join(self.creators)}"
        return consumable_str


class ConsumablesGame(Game):
    """
    Consumables are items that can be used and destroyed freely as part of a Keymaster's Keep run. Some consumables are more common than others, and some have one or more conditionals, which act as related but separate consumables in their own right.

    Consumables are intended to be used to complete difficult trials, get hinted items and skip areas, among other things, though good opportunities to use them can go overlooked. Additionally, they are also themselves trials, which can lead to the unavoidable destruction of consumables if multiple areas provide them. Therefore, careful inventory and use of each consumable is key.
    """

    name: str = "Consumables"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.META
    is_adult_only_or_unrated: bool = False
    options_cls: type[ConsumablesArchipelagoOptions] = ConsumablesArchipelagoOptions

    @cached_property
    def consumables(self) -> list[Consumable]:
        """
        The property that contains all consumable definitions. When editing existing consumables, add your name to the `creators` parameter of the consumable. If the `creators` parameter does not exist, set it to `["Jack5", "<your name here>"]`. When creating new consumables, be sure to add your lone name to the `creators` parameter.

        Returns:
            list[Consumable]: The list of consumables.
        """
        consumables: list[Consumable] = [
            # TODO: Give each consumable and their conditionals a name and inspiration
            # **Trial Adjustments**
            Consumable(
                name="1 HALF REQUIRED",
                description="Meet half of 1 trial's requirements to complete it.",
                rarity=ConsumableRarity.common,
                types=["chosen_trial", "any_areas", "trial_adjustment"],
            ),
            Consumable(
                name="2 HALF REQUIRED",
                description="Meet half of up to 2 trials' requirements or all of either to complete them.",
                rarity=ConsumableRarity.uncommon,
                types=["chosen_trial", "any_areas", "trial_adjustment"],
            ),
            Consumable(
                name="1 PRIMARY REQUIRED",
                description="Meet 1 trial's primary requirements to complete it, skipping secondary requirements.",
                rarity=ConsumableRarity.common,
                types=["chosen_trial", "any_areas", "trial_adjustment"],
            ),
            Consumable(
                name="1 EASY REQUIRED",
                description="Meet 1 trial's requirements at a lower difficulty to complete it.",
                rarity=ConsumableRarity.uncommon,
                types=["chosen_trial", "any_areas", "trial_adjustment"],
            ),
            Consumable(
                name="1 NOT LAST REQUIRED",
                description="Meet most of 1 trial's requirements to complete it, skipping the last required step.",
                rarity=ConsumableRarity.common,
                types=["chosen_trial", "any_areas", "trial_adjustment"],
            ),
            Consumable(
                name="1 IN 12 HOURS",
                description="If 1 trial is incomplete after 12 hours, complete it.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "chosen_trial",
                    "any_areas",
                    "trial_adjustment",
                    "conditional",
                    "time",
                ],
            ),
            Consumable(
                name="1 IN 1 HOUR",
                description="If 1 trial is incomplete after 1 hour, complete it.",
                rarity=ConsumableRarity.rare,
                types=[
                    "chosen_trial",
                    "any_areas",
                    "trial_adjustment",
                    "conditional",
                    "time",
                ],
            ),
            Consumable(
                name="2 IN 12 HOURS",
                description="If up to 2 trials are both incomplete after 12 hours, complete them.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "chosen_trial",
                    "any_areas",
                    "trial_adjustment",
                    "conditional",
                    "time",
                ],
            ),
            Consumable(
                name="2 IN 1 HOUR",
                description="If up to 2 trials are both incomplete after 1 hour, complete them.",
                rarity=ConsumableRarity.rare,
                types=[
                    "chosen_trial",
                    "any_areas",
                    "trial_adjustment",
                    "conditional",
                    "time",
                ],
            ),
            Consumable(
                name="1 BLOCKING",
                description="If 1 trial is blocking progression, complete it.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "chosen_trial",
                    "any_areas",
                    "trial_adjustment",
                    "conditional",
                    "any_hint",
                ],
                conditionals=[
                    ConsumableConditional(
                        name="1 BLOCKING ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    )
                ],
            ),
            Consumable(
                name="2 BLOCKING",
                description="If up to 2 trials are blocking progression, complete them.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "chosen_trial",
                    "any_areas",
                    "trial_adjustment",
                    "conditional",
                    "any_hint",
                ],
            ),
            Consumable(
                name="1 FAIL REQUIRED",
                description="If an attempt to meet 1 trial's requirements fails, complete it.",
                rarity=ConsumableRarity.uncommon,
                types=["chosen_trial", "any_areas", "trial_adjustment", "conditional"],
                conditionals=[
                    ConsumableConditional(
                        name="1 FAIL REQUIRED ON TRIAL",
                        condition="After trial completion, given the area is the same",
                        rarity=ConsumableRarity.common,
                        types=["on_trial", "in_same_area"],
                    )
                ],
            ),
            Consumable(
                name="1 DIFFERENT PERSON",
                description="If 1 trial's requirements are met by a different person, complete it.",
                rarity=ConsumableRarity.common,
                types=["chosen_trial", "any_areas", "trial_adjustment", "conditional"],
            ),
            # **Area Adjustments**
            Consumable(
                name="1 AREA HALF REQUIRED",
                description="If half of 1 accessible area's trials are completed, complete the rest.",
                rarity=ConsumableRarity.epic,
                types=["all_trials", "chosen_area", "trial_adjustment"],
                conditionals=[
                    ConsumableConditional(
                        name="1 AREA HALF REQUIRED ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    )
                ],
            ),
            Consumable(
                name="1 AREA IN 48 HOURS",
                description="If no more trials are completed in 1 accessible area after 48 hours, complete them.",
                rarity=ConsumableRarity.super_epic,
                types=[
                    "all_trials",
                    "chosen_area",
                    "area_adjustment",
                    "conditional",
                    "time",
                ],
            ),
            Consumable(
                name="1 AREA BLOCKING",
                description="If 1 accessible area is blocking progression, complete all its trials.",
                rarity=ConsumableRarity.super_epic,
                types=[
                    "all_trials",
                    "chosen_area",
                    "area_adjustment",
                    "conditional",
                    "any_hint",
                ],
            ),
            Consumable(
                name="1 AREA FAIL REQUIRED",
                description="If an attempt to meet 1 trial's requirements fails, complete its area.",
                rarity=ConsumableRarity.super_epic,
                types=["all_trials", "chosen_area", "area_adjustment", "conditional"],
            ),
            # **Complete Random Trials**
            Consumable(
                name="1 RANDOM IN 1 RANDOM",
                description="Complete 1 random trial in 1 random accessible area.",
                rarity=ConsumableRarity.common,
                types=["random_trial", "random_area"],
            ),
            Consumable(
                name="2 RANDOM IN 1 RANDOM",
                description="Complete up to 2 random trials in 1 random accessible area.",
                rarity=ConsumableRarity.common,
                types=["random_trial", "random_area"],
                conditionals=[
                    ConsumableConditional(
                        name="2 RANDOM IN 1 RANDOM ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    ),
                    ConsumableConditional(
                        name="2 RANDOM IN 1 RANDOM ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            Consumable(
                name="Flight of Passage",
                description="Complete 1 random trial each in up to 2 random accessible areas.",
                inspiration="Portal 2",
                rarity=ConsumableRarity.common,
                types=["random_trial", "random_area"],
                conditionals=[
                    ConsumableConditional(
                        name="Charted Flight",
                        condition="On area completion",
                        types=["on_area"],
                    )
                ],
            ),
            Consumable(
                name="2 RANDOM IN 2 RANDOM",
                description="Complete up to 2 random trials each in up to 2 random accessible areas.",
                rarity=ConsumableRarity.uncommon,
                types=["random_trial", "random_area"],
            ),
            Consumable(
                name="1 RANDOM IN 1 CHOSEN",
                description="Complete 1 random trial in 1 accessible area.",
                rarity=ConsumableRarity.common,
                types=["random_trial", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="1 RANDOM IN 1 CHOSEN ON TRIAL",
                        condition="On trial completion, given the area is the same",
                        rarity=ConsumableRarity.common,
                        types=["on_trial", "in_same_area"],
                    )
                ],
            ),
            Consumable(
                name="2 RANDOM IN 1 CHOSEN",
                description="Complete up to 2 random trials in 1 accessible area.",
                rarity=ConsumableRarity.uncommon,
                types=["random_trial", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="2 RANDOM IN 1 CHOSEN ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    ),
                    ConsumableConditional(
                        name="2 RANDOM IN 1 CHOSEN ON TRIAL",
                        condition="On trial completion, given the area is the same",
                        rarity=ConsumableRarity.common,
                        types=["on_trial", "in_same_area"],
                    ),
                    ConsumableConditional(
                        name="2 RANDOM IN 1 CHOSEN ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            # **Complete Specific Trials**
            Consumable(
                name="Chainlink Lasso",
                description="Complete the trials at the top and bottom of 1 accessible area.",
                inspiration="PEAK",
                rarity=ConsumableRarity.uncommon,
                types=["top_bottom_trials", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="Lasso of Destiny",
                        inspiration="Indiana Jones and the Dial of Destiny",
                        condition="On area completion",
                        types=["on_area"],
                    ),
                    ConsumableConditional(
                        name="Pocket Lasso",
                        condition="On top or bottom trial completion, given the area is the same",
                        rarity=ConsumableRarity.common,
                        types=["on_trial", "in_same_area"],
                    ),
                    ConsumableConditional(
                        name="1 EDGES IN 1 CHOSEN ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            Consumable(
                name="1 EDGES IN 2 CHOSEN",
                description="Complete the trials at the top and bottom of up to 2 accessible areas.",
                rarity=ConsumableRarity.rare,
                types=["top_bottom_trials", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="1 EDGES IN 2 CHOSEN ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    )
                ],
            ),
            Consumable(
                name="2 EDGES IN 1 CHOSEN",
                description="Complete the 2 trials each at the top and bottom of 1 accessible area.",
                rarity=ConsumableRarity.very_rare,
                types=["top_bottom_trials", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="2 EDGES IN 1 CHOSEN ON TRIAL",
                        condition="On top or bottom trial completion, given the area is the same",
                        rarity=ConsumableRarity.rare,
                        types=["on_trial", "in_same_area"],
                    ),
                    ConsumableConditional(
                        name="2 EDGES IN 1 CHOSEN ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            Consumable(
                name="2 EDGES IN 2 CHOSEN",
                description="Complete the 2 trials each at the top and bottom of up to 2 accessible areas.",
                rarity=ConsumableRarity.very_rare,
                types=["top_bottom_trials", "chosen_area"],
            ),
            Consumable(
                name="BESIDE 5 IN 1 CHOSEN",
                description="Complete the trials right beside all 5+ trial chains in 1 accessible area.",
                rarity=ConsumableRarity.rare,
                types=["trials_beside", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="BESIDE 5 IN 1 CHOSEN ON TRIAL",
                        condition="On trial completion, given it is part of the chain",
                        rarity=ConsumableRarity.uncommon,
                        types=["on_trial", "in_trial_chain"],
                    )
                ],
            ),
            Consumable(
                name="BESIDE 5 IN 2 CHOSEN",
                description="Complete the trials right beside all 5-trial chains in up to 2 accessible areas.",
                rarity=ConsumableRarity.very_rare,
                types=["trials_beside", "chosen_area"],
            ),
            Consumable(
                name="BESIDE ALL IN 1 CHOSEN",
                description="Complete the trials right beside all completed in 1 accessible area.",
                rarity=ConsumableRarity.epic,
                types=["trials_beside", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="BESIDE ALL IN 1 CHOSEN ON TRIAL",
                        rarity=ConsumableRarity.very_rare,
                        condition="On trial completion, given the area is the same",
                        types=["on_trial", "in_same_area"],
                    ),
                    ConsumableConditional(
                        name="BESIDE ALL IN 1 CHOSEN ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            Consumable(
                name="BESIDE ALL IN 2 CHOSEN",
                description="Complete the trials right beside all completed in up to 2 accessible areas.",
                rarity=ConsumableRarity.legendary,
                types=["trials_beside", "chosen_area"],
            ),
            # **Complete Chosen Trials**
            Consumable(
                name="1 CHOSEN IN ANY",
                description="Complete 1 accessible trial.",
                rarity=ConsumableRarity.rare,
                types=["chosen_trial", "any_areas"],
                conditionals=[
                    ConsumableConditional(
                        name="1 CHOSEN IN ANY ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    ),
                    ConsumableConditional(
                        name="1 CHOSEN IN ANY ON TRIAL",
                        condition="On trial completion",
                        types=["on_trial"],
                    ),
                ],
            ),
            Consumable(
                name="2 CHOSEN IN ANY",
                description="Complete up to 2 accessible trials.",
                rarity=ConsumableRarity.very_rare,
                types=["chosen_trial", "any_areas"],
                conditionals=[
                    ConsumableConditional(
                        name="2 CHOSEN IN ANY ON TRIAL",
                        condition="On trial completion",
                        types=["on_trial"],
                    ),
                    ConsumableConditional(
                        name="2 CHOSEN IN ANY ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            Consumable(
                name="Chimera's Instinct",
                description="Complete up to 5 accessible trials.",
                inspiration="Tower Unite (Little Crusaders)",
                rarity=ConsumableRarity.epic,
                types=["chosen_trial", "any_areas"],
            ),
            Consumable(
                name="1 CHOSEN IN ALL",
                description="Complete 1 trial each in all accessible areas.",
                rarity=ConsumableRarity.super_epic,
                types=["chosen_trial", "all_areas"],
                conditionals=[
                    ConsumableConditional(
                        name="1 CHOSEN IN ALL ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    ),
                    ConsumableConditional(
                        name="1 CHOSEN IN ALL ON TRIAL",
                        condition="On trial completion, excluding the current area",
                        rarity=ConsumableRarity.epic,
                        types=["on_trial", "in_other_areas"],
                    ),
                    ConsumableConditional(
                        name="1 CHOSEN IN ALL ON SHOP",
                        condition="On shop item purchase",
                        types=["on_shop"],
                    ),
                ],
            ),
            # **Complete Hinted Trials**
            Consumable(
                name="FILLER HINT IN 1 TRIAL",
                description="If a filler item is hinted for 1 accessible trial, complete it.",
                rarity=ConsumableRarity.common,
                types=[
                    "on_hint",
                    "filler_hint",
                    "chosen_trial",
                    "any_areas",
                    "conditional",
                ],
            ),
            Consumable(
                name="TRAP HINT IN 1 TRIAL",
                description="If a trap item is hinted for 1 accessible trial, complete it.",
                rarity=ConsumableRarity.common,
                types=[
                    "on_hint",
                    "trap_hint",
                    "chosen_trial",
                    "any_areas",
                    "conditional",
                ],
            ),
            Consumable(
                name="PROGRESSION HINT IN 1 TRIAL",
                description="If a progression item is hinted for 1 accessible trial, complete it.",
                rarity=ConsumableRarity.common,
                types=[
                    "on_hint",
                    "progression_hint",
                    "chosen_trial",
                    "any_areas",
                    "conditional",
                ],
            ),
            Consumable(
                name="ANY HINT IN 1 TRIAL",
                description="If any item is hinted for 1 accessible trial, complete it.",
                rarity=ConsumableRarity.common,
                types=[
                    "on_hint",
                    "any_hint",
                    "chosen_trial",
                    "any_areas",
                    "conditional",
                ],
            ),
            Consumable(
                name="ANY HINTS IN 2 TRIALS",
                description="If any item is hinted for up to 2 accessible trials, complete them.",
                rarity=ConsumableRarity.common,
                types=[
                    "on_hint",
                    "any_hint",
                    "chosen_trial",
                    "any_areas",
                    "conditional",
                ],
            ),
            Consumable(
                name="ANY HINTS IN 5 TRIALS",
                description="If any item is hinted for up to 5 accessible trials, complete them.",
                rarity=ConsumableRarity.epic,
                types=[
                    "on_hint",
                    "any_hint",
                    "chosen_trial",
                    "any_areas",
                    "conditional",
                ],
            ),
            Consumable(
                name="FILLER HINTS IN 1 AREA",
                description="If any filler items are hinted for 1 accessible area, complete them.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "on_hint",
                    "filler_hint",
                    "all_trials",
                    "chosen_area",
                    "conditional",
                ],
            ),
            Consumable(
                name="TRAP HINTS IN 1 AREA",
                description="If any trap items are hinted for 1 accessible area, complete them.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "on_hint",
                    "trap_hint",
                    "all_trials",
                    "chosen_area",
                    "conditional",
                ],
            ),
            Consumable(
                name="PROGRESSION HINTS IN 1 AREA",
                description="If any progression items are hinted for 1 accessible area, complete them.",
                rarity=ConsumableRarity.uncommon,
                types=[
                    "on_hint",
                    "progression_hint",
                    "all_trials",
                    "chosen_area",
                    "conditional",
                ],
            ),
            Consumable(
                name="ANY HINTS IN 1 AREA",
                description="If any items are hinted for 1 accessible area, complete them.",
                rarity=ConsumableRarity.rare,
                types=[
                    "on_hint",
                    "any_hint",
                    "all_trials",
                    "chosen_area",
                    "conditional",
                ],
            ),
            Consumable(
                name="ANY HINTS IN 2 AREAS",
                description="If any items are hinted for up to 2 accessible areas, complete them.",
                rarity=ConsumableRarity.very_rare,
                types=[
                    "on_hint",
                    "any_hint",
                    "all_trials",
                    "chosen_area",
                    "conditional",
                ],
            ),
            # **Complete Areas**
            Consumable(
                name="ALL IN 1 RANDOM",
                description="Complete all trials in 1 random accessible area.",
                rarity=ConsumableRarity.super_epic,
                types=["all_trials", "random_area"],
                conditionals=[
                    ConsumableConditional(
                        name="ALL IN 1 RANDOM ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    )
                ],
            ),
            Consumable(
                name="ALL IN 1 RANDOM WITH MOST",
                description="Complete all trials in 1 accessible area with the most completed.",
                rarity=ConsumableRarity.super_epic,
                types=["all_trials", "random_area", "most_trials"],
                conditionals=[
                    ConsumableConditional(
                        name="ALL IN 1 RANDOM WITH MOST ON AREA",
                        condition="On area completion",
                        types=["on_area"],
                    )
                ],
            ),
            Consumable(
                name="ALL IN 1 RANDOM WITH LEAST",
                description="Complete all trials in 1 accessible area with the least completed.",
                rarity=ConsumableRarity.super_epic,
                types=["all_trials", "random_area", "least_trials"],
                conditionals=[
                    ConsumableConditional(
                        name="ALL IN 1 RANDOM WITH LEAST ON AREA",
                        condition="On area completion",
                        rarity=ConsumableRarity.epic,
                        types=["on_area"],
                    )
                ],
            ),
            Consumable(
                name="Ever-Unravelling Scroll",
                description="Complete all trials in 1 accessible area.",
                inspiration="Vampire Survivors",
                rarity=ConsumableRarity.super_epic,
                types=["all_trials", "chosen_area"],
                conditionals=[
                    ConsumableConditional(
                        name="Ever-Unravelling Banner",
                        condition="On area completion",
                        types=["on_area"],
                    ),
                    ConsumableConditional(
                        name="ALL IN 1 CHOSEN ON TRIAL",
                        condition="On trial completion, given the area is the same",
                        rarity=ConsumableRarity.epic,
                        types=["on_trial", "in_same_area"],
                    ),
                ],
            ),
            Consumable(
                name="ALL IN 2 RANDOM",
                description="Complete all trials in up to 2 random accessible areas.",
                rarity=ConsumableRarity.legendary,
                types=["all_trials", "random_area"],
            ),
            Consumable(
                name="ALL IN 2 CHOSEN",
                description="Complete all trials in up to 2 accessible areas.",
                rarity=ConsumableRarity.legendary,
                types=["all_trials", "chosen_area"],
            ),
        ]
        for cons in consumables:
            cons.types.append("default")  # This is also inherited by conditionals
        return consumables

    @cached_property
    def consumables_str(self) -> list[str]:
        consumables_list: list[Consumable] = []

        def cons_allowed(cons: Consumable) -> bool:
            """
            Checks that the consumable is allowed to appear in the game according to the `consumables_min_rarity`, `consumables_max_rarity` and `consumables_banned_types` options.

            Args:
                cons (Consumable): The consumable to check.

            Returns:
                bool: Whether the consumable is allowed to appear in the game.
            """
            return (
                cons.rarity.value
                >= self.archipelago_options.consumables_min_rarity.value
                and cons.rarity.value
                <= self.archipelago_options.consumables_max_rarity.value
                and not any(
                    [
                        t in cons.types
                        for t in self.archipelago_options.consumables_banned_types.value
                    ]
                )
            )

        for cons in self.consumables:
            if not cons_allowed(cons):
                continue
            consumables_list.append(cons)
            if cons.conditionals is None:
                continue
            # Conditionals are converted into separate consumables
            for cond in cons.conditionals:
                cond_cons: Consumable = Consumable(
                    name=cond.name,
                    description=f"{cond.condition}, {cons.description[0].lower()}{cons.description[1:]}",
                    inspiration=cond.inspiration,
                    rarity=cons.rarity if cond.rarity is None else cond.rarity,
                    types=[*cons.types, *cond.types],
                    creators=cond.creators or cons.creators,
                )
                if cons_allowed(cond_cons):
                    consumables_list.append(cond_cons)
        # Load custom consumables from option
        ccons_parsed: list[dict[str, Any]] = Utils.parse_yaml(
            self.archipelago_options.consumables_custom_consumables.value
        )
        if not isinstance(ccons_parsed, list):
            raise TypeError("Custom consumables is not a list")
        for index, ccons in enumerate(ccons_parsed):
            if not isinstance(ccons, dict):
                raise TypeError(
                    f"Custom consumable #{index + 1} is not a dictionary: {ccons!r}"
                )
            if "name" not in ccons or not isinstance(ccons["name"], str):
                raise TypeError(
                    f"Custom consumable #{index + 1} has no name or name is not a string: {ccons!r}"
                )
            if "description" not in ccons or not isinstance(ccons["description"], str):
                raise TypeError(
                    f"Custom consumable #{index + 1} has no description or description is not a string: {ccons!r}"
                )
            if "rarity" not in ccons or (
                not isinstance(ccons["rarity"], str)
                and not isinstance(ccons["rarity"], int)
            ):
                raise TypeError(
                    f"Custom consumable #{index + 1} has no rarity or rarity is not a string or integer: {ccons!r}"
                )
            if (
                "types" not in ccons
                or not isinstance(ccons["types"], list)
                or not all(isinstance(t, str) for t in ccons["types"])
            ):
                raise TypeError(
                    f"Custom consumable #{index + 1} has no types or types is not a list of strings: {ccons!r}"
                )
            if (
                "creators" not in ccons
                or not isinstance(ccons["creators"], list)
                or not all(isinstance(c, str) for c in ccons["creators"])
            ):
                raise TypeError(
                    f"Custom consumable #{index + 1} has no creators or creators is not a list of strings: {ccons!r}"
                )
            rarity: ConsumableRarity
            if isinstance(ccons["rarity"], str):
                try:
                    rarity = ConsumableRarity(
                        next(
                            c.value
                            for c in ConsumableRarity
                            if c.name == ccons["rarity"]
                        )
                    )
                except StopIteration:
                    raise ValueError(
                        f"Custom consumable #{index + 1} has an invalid rarity: {ccons!r}"
                    )
            else:  # int
                rarity = ConsumableRarity(ccons["rarity"])
            ccons_cons: Consumable = Consumable(
                name=ccons["name"],
                description=ccons["description"],
                rarity=rarity,
                types=ccons["types"],
                creators=ccons["creators"],
            )
            if cons_allowed(ccons_cons):
                consumables_list.append(ccons_cons)
        # Convert consumables to strings
        consumable_strs: list[str] = []
        for consumable in consumables_list:
            """
            The weight of a consumable is calculated as an exponential curve based on the highest rarity, and it is inserted into the list that many times. Currently, the lowest rarity covers 3/4 of all possible consumables, the next lowest 3/4 of the remainder and so on, with each consumable belonging to the highest rarity only appearing once. Note that this causes minor slowdown with a max rarity of 6, so the base of pow() should not be increased beyond 4, and may need to decrease in the unlikely event that another rarity is added.
            """
            weight: int = pow(4, MAX_RARITY - consumable.rarity.value)
            for _ in range(weight):
                consumable_strs.append(
                    consumable.__str__(
                        show_rarity=bool(
                            self.archipelago_options.consumables_show_rarities.value
                        ),
                        show_name=bool(
                            self.archipelago_options.consumables_show_names.value
                        ),
                        show_creators=bool(
                            self.archipelago_options.consumables_show_creators.value
                        ),
                    )
                )
        return consumable_strs

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="CONSUMABLE",
                data={"CONSUMABLE": (self.consumables_str, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=1,
            )
        ]

    def optional_game_constraint_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="No effect if completed by others or on Keymaster's Challenge Chamber",
                data={},
            )
        ]


if __name__ == "__main__":
    """
    The main script, run when executing `python -m keymasters_keep.consumables` in the project root. Sorts all consumables by rarity and prints them to the console using pandas.
    """
    import pandas

    consumables: list[Consumable] = ConsumablesGame().consumables
    consumables_df: pandas.DataFrame = pandas.DataFrame(
        {
            "Name": [c.name for c in consumables],
            "Description": [c.description for c in consumables],
            "Rarity": [c.rarity.value for c in consumables],
        }
    )
    for cons in consumables:
        if cons.conditionals is None:
            continue
        consumables_df = pandas.concat(
            [
                consumables_df,
                pandas.DataFrame(
                    {
                        "Name": [c.name for c in cons.conditionals],
                        "Description": [
                            f"{c.condition}, {cons.description[0].lower()}{cons.description[1:]}"
                            for c in cons.conditionals
                        ],
                        "Rarity": [
                            cons.rarity.value if c.rarity is None else c.rarity.value
                            for c in cons.conditionals
                        ],
                    }
                ),
            ]
        )
    consumables_df.sort_values(by=["Rarity", "Description"], inplace=True)
    pandas.set_option("display.max_colwidth", None)
    pandas.set_option("display.max_rows", None)
    print(consumables_df)
