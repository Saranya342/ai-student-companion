package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class ProfileActivity extends AppCompatActivity {

    TextView navChat, navPlanner, navBag, navMemories;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_profile);

        navChat = findViewById(R.id.navChat);
        navPlanner = findViewById(R.id.navPlanner);
        navBag = findViewById(R.id.navBag);
        navMemories = findViewById(R.id.navMemories);

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
        navMemories.setOnClickListener(v -> {
            startActivity(new Intent(this, MemoriesActivity.class));
            finish();
        });
    }
}