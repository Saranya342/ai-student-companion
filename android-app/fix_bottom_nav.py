import os

BASE = r"C:\Users\saranya\Downloads\ai-student-companion\android-app\app\src\main"

# ─────────────────────────────────────────────
# 1) view_bottom_nav.xml
# ─────────────────────────────────────────────
view_bottom_nav = '''<com.google.android.material.bottomnavigation.BottomNavigationView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/bottomNav"
    android:layout_width="match_parent"
    android:layout_height="72dp"
    android:background="#1A1A1A"
    app:menu="@menu/menu_bottom_nav"
    app:labelVisibilityMode="labeled"
    app:itemIconSize="24dp"
    app:itemIconTint="@color/bottom_nav_item_colors"
    app:itemTextColor="@color/bottom_nav_item_colors"/>
'''
path = os.path.join(BASE, "res", "layout", "view_bottom_nav.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(view_bottom_nav)
print("DONE: view_bottom_nav.xml")

# ─────────────────────────────────────────────
# 2) menu_bottom_nav.xml
# ─────────────────────────────────────────────
menu_bottom_nav = '''<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/nav_chat"
        android:icon="@drawable/ic_nav_chat"
        android:title="Chat" />
    <item
        android:id="@+id/nav_planner"
        android:icon="@drawable/ic_nav_planner"
        android:title="Planner" />
    <item
        android:id="@+id/nav_bag"
        android:icon="@drawable/ic_nav_bag"
        android:title="Bag" />
    <item
        android:id="@+id/nav_memories"
        android:icon="@drawable/ic_nav_journal"
        android:title="Memories" />
    <item
        android:id="@+id/nav_profile"
        android:icon="@drawable/ic_nav_profile"
        android:title="Profile" />
</menu>
'''
menu_dir = os.path.join(BASE, "res", "menu")
os.makedirs(menu_dir, exist_ok=True)
path = os.path.join(menu_dir, "menu_bottom_nav.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(menu_bottom_nav)
print("DONE: menu_bottom_nav.xml")

# ─────────────────────────────────────────────
# 3) bottom_nav_item_colors.xml
# ─────────────────────────────────────────────
color_xml = '''<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:color="#B388FF" android:state_checked="true"/>
    <item android:color="#555555"/>
</selector>
'''
color_dir = os.path.join(BASE, "res", "color")
os.makedirs(color_dir, exist_ok=True)
path = os.path.join(color_dir, "bottom_nav_item_colors.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(color_xml)
print("DONE: bottom_nav_item_colors.xml")

# ─────────────────────────────────────────────
# 4) Rewrite ALL 5 layout XML files
#    Replace the old bottom LinearLayout with <include layout="@layout/view_bottom_nav"/>
# ─────────────────────────────────────────────
import re

layout_dir = os.path.join(BASE, "res", "layout")

def fix_layout(filename):
    path = os.path.join(layout_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the bottom nav LinearLayout block
    # It starts with a LinearLayout containing navChat TextView children
    # We find the last big LinearLayout that contains nav items
    pattern = re.compile(
        r'(\s*<!--\s*Bottom Navigation\s*-->\s*)?'
        r'<LinearLayout[^>]*android:layout_height="72dp"[^>]*>.*?</LinearLayout>',
        re.DOTALL
    )

    new_content, count = pattern.subn(
        '\n    <include layout="@layout/view_bottom_nav"/>\n',
        content
    )

    if count == 0:
        # fallback: try matching by navChat presence
        pattern2 = re.compile(
            r'<LinearLayout[^>]*>(?:[^<]|<(?!LinearLayout))*?'
            r'android:id="@\+id/navChat".*?</LinearLayout>',
            re.DOTALL
        )
        new_content, count = pattern2.subn(
            '\n    <include layout="@layout/view_bottom_nav"/>\n',
            content
        )

    if count > 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"DONE layout: {filename} (replaced {count} block)")
    else:
        print(f"WARNING: Could not auto-replace in {filename} - do it manually")

fix_layout("activity_home.xml")
fix_layout("activity_bag.xml")
fix_layout("activity_planner.xml")
fix_layout("activity_memories.xml")
fix_layout("activity_profile.xml")

# ─────────────────────────────────────────────
# 5) Rewrite ALL 5 Activity Java files
#    - Remove old nav TextViews + findViewByIds + setOnClickListeners
#    - Add BottomNavigationView block
# ─────────────────────────────────────────────

java_dir = os.path.join(BASE, "java", "com", "mindmate", "app")

NAV_IMPORT = "import com.google.android.material.bottomnavigation.BottomNavigationView;\n"

def nav_block(selected, items):
    lines = []
    lines.append("        // ── Bottom Navigation ──")
    lines.append("        BottomNavigationView bottomNav = findViewById(R.id.bottomNav);")
    lines.append(f"        bottomNav.setSelectedItemId(R.id.{selected});")
    lines.append("        bottomNav.setOnItemSelectedListener(item -> {")
    lines.append("            int id = item.getItemId();")
    lines.append(f"            if (id == R.id.{selected}) return true;")
    for nav_id, activity in items:
        lines.append(f"            else if (id == R.id.{nav_id}) startActivity(new Intent(this, {activity}.class));")
    lines.append("            finish();")
    lines.append("            return true;")
    lines.append("        });")
    return "\n".join(lines)

activities = {
    "HomeActivity.java": {
        "selected": "nav_chat",
        "others": [
            ("nav_planner", "PlannerActivity"),
            ("nav_bag", "BagActivity"),
            ("nav_memories", "MemoriesActivity"),
            ("nav_profile", "ProfileActivity"),
        ]
    },
    "BagActivity.java": {
        "selected": "nav_bag",
        "others": [
            ("nav_chat", "HomeActivity"),
            ("nav_planner", "PlannerActivity"),
            ("nav_memories", "MemoriesActivity"),
            ("nav_profile", "ProfileActivity"),
        ]
    },
    "PlannerActivity.java": {
        "selected": "nav_planner",
        "others": [
            ("nav_chat", "HomeActivity"),
            ("nav_bag", "BagActivity"),
            ("nav_memories", "MemoriesActivity"),
            ("nav_profile", "ProfileActivity"),
        ]
    },
    "MemoriesActivity.java": {
        "selected": "nav_memories",
        "others": [
            ("nav_chat", "HomeActivity"),
            ("nav_planner", "PlannerActivity"),
            ("nav_bag", "BagActivity"),
            ("nav_profile", "ProfileActivity"),
        ]
    },
    "ProfileActivity.java": {
        "selected": "nav_profile",
        "others": [
            ("nav_chat", "HomeActivity"),
            ("nav_planner", "PlannerActivity"),
            ("nav_bag", "BagActivity"),
            ("nav_memories", "MemoriesActivity"),
        ]
    },
}

# Old nav variables to remove
OLD_NAV_VARS = [
    "TextView navChat",
    "TextView navPlanner",
    "TextView navBag",
    "TextView navMemories",
    "TextView navProfile",
]

OLD_NAV_FINDVIEWS = [
    "navChat = findViewById",
    "navPlanner = findViewById",
    "navBag = findViewById",
    "navMemories = findViewById",
    "navProfile = findViewById",
]

for filename, config in activities.items():
    path = os.path.join(java_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add import if missing
    if "BottomNavigationView" not in content:
        content = content.replace(
            "import com.mindmate.app.network.ApiClient;",
            "import com.google.android.material.bottomnavigation.BottomNavigationView;\nimport com.mindmate.app.network.ApiClient;"
        )

    # Remove old nav field declarations (class-level)
    for var in OLD_NAV_VARS:
        content = re.sub(r'\s*' + re.escape(var) + r'[^;]*;', '', content)

    # Remove old nav findViewByIds
    for fv in OLD_NAV_FINDVIEWS:
        content = re.sub(r'\s*' + re.escape(fv) + r'[^;]*;', '', content)

    # Remove old nav setOnClickListeners blocks
    # They look like: navChat.setOnClickListener(v -> { ... });
    content = re.sub(
        r'\s*nav(?:Chat|Planner|Bag|Memories|Profile)\.setOnClickListener\(.*?\}\);',
        '',
        content,
        flags=re.DOTALL
    )

    # Add BottomNavigationView block before last closing brace of onCreate
    nav_code = "\n" + nav_block(config["selected"], config["others"]) + "\n"

    # Insert before the last } of onCreate
    # Find onCreate closing brace
    oncreate_match = re.search(r'(protected void onCreate.*?)\n(\s*\})', content, re.DOTALL)
    if oncreate_match and "bottomNav" not in content:
        insert_pos = oncreate_match.end(1)
        content = content[:insert_pos] + nav_code + content[insert_pos:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"DONE activity: {filename}")

print("\n✅ ALL DONE. Now build in Android Studio.")