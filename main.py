import argparse
import glob
import json
import os
import re
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from textwrap import dedent

import x2py

CONTENT = Path(os.getenv("XCOM2CONTENTPATH"))


def guess_title(template):
    for attr in [
        "DisplayName",
        "FriendlyName",
    ]:
        candidate = getattr(template, attr, None)
        if candidate:
            return candidate


def guess_soldier_class_title(template):
    return f"{template.DisplayName or template.DataName}{' (Multiplayer)' if template.bMultiplayerOnly else ''}"


def recurse_classes(args, x2, uclass):
    classname = uclass.__name__.casefold()

    for child in uclass.__subclasses__():
        recurse_classes(args, x2, child)

    if args.templates:
        for arg in args.templates:
            if arg.casefold() == classname:
                break
            with suppress(TypeError):
                if re.match(rf"x2{arg}template", classname, re.IGNORECASE):
                    break
        else:
            return

    layout = (
        classname if Path(f"_layouts/{classname}.html").exists() else "x2datatemplate"
    )
    with open(Path(f"_wotc/{classname}.html"), "w") as file:
        file.write(
            dedent(
                f"""\
                ---
                title: {classname}
                flavor: wotc
                UClass: {classname}
                layout: {layout}
                permalink: /wotc/{classname}
                ---
                """
            )
        )

    layout = (
        f"{classname}_"
        if Path(f"_layouts/{classname}_.html").exists()
        else "x2datatemplate_"
    )

    for dataname, template in uclass.instances.items():
        with open(Path(f"_wotc/") / f"{classname}_{dataname}.html", "w") as file:
            file.write(
                dedent(
                    f"""\
                    ---
                    title: \"{template.guess_title() or dataname}\"
                    flavor: wotc
                    UClass: {classname}
                    DataName: {dataname}
                    layout: {layout}
                    permalink: /wotc/{classname}/{dataname}
                    ---
                    """
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--templates", nargs="+", required=False)

    args = parser.parse_args()

    x2 = x2py.X2(CONTENT, CONTENT)
    Path("_data").mkdir(exist_ok=True)
    with open("_data/wotc.json", "w") as file:
        x2.dump(file, html=True)

    x2.X2DataTemplate.guess_title = guess_title

    # fmt: off
    x2.X2AbilityPointTemplate.guess_title = (
        lambda template: template.ActionFriendlyName[:1].upper()
        + template.ActionFriendlyName[1:]
    )
    x2.X2AbilityTemplate.guess_title = lambda template: template.LocFriendlyName
    x2.X2AdventChosenTemplate.guess_title = lambda template: template.ChosenTitleWithArticle
    x2.X2CharacterTemplate.guess_title = lambda template: template.strCharacterName
    x2.X2CovertActionTemplate.guess_title = lambda template: template.ActionObjective
    x2.X2CovertActionRiskTemplate.guess_title = lambda template: template.RiskName
    x2.X2CovertActionNarrativeTemplate.guess_title = lambda template: template.ActionName
    x2.X2EncyclopediaTemplate.guess_title = lambda template: template.ListTitle or template.DescriptionTitle
    x2.X2LadderUpgradeTemplate.guess_title = lambda template: template.ShortDescription
    x2.X2MissionSourceTemplate.guess_title = lambda template: template.MissionPinLabel or template.BattleOpName
    x2.X2ObjectiveTemplate.guess_title = lambda template: template.Title
    x2.X2MPCharacterTemplate.guess_title = lambda template: template.DisplayName + " (Multiplayer)"
    x2.X2PointOfInterestTemplate.guess_title = lambda template: ", ".join(
        [
            x2.X2RewardTemplate.instances[reward.casefold()].guess_title()
            for reward in template.RewardTypes
        ]
    )
    x2.X2ResistanceFactionTemplate.guess_title = lambda template: template.FactionTitle
    x2.X2ResistanceActivityTemplate.guess_title = lambda template: template.DisplayName.strip().rstrip(":")
    x2.X2SoldierClassTemplate.guess_title = guess_soldier_class_title
    x2.X2SpecialRoomFeatureTemplate.guess_title = lambda template: template.UnclearedDisplayName
    x2.X2StaffSlotTemplate.guess_title = lambda template: template.BonusEmptyText.strip().rstrip(".")
    x2.X2TraitTemplate.guess_title = lambda template: template.TraitFriendlyName
    # fmt: on

    img = {}
    for fname in glob.glob("content/**", recursive=True):
        if Path(fname).is_file():
            img[fname.casefold().replace("\\", "/")] = fname.replace("\\", "/")
    with open("_data/img.json", "w") as file:
        json.dump(img, file)

    Path("_wotc").mkdir(exist_ok=True)
    with open(Path(f"_wotc/index.html"), "w") as file:
        file.write(
            dedent(
                """\
                ---
                title: War of the Chosen
                layout: index
                flavor: wotc
                ---
                """
            )
        )

    Path("_wotc").mkdir(exist_ok=True)

    recurse_classes(args, x2, x2.X2DataTemplate)
