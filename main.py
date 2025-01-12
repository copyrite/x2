import os
from pathlib import Path

import x2py

if __name__ == "__main__":
    x2 = x2py.X2(os.getenv("XCOM2CONTENTPATH"))
    Path("_data").mkdir(exist_ok=True)
    with open("_data/wotc.json", "w") as file:
        x2.dump(file, html=True)

    Path("_wotc").mkdir(exist_ok=True)
    with open(Path(f"_wotc/index.html"), "w") as file:
        file.write(f"---\ntitle: wotc\nlayout: index\nflavor: wotc\n---\n")

    Path("_wotc").mkdir(exist_ok=True)
    for kind, manager in x2.managers.items():

        with open(Path(f"_wotc/x2{kind}templatemanager.html"), "w") as file:
            layout_kind = (
                kind
                if Path(f"_layouts/x2{kind}templatemanager.html").exists()
                else "data"
            )
            file.write(
                f"---\ntitle: {kind}\nlayout: x2{layout_kind}templatemanager\nflavor: wotc\npermalink: wotc/{kind}\n---\n"
            )

        for template in manager:
            with open(
                Path(f"_wotc/") / f"{template}_x2{kind}template.html", "w"
            ) as file:
                file.write(
                    f"---\ntitle: {template}\nlayout: x2datatemplate\ntemplate_type: {kind}\npermalink: wotc/{kind}/{template}\nflavor: wotc\n---\n"
                )
