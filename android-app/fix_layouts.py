import os

BASE = r"C:\Users\saranya\Downloads\ai-student-companion\android-app\app\src\main\res\layout"

INCLUDE_LINE = '    <include layout="@layout/view_bottom_nav"/>'

# ─────────────────────────────────────────────
# activity_home.xml
# ─────────────────────────────────────────────
home = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:fitsSystemWindows="true"
    android:background="#0D0D0D">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp"
        android:gravity="center_vertical"
        android:background="#1A1A1A">

        <ImageView
            android:layout_width="44dp"
            android:layout_height="44dp"
            android:src="@drawable/robot"
            android:scaleType="centerCrop"
            android:background="@drawable/circle_purple"
            android:padding="4dp"
            android:layout_marginEnd="12dp"/>

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="vertical">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Study Buddy"
                android:textColor="#FFFFFF"
                android:textSize="16sp"
                android:textStyle="bold"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="&#9679; Online"
                android:textColor="#69F0AE"
                android:textSize="12sp"/>

        </LinearLayout>

    </LinearLayout>

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/rvMessages"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:padding="16dp"
        android:clipToPadding="false"/>

    <HorizontalScrollView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:scrollbars="none"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:paddingBottom="8dp">

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <TextView
                android:id="@+id/chipRemind"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Remind me"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:padding="10dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/chipStressed"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="I feel stressed"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:padding="10dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/chipPlan"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Plan my day"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:padding="10dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/chipBag"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="What to carry?"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:padding="10dp"
                android:background="@drawable/chip_dark"/>

        </LinearLayout>

    </HorizontalScrollView>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="12dp"
        android:gravity="center_vertical"
        android:background="#1A1A1A">

        <EditText
            android:id="@+id/etMessage"
            android:layout_width="0dp"
            android:layout_height="48dp"
            android:layout_weight="1"
            android:hint="Type a message..."
            android:textColor="#FFFFFF"
            android:textColorHint="#555555"
            android:paddingStart="16dp"
            android:paddingEnd="16dp"
            android:background="@drawable/edittext_dark"
            android:layout_marginEnd="8dp"
            android:imeOptions="actionSend"
            android:inputType="textMultiLine"/>

        <Button
            android:id="@+id/btnSend"
            android:layout_width="48dp"
            android:layout_height="48dp"
            android:text="&#10148;"
            android:textSize="18sp"
            android:padding="0dp"
            android:backgroundTint="#7C4DFF"/>

    </LinearLayout>

    <include layout="@layout/view_bottom_nav"/>

</LinearLayout>
'''

# ─────────────────────────────────────────────
# activity_bag.xml
# ─────────────────────────────────────────────
bag = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#0D0D0D">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp"
        android:gravity="center_vertical">

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Smart Bag"
                android:textColor="#FFFFFF"
                android:textSize="24sp"
                android:textStyle="bold"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Never forget anything again"
                android:textColor="#888888"
                android:textSize="13sp"/>

        </LinearLayout>

        <TextView
            android:id="@+id/btnAddItem"
            android:layout_width="44dp"
            android:layout_height="44dp"
            android:text="+"
            android:textColor="#FFFFFF"
            android:textSize="24sp"
            android:gravity="center"
            android:background="@drawable/chip_purple"/>

    </LinearLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:background="@drawable/card_dark"
        android:padding="16dp"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="12dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="8dp">

            <TextView
                android:id="@+id/tvProgressLabel"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="MON CHECKLIST"
                android:textColor="#888888"
                android:textSize="12sp"
                android:textStyle="bold"/>

            <TextView
                android:id="@+id/tvProgressCount"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="0/0 packed"
                android:textColor="#B388FF"
                android:textSize="12sp"
                android:textStyle="bold"/>

        </LinearLayout>

        <ProgressBar
            android:id="@+id/progressBar"
            style="?android:attr/progressBarStyleHorizontal"
            android:layout_width="match_parent"
            android:layout_height="8dp"
            android:progressDrawable="@drawable/progress_purple"
            android:progress="0"
            android:max="100"/>

    </LinearLayout>

    <HorizontalScrollView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:scrollbars="none"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:paddingBottom="12dp">

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <TextView
                android:id="@+id/dayMon"
                android:layout_width="70dp"
                android:layout_height="44dp"
                android:text="Mon"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:gravity="center"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_purple"/>

            <TextView
                android:id="@+id/dayTue"
                android:layout_width="70dp"
                android:layout_height="44dp"
                android:text="Tue"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:gravity="center"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/dayWed"
                android:layout_width="70dp"
                android:layout_height="44dp"
                android:text="Wed"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:gravity="center"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/dayThu"
                android:layout_width="70dp"
                android:layout_height="44dp"
                android:text="Thu"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:gravity="center"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/dayFri"
                android:layout_width="70dp"
                android:layout_height="44dp"
                android:text="Fri"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:gravity="center"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/daySat"
                android:layout_width="70dp"
                android:layout_height="44dp"
                android:text="Sat"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:gravity="center"
                android:background="@drawable/chip_dark"/>

        </LinearLayout>

    </HorizontalScrollView>

    <HorizontalScrollView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:scrollbars="none"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:paddingBottom="12dp">

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <TextView
                android:id="@+id/catAll"
                android:layout_width="wrap_content"
                android:layout_height="32dp"
                android:text="ALL"
                android:textColor="#FFFFFF"
                android:textSize="11sp"
                android:textStyle="bold"
                android:gravity="center"
                android:paddingStart="12dp"
                android:paddingEnd="12dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_purple"/>

            <TextView
                android:id="@+id/catBooks"
                android:layout_width="wrap_content"
                android:layout_height="32dp"
                android:text="Books"
                android:textColor="#FFFFFF"
                android:textSize="11sp"
                android:gravity="center"
                android:paddingStart="12dp"
                android:paddingEnd="12dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/catStationery"
                android:layout_width="wrap_content"
                android:layout_height="32dp"
                android:text="Stationery"
                android:textColor="#FFFFFF"
                android:textSize="11sp"
                android:gravity="center"
                android:paddingStart="12dp"
                android:paddingEnd="12dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/catLab"
                android:layout_width="wrap_content"
                android:layout_height="32dp"
                android:text="Lab"
                android:textColor="#FFFFFF"
                android:textSize="11sp"
                android:gravity="center"
                android:paddingStart="12dp"
                android:paddingEnd="12dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/catPersonal"
                android:layout_width="wrap_content"
                android:layout_height="32dp"
                android:text="Personal"
                android:textColor="#FFFFFF"
                android:textSize="11sp"
                android:gravity="center"
                android:paddingStart="12dp"
                android:paddingEnd="12dp"
                android:background="@drawable/chip_dark"/>

        </LinearLayout>

    </HorizontalScrollView>

    <ScrollView
        android:id="@+id/rvBagItems"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"/>

    <include layout="@layout/view_bottom_nav"/>

</LinearLayout>
'''

# ─────────────────────────────────────────────
# activity_planner.xml
# ─────────────────────────────────────────────
planner = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#0D0D0D">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Smart Planner"
            android:textColor="#FFFFFF"
            android:textSize="24sp"
            android:textStyle="bold"/>

        <TextView
            android:id="@+id/tvDate"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textColor="#888888"
            android:textSize="14sp"/>

    </LinearLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp"
        android:background="@drawable/card_dark"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="16dp">

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Today\'s Progress"
                android:textColor="#888888"
                android:textSize="12sp"/>

            <TextView
                android:id="@+id/tvProgress"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="0/0"
                android:textColor="#FFFFFF"
                android:textSize="28sp"
                android:textStyle="bold"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Keep going!"
                android:textColor="#B388FF"
                android:textSize="12sp"/>

        </LinearLayout>

    </LinearLayout>

    <Button
        android:id="@+id/btnAddTask"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:text="+ Add Task"
        android:textColor="#FFFFFF"
        android:textSize="14sp"
        android:backgroundTint="#7C4DFF"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="8dp"/>

    <Button
        android:id="@+id/btnAiPlan"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:text="Get AI Study Plan"
        android:textColor="#FFFFFF"
        android:textSize="14sp"
        android:backgroundTint="#3D1B6E"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="16dp"/>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="TIMELINE"
        android:textColor="#555555"
        android:textSize="12sp"
        android:textStyle="bold"
        android:paddingStart="16dp"
        android:paddingBottom="8dp"/>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <LinearLayout
            android:id="@+id/taskContainer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="16dp"/>

    </ScrollView>

    <include layout="@layout/view_bottom_nav"/>

</LinearLayout>
'''

# ─────────────────────────────────────────────
# activity_memories.xml
# ─────────────────────────────────────────────
memories = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#0D0D0D">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp"
        android:gravity="center_vertical">

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Your Proud Moments"
                android:textColor="#FFFFFF"
                android:textSize="22sp"
                android:textStyle="bold"/>

            <TextView
                android:id="@+id/tvMemoryCount"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Loading..."
                android:textColor="#888888"
                android:textSize="13sp"/>

        </LinearLayout>

        <TextView
            android:id="@+id/btnSearch"
            android:layout_width="44dp"
            android:layout_height="44dp"
            android:text="&#128269;"
            android:textSize="20sp"
            android:gravity="center"
            android:background="@drawable/chip_dark"/>

    </LinearLayout>

    <LinearLayout
        android:id="@+id/searchLayout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:paddingBottom="12dp"
        android:gravity="center_vertical"
        android:visibility="gone">

        <EditText
            android:id="@+id/etSearch"
            android:layout_width="0dp"
            android:layout_height="48dp"
            android:layout_weight="1"
            android:hint="Search memories..."
            android:textColor="#FFFFFF"
            android:textColorHint="#555555"
            android:paddingStart="16dp"
            android:paddingEnd="16dp"
            android:background="@drawable/edittext_dark"
            android:layout_marginEnd="8dp"
            android:inputType="text"/>

        <TextView
            android:id="@+id/btnCancelSearch"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="X"
            android:textColor="#FF5252"
            android:textSize="18sp"
            android:padding="8dp"/>

    </LinearLayout>

    <HorizontalScrollView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:scrollbars="none"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:paddingBottom="12dp">

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <TextView
                android:id="@+id/chipAll"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="ALL"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:textStyle="bold"
                android:gravity="center"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_purple"/>

            <TextView
                android:id="@+id/chipWin"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="WIN"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:gravity="center"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/chipStudy"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="STUDY"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:gravity="center"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/chipGrowth"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="GROWTH"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:gravity="center"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:layout_marginEnd="8dp"
                android:background="@drawable/chip_dark"/>

            <TextView
                android:id="@+id/chipNote"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="NOTE"
                android:textColor="#FFFFFF"
                android:textSize="12sp"
                android:gravity="center"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:background="@drawable/chip_dark"/>

        </LinearLayout>

    </HorizontalScrollView>

    <Button
        android:id="@+id/btnAddMemory"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:text="+ Add Proud Moment"
        android:textColor="#FFFFFF"
        android:textSize="14sp"
        android:backgroundTint="#7C4DFF"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="12dp"/>

    <ScrollView
        android:id="@+id/rvMemories"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"/>

    <include layout="@layout/view_bottom_nav"/>

</LinearLayout>
'''

# ─────────────────────────────────────────────
# activity_profile.xml  (keep all tabs, just replace bottom nav)
# ─────────────────────────────────────────────
profile = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#0D0D0D">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp"
        android:gravity="center_vertical"
        android:background="#111111">

        <ImageView
            android:layout_width="48dp"
            android:layout_height="48dp"
            android:src="@drawable/robot"
            android:scaleType="centerCrop"
            android:background="@drawable/circle_purple"
            android:padding="4dp"
            android:layout_marginEnd="12dp"/>

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical">

            <TextView
                android:id="@+id/tvStudentName"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Hey, Student!"
                android:textColor="#FFFFFF"
                android:textSize="18sp"
                android:textStyle="bold"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Your mind space"
                android:textColor="#888888"
                android:textSize="12sp"/>

        </LinearLayout>

    </LinearLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="16dp">

        <TextView
            android:id="@+id/tabThought"
            android:layout_width="0dp"
            android:layout_height="44dp"
            android:layout_weight="1"
            android:text="Mind Garage"
            android:textColor="#FFFFFF"
            android:textSize="13sp"
            android:gravity="center"
            android:background="@drawable/chip_purple"
            android:layout_marginEnd="8dp"/>

        <TextView
            android:id="@+id/tabFuture"
            android:layout_width="0dp"
            android:layout_height="44dp"
            android:layout_weight="1"
            android:text="Time Capsule"
            android:textColor="#FFFFFF"
            android:textSize="13sp"
            android:gravity="center"
            android:background="@drawable/chip_dark"/>

    </LinearLayout>

    <LinearLayout
        android:id="@+id/thoughtLayout"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:orientation="vertical">

        <HorizontalScrollView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:scrollbars="none"
            android:paddingStart="16dp"
            android:paddingEnd="16dp"
            android:paddingBottom="12dp">

            <LinearLayout
                android:id="@+id/moodContainer"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:orientation="horizontal">

                <TextView
                    android:id="@+id/moodFrustrated"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Frustrated"
                    android:textColor="#FFFFFF"
                    android:textSize="12sp"
                    android:gravity="center"
                    android:paddingStart="12dp"
                    android:paddingEnd="12dp"
                    android:layout_marginEnd="8dp"
                    android:background="@drawable/chip_dark"/>

                <TextView
                    android:id="@+id/moodCurious"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Curious"
                    android:textColor="#FFFFFF"
                    android:textSize="12sp"
                    android:gravity="center"
                    android:paddingStart="12dp"
                    android:paddingEnd="12dp"
                    android:layout_marginEnd="8dp"
                    android:background="@drawable/chip_dark"/>

                <TextView
                    android:id="@+id/moodHappy"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Happy"
                    android:textColor="#FFFFFF"
                    android:textSize="12sp"
                    android:gravity="center"
                    android:paddingStart="12dp"
                    android:paddingEnd="12dp"
                    android:layout_marginEnd="8dp"
                    android:background="@drawable/chip_dark"/>

                <TextView
                    android:id="@+id/moodAnxious"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Anxious"
                    android:textColor="#FFFFFF"
                    android:textSize="12sp"
                    android:gravity="center"
                    android:paddingStart="12dp"
                    android:paddingEnd="12dp"
                    android:layout_marginEnd="8dp"
                    android:background="@drawable/chip_dark"/>

                <TextView
                    android:id="@+id/moodIdea"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Idea"
                    android:textColor="#FFFFFF"
                    android:textSize="12sp"
                    android:gravity="center"
                    android:paddingStart="12dp"
                    android:paddingEnd="12dp"
                    android:layout_marginEnd="8dp"
                    android:background="@drawable/chip_dark"/>

                <TextView
                    android:id="@+id/moodMotivated"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Motivated"
                    android:textColor="#FFFFFF"
                    android:textSize="12sp"
                    android:gravity="center"
                    android:paddingStart="12dp"
                    android:paddingEnd="12dp"
                    android:background="@drawable/chip_dark"/>

            </LinearLayout>

        </HorizontalScrollView>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:paddingStart="16dp"
            android:paddingEnd="16dp"
            android:paddingBottom="12dp"
            android:gravity="center_vertical">

            <EditText
                android:id="@+id/etThought"
                android:layout_width="0dp"
                android:layout_height="48dp"
                android:layout_weight="1"
                android:hint="Drop a thought here..."
                android:textColor="#FFFFFF"
                android:textColorHint="#555555"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:background="@drawable/edittext_dark"
                android:layout_marginEnd="8dp"/>

            <Button
                android:id="@+id/btnPark"
                android:layout_width="48dp"
                android:layout_height="48dp"
                android:text="&#10148;"
                android:textSize="16sp"
                android:padding="0dp"
                android:backgroundTint="#7C4DFF"/>

        </LinearLayout>

        <TextView
            android:id="@+id/tvThoughtCount"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="YOUR PARKED THOUGHTS"
            android:textColor="#555555"
            android:textSize="11sp"
            android:textStyle="bold"
            android:paddingStart="16dp"
            android:paddingBottom="8dp"/>

        <ScrollView
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1">

            <LinearLayout
                android:id="@+id/thoughtContainer"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp"/>

        </ScrollView>

    </LinearLayout>

    <LinearLayout
        android:id="@+id/futureLayout"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:orientation="vertical"
        android:visibility="gone">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="16dp"
            android:background="#111111"
            android:layout_marginStart="16dp"
            android:layout_marginEnd="16dp"
            android:layout_marginBottom="12dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Dear Future Me..."
                android:textColor="#B388FF"
                android:textSize="16sp"
                android:textStyle="bold"
                android:layout_marginBottom="8dp"/>

            <EditText
                android:id="@+id/etFutureLetter"
                android:layout_width="match_parent"
                android:layout_height="120dp"
                android:hint="Write something your future self needs to hear..."
                android:textColor="#FFFFFF"
                android:textColorHint="#555555"
                android:padding="12dp"
                android:gravity="top"
                android:background="@drawable/edittext_dark"
                android:layout_marginBottom="12dp"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Seal until..."
                android:textColor="#888888"
                android:textSize="12sp"
                android:layout_marginBottom="8dp"/>

            <HorizontalScrollView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:scrollbars="none"
                android:layout_marginBottom="12dp">

                <LinearLayout
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">

                    <TextView
                        android:id="@+id/timer1Week"
                        android:layout_width="wrap_content"
                        android:layout_height="36dp"
                        android:text="1 Week"
                        android:textColor="#FFFFFF"
                        android:textSize="12sp"
                        android:gravity="center"
                        android:paddingStart="12dp"
                        android:paddingEnd="12dp"
                        android:layout_marginEnd="8dp"
                        android:background="@drawable/chip_purple"/>

                    <TextView
                        android:id="@+id/timer1Month"
                        android:layout_width="wrap_content"
                        android:layout_height="36dp"
                        android:text="1 Month"
                        android:textColor="#FFFFFF"
                        android:textSize="12sp"
                        android:gravity="center"
                        android:paddingStart="12dp"
                        android:paddingEnd="12dp"
                        android:layout_marginEnd="8dp"
                        android:background="@drawable/chip_dark"/>

                    <TextView
                        android:id="@+id/timer3Months"
                        android:layout_width="wrap_content"
                        android:layout_height="36dp"
                        android:text="3 Months"
                        android:textColor="#FFFFFF"
                        android:textSize="12sp"
                        android:gravity="center"
                        android:paddingStart="12dp"
                        android:paddingEnd="12dp"
                        android:layout_marginEnd="8dp"
                        android:background="@drawable/chip_dark"/>

                    <TextView
                        android:id="@+id/timer1Year"
                        android:layout_width="wrap_content"
                        android:layout_height="36dp"
                        android:text="1 Year"
                        android:textColor="#FFFFFF"
                        android:textSize="12sp"
                        android:gravity="center"
                        android:paddingStart="12dp"
                        android:paddingEnd="12dp"
                        android:layout_marginEnd="8dp"
                        android:background="@drawable/chip_dark"/>

                    <TextView
                        android:id="@+id/timerCustom"
                        android:layout_width="wrap_content"
                        android:layout_height="36dp"
                        android:text="Custom"
                        android:textColor="#FFFFFF"
                        android:textSize="12sp"
                        android:gravity="center"
                        android:paddingStart="12dp"
                        android:paddingEnd="12dp"
                        android:background="@drawable/chip_dark"/>

                </LinearLayout>

            </HorizontalScrollView>

            <Button
                android:id="@+id/btnSendLetter"
                android:layout_width="match_parent"
                android:layout_height="48dp"
                android:text="Seal and Send to Future Me"
                android:textColor="#FFFFFF"
                android:textSize="14sp"
                android:backgroundTint="#3D1B6E"/>

        </LinearLayout>

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="TIME CAPSULES"
            android:textColor="#555555"
            android:textSize="11sp"
            android:textStyle="bold"
            android:paddingStart="16dp"
            android:paddingBottom="8dp"/>

        <ScrollView
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1">

            <LinearLayout
                android:id="@+id/futureContainer"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp"/>

        </ScrollView>

    </LinearLayout>

    <Button
        android:id="@+id/btnLogout"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:text="Logout"
        android:textColor="#FFFFFF"
        android:textSize="14sp"
        android:backgroundTint="#FF5252"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="8dp"/>

    <include layout="@layout/view_bottom_nav"/>

</LinearLayout>
'''

# ─────────────────────────────────────────────
# Write all files
# ─────────────────────────────────────────────
files = {
    "activity_home.xml": home,
    "activity_bag.xml": bag,
    "activity_planner.xml": planner,
    "activity_memories.xml": memories,
    "activity_profile.xml": profile,
}

for filename, content in files.items():
    path = os.path.join(BASE, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"DONE: {filename}")

print("\n✅ All layout files updated.")