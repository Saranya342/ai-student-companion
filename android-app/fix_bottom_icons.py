from pathlib import Path
import re
import shutil

BASE = Path.cwd()

layout_dir = BASE / "app" / "src" / "main" / "res" / "layout"
drawable_dir = BASE / "app" / "src" / "main" / "res" / "drawable"
backup_dir = BASE / "backup_bottom_icons"

backup_dir.mkdir(exist_ok=True)
drawable_dir.mkdir(exist_ok=True)

ACTIVE = "#B388FF"
INACTIVE = "#777777"

icons = {
    "ic_nav_chat.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M20,2H4C2.9,2 2,2.9 2,4v18l4,-4h14c1.1,0 2,-0.9 2,-2V4C22,2.9 21.1,2 20,2zM6,9h12v2H6V9zM14,14H6v-2h8v2z"/>
</vector>
""",

    "ic_nav_planner.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M19,3h-1V1h-2v2H8V1H6v2H5C3.9,3 3,3.9 3,5v14c0,1.1 0.9,2 2,2h14c1.1,0 2,-0.9 2,-2V5C21,3.9 20.1,3 19,3zM19,19H5V9h14v10zM5,7V5h14v2H5zM7,11h5v5H7z"/>
</vector>
""",

    "ic_nav_bag.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M20,6h-4V4c0,-1.1 -0.9,-2 -2,-2h-4C8.9,2 8,2.9 8,4v2H4C2.9,6 2,6.9 2,8v11c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2V8C22,6.9 21.1,6 20,6zM10,4h4v2h-4V4zM20,19H4V8h16v11zM6,10h2v7H6zM16,10h2v7h-2z"/>
</vector>
""",

    "ic_nav_memories.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M12,17.27L18.18,21l-1.64,-7.03L22,9.24l-7.19,-0.61L12,2 9.19,8.63 2,9.24l5.46,4.73L5.82,21z"/>
</vector>
""",

    "ic_nav_profile.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M12,12c2.21,0 4,-1.79 4,-4s-1.79,-4 -4,-4 -4,1.79 -4,4 1.79,4 4,4zM12,14c-2.67,0 -8,1.34 -8,4v2h16v-2c0,-2.66 -5.33,-4 -8,-4z"/>
</vector>
"""
}

for name, content in icons.items():
    path = drawable_dir / name
    path.write_text(content, encoding="utf-8")
    print(f"Created icon: {path}")

nav_info = {
    "navChat": {
        "label": "Chat",
        "icon": "@drawable/ic_nav_chat"
    },
    "navPlanner": {
        "label": "Planner",
        "icon": "@drawable/ic_nav_planner"
    },
    "navBag": {
        "label": "Bag",
        "icon": "@drawable/ic_nav_bag"
    },
    "navMemories": {
        "label": "Memories",
        "icon": "@drawable/ic_nav_memories"
    },
    "navProfile": {
        "label": "Profile",
        "icon": "@drawable/ic_nav_profile"
    },
}

files_active_nav = {
    "activity_home.xml": "navChat",
    "activity_planner.xml": "navPlanner",
    "activity_bag.xml": "navBag",
    "activity_memories.xml": "navMemories",
    "activity_profile.xml": "navProfile",
}

def set_attr(block: str, attr: str, value: str) -> str:
    pattern = rf'android:{attr}="[^"]*"'
    replacement = f'android:{attr}="{value}"'

    if re.search(pattern, block):
        return re.sub(pattern, replacement, block)

    # Insert before self-closing />
    return block.replace("/>", f'    android:{attr}="{value}"\n        />')

def update_textview_block(block: str, nav_id: str, active_nav: str) -> str:
    info = nav_info[nav_id]
    color = ACTIVE if nav_id == active_nav else INACTIVE

    block = set_attr(block, "text", info["label"])
    block = set_attr(block, "textColor", color)
    block = set_attr(block, "textSize", "11sp")
    block = set_attr(block, "gravity", "center")
    block = set_attr(block, "drawableTop", info["icon"])
    block = set_attr(block, "drawableTint", color)
    block = set_attr(block, "drawablePadding", "3dp")

    return block

for file_name, active_nav in files_active_nav.items():
    path = layout_dir / file_name

    if not path.exists():
        print(f"SKIPPED missing file: {path}")
        continue

    backup_path = backup_dir / file_name
    shutil.copy2(path, backup_path)

    text = path.read_text(encoding="utf-8")

    # Optional safe status bar fix: if root LinearLayout does not have fitsSystemWindows, add it
    text = re.sub(
        r'(<LinearLayout\s+xmlns:android="http://schemas.android.com/apk/res/android"\s*)',
        r'\1\n    android:fitsSystemWindows="true"\n',
        text,
        count=1
    ) if 'android:fitsSystemWindows=' not in text.split(">", 1)[0] else text

    for nav_id in nav_info.keys():
        pattern = rf'<TextView\b(?=[^>]*android:id="@\+id/{nav_id}")[^>]*/>'

        def repl(match):
            return update_textview_block(match.group(0), nav_id, active_nav)

        text, count = re.subn(pattern, repl, text, count=1)

        if count == 0:
            print(f"WARNING: {nav_id} not found in {file_name}")

    path.write_text(text, encoding="utf-8")
    print(f"Updated: {path}")

print()
print("DONE ✅")
print(f"Backups saved in: {backup_dir}")
print("Now sync/rebuild Android project.")