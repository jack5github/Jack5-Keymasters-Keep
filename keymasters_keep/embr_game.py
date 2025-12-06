from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from Options import OptionCounter  # pyright: ignore[reportMissingImports]
from ..enums import KeymastersKeepGamePlatforms  # pyright: ignore[reportMissingImports]
from ..game import Game  # pyright: ignore[reportMissingImports]
from ..game_objective_template import (  # pyright: ignore[reportMissingImports]
    GameObjectiveTemplate,
)


class EmbrWeights(OptionCounter):
    """
    The weights to use for Embr objective types. Note that "embrgigs", "goals" and one-fifth of "bonus" are classified as difficult and time consuming, and will not appear if difficult or time consuming objectives are disabled.
    """

    display_name: str = "Embr Weights"
    default: dict[str, int] = {
        "rescue_on_neighbourhood": 1,
        "rescue_on_neighbourhood_all_clients": 1,
        "mission_on_neighbourhood": 3,
        "escape": 1,
        "boss": 2,
        "cash_on_neighbourhood": 1,
        "cash_on_escape": 1,
        "mission_with_loadout": 2,
        "mission_with_gear": 2,
        "embrgigs": 2,
        "goals": 2,
        "bonus": 5,
    }


class EmbrMissionWeights(OptionCounter):
    """
    The weights to use for mission types in Embr objectives that use them (`mission_on_neighbourhood` (excludes "Rescue Mission"), `mission_with_loadout` and `mission_with_gear`).
    """

    display_name: str = "Embr Mission Weights"
    default: dict[str, int] = {
        "Rescue Mission": 1,
        "Salvage": 1,
        "Low House Damage": 1,
        "Special Object": 1,
        "Embr Eats": 1,
        "Demolition": 1,
    }


class EmbrNeighbourhoodWeights(OptionCounter):
    """
    The weights to use for neighbourhoods in Embr objectives. Note that "Wayside Way" and all neighbourhoods outside of the "Bedbugstuy" district are classified as difficult, and will not appear if difficult objectives are disabled.
    """

    display_name: str = "Embr Neighbourhood Weights"
    default: dict[str, int] = {
        "First Ave": 1,
        "Oscar Heights": 1,
        "Crab n' Go": 1,
        "Utica Ave": 1,
        "St. John St.": 1,
        "Canal St": 1,
        "Dent Memorial Bypass": 1,
        "Empire Towers": 1,
        "Wayside Way": 1,
        "Newton Avenue": 1,
        "Douglas St.": 1,
        "YouWork Office": 1,
        "Schuldenberg Bank": 1,
        "Defender Headquarters": 1,
        "Hypertube Experimental Offices": 1,
        "Mystery Manors": 1,
        "Yachtster Rent-a-Yacht": 1,
        "Crab and Go: Claw Club": 1,
        "Rockside Resort": 1,
        "Whitehall Municipal LLC": 1,
        "Hotel Construction Site": 1,
        "Barrel Factory": 1,
        "Embr Satellite Office": 1,
        "Maple St. Warehouse": 1,
        "Fyre HQ": 1,
        "Mystery Signal from Embr HQ": 1,
    }


@dataclass
class EmbrArchipelagoOptions:
    embr_weights: EmbrWeights
    embr_mission_weights: EmbrMissionWeights
    embr_neighbourhood_weights: EmbrNeighbourhoodWeights


class EmbrGame(Game):
    name: str = "Embr"
    platform: KeymastersKeepGamePlatforms = KeymastersKeepGamePlatforms.PC
    platforms_other: list[KeymastersKeepGamePlatforms] = [
        KeymastersKeepGamePlatforms.PS4,  # Sony PlayStation 4
        KeymastersKeepGamePlatforms.SW,  # Nintendo Switch
        KeymastersKeepGamePlatforms.XONE,  # Microsoft Xbox One
    ]
    is_adult_only_or_unrated: bool = False
    options_cls: type[EmbrArchipelagoOptions] = EmbrArchipelagoOptions

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

    @cached_property
    def special_missions_list(self) -> list[str]:
        return [
            "Salvage",
            "Low House Damage",
            "Special Object",
            "Embr Eats",
            "Demolition",
        ]

    def special_missions(self) -> list[str]:
        return self._get_weighted_items(
            self.special_missions_list, self.archipelago_options.embr_mission_weights
        )

    def loadout_missions(self) -> list[str]:
        return self._get_weighted_items(
            list(EmbrMissionWeights.default.keys()),
            self.archipelago_options.embr_mission_weights,
        )

    @cached_property
    def neighbourhoods_base_list(self) -> list[str]:
        return [
            "First Ave",
            "Oscar Heights",
            "Crab n' Go",
            "Utica Ave",
            "St. John St.",
            "Canal St",
            "Dent Memorial Bypass",
            "Empire Towers",
        ]

    def neighbourhoods_base(self) -> list[str]:
        return self._get_weighted_items(
            self.neighbourhoods_base_list,
            self.archipelago_options.embr_neighbourhood_weights,
        )

    @cached_property
    def neighbourhoods_difficult_list(self) -> list[str]:
        # The game becomes exponentially more difficult from the Prospect Flats district onwards, as this is where security access keys are introduced
        # The lone exception is Wayside Way, in which the fire is near-impossible to put out
        return [
            "Wayside Way",
            "Newton Avenue",
            "Douglas St.",
            "YouWork Office",
            "Schuldenberg Bank",
            "Defender Headquarters",
            "Hypertube Experimental Offices",
            "Mystery Manors",
            "Yachtster Rent-a-Yacht",
            "Crab and Go: Claw Club",
            "Rockside Resort",
            "Whitehall Municipal LLC",
        ]

    def neighbourhoods_difficult(self) -> list[str]:
        return self._get_weighted_items(
            self.neighbourhoods_difficult_list,
            self.archipelago_options.embr_neighbourhood_weights,
        )

    @cached_property
    def neighbourhoods_escape_list(self) -> list[str]:
        return ["Hotel Construction Site", "Barrel Factory", "Embr Satellite Office"]

    def neighbourhoods_escape(self) -> list[str]:
        return self._get_weighted_items(
            self.neighbourhoods_escape_list,
            self.archipelago_options.embr_neighbourhood_weights,
        )

    @cached_property
    def neighbourhoods_boss_list(self) -> list[str]:
        return ["Maple St. Warehouse", "Fyre HQ", "Mystery Signal from Embr HQ"]

    def neighbourhoods_boss(self) -> list[str]:
        return self._get_weighted_items(
            self.neighbourhoods_boss_list,
            self.archipelago_options.embr_neighbourhood_weights,
        )

    @staticmethod
    def embrgigs() -> list[str]:
        return ["Mutator Challenge", "GasLight Inc.", "BoxBox"]

    @staticmethod
    def goals() -> list[str]:
        return ["Daily Goal 1", "Daily Goal 2", "Weekly Goal"]

    @staticmethod
    def extinguishers() -> list[str]:
        return ["Basic Hose", "Fire Extinguisher", "Ice Acceleratr", "Sprinkler"]

    @staticmethod
    def entries() -> list[str]:
        return ["Fire Axe", "Breaching Charge", "Throwing Axe"]

    @staticmethod
    def ascenders() -> list[str]:
        return [
            "Grappling Hook",
            "Jump Pad",
            "Collapsible Ladder",
            "Parachute Pack",
            "Trampoline",
        ]

    @staticmethod
    def miscs() -> list[str]:
        return [
            "Hair Dryer",
            "Headling Needle",
            "Cheap Metal Box",
            "Slippery Slide",
            "Client Findr",
        ]

    @staticmethod
    def grenades() -> list[str]:
        return [
            "EMP Grenade",
            "Stim Pen",
            "Deployable Toilet",
            "Vacuum Grenade",
            "Water Grenade",
        ]

    @staticmethod
    def heads() -> list[str]:
        return [
            "Appbulance Headgear",
            "Baseball Cap",
            "Boxing Helmet",
            "Cowboy Hat",
            "Crash Helmet",
            "Dummy Helmet",
            "Embr Eats Cap",
            "Firefighting Helmet",
            "Football Helmet",
            "Hard Hat",
            "Hazmat Headgear",
            "Mechanic Helmet",
            "Motorcycle Helmet",
            "Pajama Cap",
            "Gourd Guardian",
            "Reindeer Cap",
            "Scuba Mask",
            "Defendr Tech Helmet",
        ]

    @staticmethod
    def bodies() -> list[str]:
        return [
            "Hazmat Bodysuit",
            "Leather Jacket",
            "Mechanic Suit",
            "Pajama Top",
            "Red Plaid Shirt",
            "Defendr Technician Suit",
            "Wastemates Shirt",
        ]

    @staticmethod
    def gloves() -> list[str]:
        return [
            "Cowboy Gloves",
            "Embr Eats Gloves",
            "Firefighting Gloves",
            "Hazmat Gloves",
            "Mechanic Gloves",
            "Pajama Gloves",
            "Defendr Tech Gloves",
        ]

    @staticmethod
    def pants() -> list[str]:
        return [
            "Cowboy Pants",
            "Elf Pants",
            "Firefighter Pants",
            "Hazmat Pants",
            "Mechanic Pants",
            "Pajama Pants",
            "Defendr Tech Trousers",
            "Wastemates Pants",
        ]

    @staticmethod
    def bonus_objectives_base() -> list[str]:
        return [
            "Abandon a job",
            "Allow a client to die",
            "Bounce on 2 Jump Pads without touching the ground",
            "Break a floorboard",
            "Buy something from the Embr Shop",
            "Change the upgrades of a tool",
            "Change your character (profile image)",
            "Create a new loadout",
            "Destroy an explosive with a Fire Axe",
            "Destroy an explosive with a Throwing Axe",
            "Drop from a great height while holding a client with the Cowboy Gloves",
            "Extinguish an unreachable fire with a Fire Extinguisher",
            "Heal a player with a Healing Needle",
            "Hypnotise a client with a Deployable Toilet",
            "Kill a client",
            "Land on a Trampoline from a great height",
            "Let a neighbourhood burn down",
            "Lose all your health",
            "Lose all your water",
            "Open a safe",
            "Play Secret HOSR with 3 other players",
            "Put something in your Salvage Zone",
            "Rescue a player that has no health",
            "Slide down a Slippery Slide",
            "Stand still and watch a raging fire",
            "Use a Cheap Metal Box",
            "Use a Vacuum Grenade",
            "Use an EMP Grenade on an electrical outlet",
        ]

    @staticmethod
    def bonus_objectives_difficult() -> list[str]:
        return [
            "Be pushed by a giant fan",
            "Collect a total of 20 security access keys",
            "Get crushed by giant pistons",
            "Play a mission with security cameras without being seen",
            "Play a mission with tripwires without triggering them",
            "Trigger a fire shooter",
        ]

    @staticmethod
    def constraints() -> list[str]:
        return [
            "Always have 4 players in the lobby",
            "Do not jump",
            "Do not look at Client Findr",
            "Use no more than 4 tools and a grenade at once",
            "Use only needed upgrades",
            "Wear gear with downsides unless instructed otherwise",
        ]

    def game_objective_templates(self) -> list[GameObjectiveTemplate]:
        weights: dict[str, int] = self.archipelago_options.embr_weights.value
        factor: int = 100
        return [
            GameObjectiveTemplate(
                label="Beat Rescue Mission on NEIGHBOURHOOD",
                data={"NEIGHBOURHOOD": (self.neighbourhoods_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["rescue_on_neighbourhood"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Beat Rescue Mission on NEIGHBOURHOOD",
                data={"NEIGHBOURHOOD": (self.neighbourhoods_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["rescue_on_neighbourhood"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Rescue all clients on NEIGHBOURHOOD",
                data={"NEIGHBOURHOOD": (self.neighbourhoods_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["rescue_on_neighbourhood_all_clients"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Rescue all clients on NEIGHBOURHOOD",
                data={"NEIGHBOURHOOD": (self.neighbourhoods_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["rescue_on_neighbourhood_all_clients"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Beat MISSION on NEIGHBOURHOOD",
                data={
                    "MISSION": (self.special_missions, 1),
                    "NEIGHBOURHOOD": (self.neighbourhoods_base, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["mission_on_neighbourhood"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Beat MISSION on NEIGHBOURHOOD",
                data={
                    "MISSION": (self.special_missions, 1),
                    "NEIGHBOURHOOD": (self.neighbourhoods_difficult, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["mission_on_neighbourhood"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Escape ESCAPE",
                data={"ESCAPE": (self.neighbourhoods_escape, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["escape"] * factor,
            ),
            GameObjectiveTemplate(
                label="Defeat boss on BOSS",
                data={"BOSS": (self.neighbourhoods_boss, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["boss"] * factor,
            ),
            GameObjectiveTemplate(
                label="Find all bonus cash on NEIGHBOURHOOD",
                data={"NEIGHBOURHOOD": (self.neighbourhoods_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["cash_on_neighbourhood"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Find all bonus cash on NEIGHBOURHOOD",
                data={"NEIGHBOURHOOD": (self.neighbourhoods_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["cash_on_neighbourhood"] * factor / 2),
            ),
            GameObjectiveTemplate(
                label="Find all cash bags on ESCAPE",
                data={"ESCAPE": (self.neighbourhoods_escape, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["cash_on_escape"] * factor,
            ),
            GameObjectiveTemplate(
                label="Beat MISSION with loadout EXTINGUISHER, ENTRY, ASCENDER, MISC & GRENADE",
                data={
                    "MISSION": (self.loadout_missions, 1),
                    "EXTINGUISHER": (self.extinguishers, 1),
                    "ENTRY": (self.entries, 1),
                    "ASCENDER": (self.ascenders, 1),
                    "MISC": (self.miscs, 1),
                    "GRENADE": (self.grenades, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["mission_with_loadout"] * factor,
            ),
            GameObjectiveTemplate(
                label="Beat MISSION with gear HEAD, BODY, GLOVES & PANTS",
                data={
                    "MISSION": (self.loadout_missions, 1),
                    "HEAD": (self.heads, 1),
                    "BODY": (self.bodies, 1),
                    "GLOVES": (self.gloves, 1),
                    "PANTS": (self.pants, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=weights["mission_with_gear"] * factor,
            ),
            GameObjectiveTemplate(
                label=f"Fulfil EMBRGIG EmbrGig",
                data={"EMBRGIG": (self.embrgigs, 1)},
                # Time consuming due to requiring visiting three neighbourhoods
                is_time_consuming=True,
                # Difficult due to difficult neighbourhoods possibly appearing
                is_difficult=True,
                weight=weights["embrgigs"] * factor,
            ),
            GameObjectiveTemplate(
                label="Complete GOAL",
                data={"GOAL": (self.goals, 1)},
                # One of the possible types of goals is to complete an EmbrGig
                # Since EmbrGigs are time consuming and difficult, goals must also be
                is_time_consuming=True,
                is_difficult=True,
                weight=weights["goals"] * factor,
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_base, 1)},
                is_time_consuming=False,
                is_difficult=False,
                weight=int(weights["bonus"] * factor * 0.8),
            ),
            GameObjectiveTemplate(
                label="BONUS",
                data={"BONUS": (self.bonus_objectives_difficult, 1)},
                is_time_consuming=False,
                is_difficult=True,
                weight=int(weights["bonus"] * factor * 0.2),
            ),
        ]

    def optional_game_constraint_templates(self) -> list[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="CONSTRAINT", data={"CONSTRAINT": (self.constraints, 1)}
            )
        ]
