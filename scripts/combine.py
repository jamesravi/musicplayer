# Copyright (C) 2022 James Ravindran
# SPDX-License-Identifier: GPL-3.0-or-later

import json, os
from tinydb import TinyDB
from tqdm import tqdm
from pathlib import Path

root = Path.cwd().parent / "databases"

allitems = set()
for filename in root.glob("*.json"):
    with TinyDB(filename) as db:
        for item in tqdm(db):
            item = json.dumps(dict(item), sort_keys=True)
            allitems.add(item)
allitems = sorted(map(lambda x: json.loads(x), allitems), key=lambda x: x["timestamp"])

if os.path.isfile(root / "dball.json"):
    os.remove(root / "dball.json")
dball = TinyDB(root / "dball.json")
dball.insert_multiple(allitems)
