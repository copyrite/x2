import argparse
import glob
import json
import os
import re
from contextlib import suppress
from pathlib import Path

import x2py

CONTENT = Path(os.getenv("XCOM2CONTENTPATH"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--templates", nargs="+", required=False)

    args = parser.parse_args()

    x2 = x2py.X2(CONTENT, CONTENT)
    Path("_data").mkdir(exist_ok=True)
    with open("_data/wotc.json", "w") as file:
        x2.dump(file, html=True)

    img = {}
    for fname in glob.glob("content/**", recursive=True):
        if Path(fname).is_file():
            img[fname.casefold().replace("\\", "/")] = fname.replace("\\", "/")
    with open("_data/img.json", "w") as file:
        json.dump(img, file)

    Path("_wotc").mkdir(exist_ok=True)
    with open(Path(f"_wotc/index.html"), "w") as file:
        file.write(f"---\ntitle: wotc\nlayout: index\nflavor: wotc\n---\n")

    Path("_wotc").mkdir(exist_ok=True)
    for kind, manager in x2.managers.items():
        # Dev option: only generate selected types of templates
        if args.templates:
            for arg in args.templates:
                if arg.casefold() == kind.casefold():
                    break
                with suppress(TypeError):
                    if re.match(rf"x2{arg}template", kind, re.IGNORECASE):
                        break
            else:
                continue

        with open(Path(f"_wotc/{kind}.html"), "w") as file:
            manager_layout_kind = (
                kind if Path(f"_layouts/{kind}.html").exists() else "x2datatemplate"
            )
            file.write(
                f"---\ntitle: {kind}\nlayout: {manager_layout_kind}\ntemplate_type: {kind}\nflavor: wotc\npermalink: wotc/{kind}\n---\n"
            )

        template_layout_kind = (
            f"{kind}_" if Path(f"_layouts/{kind}_.html").exists() else "x2datatemplate_"
        )

        for template in manager:
            with open(Path(f"_wotc/") / f"{kind}_{template}.html", "w") as file:
                file.write(
                    f"---\ntitle: {template}\nlayout: {template_layout_kind}\ntemplate_type: {kind}\npermalink: wotc/{kind}/{template}\nflavor: wotc\n---\n"
                )
