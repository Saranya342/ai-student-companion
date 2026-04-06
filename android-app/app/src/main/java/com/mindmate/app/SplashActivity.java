package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;

public class SplashActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        Button btnLetsGo = findViewById(R.id.btnLetsGo);

        btnLetsGo.setOnClickListener(v -> {
            SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
            String token = prefs.getString("token", null);

            if (token != null) {
                startActivity(new Intent(this, HomeActivity.class));
            } else {
                startActivity(new Intent(this, LoginActivity.class));
            }
            finish();
        });
    }
}