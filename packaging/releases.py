from datetime import datetime
from git import Repo

from packaging.version import Version


def get_releases():
    repo = Repo('.')
    releases = []

    for tag in repo.tags:
        ver = tag.path.split("/")[-1]

        if "-" in ver:
            continue

        t = tag.commit.committed_date
        dt = datetime.utcfromtimestamp(t).date()

        releases.append({
            'version': ver,
            'date': dt.isoformat()
        })

    releases.sort(key=lambda x: Version(x['version']), reverse=True)
    return releases
