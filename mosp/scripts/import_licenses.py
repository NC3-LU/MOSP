#! /usr/bin/python
import json

import requests

from mosp.bootstrap import db
from mosp.models import License


def import_licenses_from_spdx():
    r = requests.get("https://spdx.org/licenses/licenses.json")
    if r.status_code == 200:
        result = json.loads(r.content)
        db.session.bulk_save_objects(
            [
                License(name=license["name"], license_id=license["licenseId"])
                for license in result["licenses"]
                if not license["isDeprecatedLicenseId"]
            ]
        )
        db.session.commit()
