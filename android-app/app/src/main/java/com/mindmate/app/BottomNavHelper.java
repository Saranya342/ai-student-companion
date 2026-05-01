package com.mindmate.app;

import android.app.Activity;
import android.content.Intent;

import com.google.android.material.bottomnavigation.BottomNavigationView;

public final class BottomNavHelper {

    private BottomNavHelper() {}

    public static void setup(BottomNavigationView nav, Activity activity, int selectedItemId) {
        nav.setSelectedItemId(selectedItemId);

        nav.setOnItemSelectedListener(item -> {
            int id = item.getItemId();
            if (id == selectedItemId) return true;

            Intent intent = null;
            if (id == R.id.nav_chat) intent = new Intent(activity, HomeActivity.class);
            else if (id == R.id.nav_planner) intent = new Intent(activity, PlannerActivity.class);
            else if (id == R.id.nav_bag) intent = new Intent(activity, BagActivity.class);
            else if (id == R.id.nav_journal) intent = new Intent(activity, JournalActivity.class);
            else if (id == R.id.nav_profile) intent = new Intent(activity, ProfileActivity.class);

            if (intent != null) {
                activity.startActivity(intent);
                activity.finish();
                return true;
            }
            return false;
        });
    }
}