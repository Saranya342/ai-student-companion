package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class BagActivity extends AppCompatActivity {

    TextView navChat, navPlanner, navMemories, navProfile;
    String token;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bag);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        navChat = findViewById(R.id.navChat);
        navPlanner = findViewById(R.id.navPlanner);
        navMemories = findViewById(R.id.navMemories);
        navProfile = findViewById(R.id.navProfile);

        navChat.setOnClickListener(v -> {
            startActivity(new Intent(this, HomeActivity.class));
            finish();
        });
        navPlanner.setOnClickListener(v -> {
            startActivity(new Intent(this, PlannerActivity.class));
            finish();
        });
        navMemories.setOnClickListener(v -> {
            startActivity(new Intent(this, MemoriesActivity.class));
            finish();
        });
        navProfile.setOnClickListener(v -> {
            startActivity(new Intent(this, ProfileActivity.class));
            finish();
        });
    }
}