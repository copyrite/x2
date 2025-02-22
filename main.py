import os
from pathlib import Path

import x2py

if __name__ == "__main__":
    x2 = x2py.X2(os.getenv("XCOM2CONTENTPATH"), os.getenv("XCOM2CONTENTPATH"))
    Path("_data").mkdir(exist_ok=True)
    with open("_data/wotc.json", "w") as file:
        x2.dump(file, html=True)

    Path("_wotc").mkdir(exist_ok=True)
    with open(Path(f"_wotc/index.html"), "w") as file:
        file.write(f"---\ntitle: wotc\nlayout: index\nflavor: wotc\n---\n")

    Path("_wotc").mkdir(exist_ok=True)
    for kind, manager in x2.managers.items():

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
