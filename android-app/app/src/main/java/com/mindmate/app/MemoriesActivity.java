package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class MemoriesActivity extends AppCompatActivity {

    TextView navChat, navPlanner, navBag, navProfile;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_memories);

        navChat = findViewById(R.id.navChat);
        navPlanner = findViewById(R.id.navPlanner);
        navBag = findViewById(R.id.navBag);
        navProfile = findViewById(R.id.navProfile);

        navChat.setOnClickListener(v -> {
            startActivity(new Intent(this, HomeActivity.class));
            finish();
        });
        navPlanner.setOnClickListener(v -> {
            startActivity(new Intent(this, PlannerActivity.class));
            finish();
        });
        navBag.setOnClickListener(v -> {
            startActivity(new Intent(this, BagActivity.class));
            finish();
        });
        navProfile.setOnClickListener(v -> {
            startActivity(new Intent(this, ProfileActivity.class));
            finish();
        });
    }
}