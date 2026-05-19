"""
Script that uses Playwright to scrape Tomodachi Life: Living the Dream items from https://animalcrossingworld.com/tomodachi-life and writes over the regions in `keymasters_keep/tomodachi_life_living_the_dream_game.py` accordingly.
"""

if __name__ == "__main__":
    from playwright.sync_api import Browser, Locator, Page, sync_playwright

    with open(f"keymasters_keep/tomodachi_life_living_the_dream_game.py", "r") as f:
        code: str = f.read()
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch()
        page: Page = browser.new_page(java_script_enabled=False)
        for region in [
            "food",
            "quirks",
            "clothing/outfits",
            "clothing/tops",
            "clothing/long-tops",
            "clothing/legwear",
            "clothing/headwear",
            "clothing/accessories",
            "clothing/socks",
            "clothing/shoes",
            "clothing/costumes",
            "objects",
            "facilities",
            "goods",
            "treasures",
            "interiors",
            "landscaping",
            "travel-destinations",
        ]:
            url: str = (
                f"https://animalcrossingworld.com/tomodachi-life/catalog/{region}"
            )
            page.goto(url, wait_until="domcontentloaded")
            cards: Locator = page.locator(
                "a[class^='CatalogCollectionPage-module'][class$='cardButton']"
            )
            items: list[tuple[str, float | None]] = []
            for card in cards.all():
                metaLoc: Locator = card.locator(
                    "span[class^='CatalogCollectionPage-module'][class$='meta']"
                )
                title: str
                cost: float | None = None
                if region != "travel-destinations":
                    titleLoc: Locator = card.locator(
                        "h2[class^='CatalogCollectionPage-module'][class$='title']"
                    )
                    title = titleLoc.inner_text()
                    if title == "[Player Name]'s treasure shop":
                        title = "Treasure shop"
                    meta: str = metaLoc.inner_text()
                    if "$" in meta:
                        try:
                            cost = float(meta.split("$")[1])
                        except ValueError:
                            raise TypeError(f"Failed to get cost of '{title}'")
                else:  # region == "travel-destinations"
                    title = metaLoc.inner_text().split("·")[0].strip()
                    if title == "Antarctica Tour":
                        continue  # Do not include, requires $5000 pocket money
                    dupe: bool = False
                    for item in items:
                        if item[0] == title:
                            dupe = True
                            break
                    if dupe:
                        continue
                items.append((title, cost))
            if region.startswith("clothing/"):
                region = region[len("clothing/") :]
            elif region == "landscaping":
                region = "landscapes"
            elif region == "travel-destinations":
                region = "tours"
            region_start: int = code.find(f"# region {region}")
            region_line_start: int = code.rfind("\n", 0, region_start)
            region_padding: str = code[region_line_start + 1 : region_start]
            region_start += len(f"# region {region}\n")
            region_end: int = code.find("# endregion", region_start)
            region_code: str = region_padding
            for item in items:
                if item[1] is None:
                    region_code += f"LTDItem({item[0]!r}),"
                else:
                    region_code += f"LTDItem({item[0]!r}, {item[1]}),"
                region_code += f"\n{region_padding}"
            code = code[:region_start] + region_code + code[region_end:]
            with open(
                f"keymasters_keep/tomodachi_life_living_the_dream_game.py", "w"
            ) as f:
                f.write(code)
