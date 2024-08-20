import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from typing import Any
from packaging.version import Version

from jinja2 import Environment, select_autoescape
from jinja2 import FileSystemLoader

from blackboard_sync import (
    __id__,
    __title__,
    __summary__,
    __uri__,
    __homepage__,
    __author__,
    __email__,
    __publisher__,
    __license__,
    __license_spdx__,
    __copyright__
)

from releases import get_releases


def get_version_base(version: str) -> str:
    v = Version(version)
    return v.base_version


def replace_templates(template_files, context, outdir) -> int:
    folders = ["packaging/windows", "packaging/macos", "packaging/linux"]

    env = Environment(
        loader=FileSystemLoader(folders),
        autoescape=select_autoescape()
    )

    for filename in template_files:
        template = env.get_template(filename)

        outfile = f"{outdir}/{filename}"
        template.stream(**context).dump(outfile)

    return 0


def main(argv: list[str]) -> int:
    __version__ = argv[1]
    __version_base__ = get_version_base(__version__)

    template_files = [
        # Windows (MSIX)
        "AppXManifest.xml",
        "PackagingLayout.xml",

        # Windows
        "pkg_win.nsi",

        # macOS
        "pkg_macos.sh",

        # Linux
        "app.bbsync.BlackboardSync.desktop",
        "app.bbsync.BlackboardSync.metainfo.xml"
    ]

    context = {
        'package': __id__,
        'title':__title__,
        'version':__version__,
        'version_base': __version_base__,
        'author':__author__,
        'summary':__summary__,
        'homepage':__homepage__,
        'repository':__uri__,
        'publisher':__publisher__,
        'license':__license__,
        'license_spdx':__license_spdx__,
        'copyright':__copyright__,
        'releases':get_releases()
    }

    os.mkdir("replaced")
    replace_templates(template_files, context, "replaced")


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
