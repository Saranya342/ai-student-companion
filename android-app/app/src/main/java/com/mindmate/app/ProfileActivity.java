package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.mindmate.app.network.ApiClient;

import org.json.JSONObject;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProfileActivity extends AppCompatActivity {

    private String token;
    private Handler mainHandler = new Handler(Looper.getMainLooper());

    TextView tvName, tvEmail, tvHighFiveStatus;
    Button btnHighFive, btnLogout;

    TextView itemSettings, itemHelp, itemAbout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_profile);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        tvName = findViewById(R.id.tvName);
        tvEmail = findViewById(R.id.tvEmail);
        tvHighFiveStatus = findViewById(R.id.tvHighFiveStatus);
        btnHighFive = findViewById(R.id.btnHighFive);
        btnLogout = findViewById(R.id.btnLogout);

        itemSettings = findViewById(R.id.itemSettings);
        itemHelp = findViewById(R.id.itemHelp);
        itemAbout = findViewById(R.id.itemAbout);

        btnHighFive.setOnClickListener(v -> markHighFive());
        btnLogout.setOnClickListener(v -> logout());

        itemSettings.setOnClickListener(v ->
                new AlertDialog.Builder(this)
                        .setTitle("Settings")
                        .setMessage("Settings screen coming soon.")
                        .setPositiveButton("OK", null)
                        .show()
        );

        itemHelp.setOnClickListener(v ->
                startActivity(new Intent(ProfileActivity.this, FaqActivity.class))
        );

        itemAbout.setOnClickListener(v ->
                startActivity(new Intent(ProfileActivity.this, AboutActivity.class))
        );

        loadProfile();
        loadStreaks(); // show streak info on load

        BottomNavigationView bottomNav = findViewById(R.id.bottomNav);
        bottomNav.setSelectedItemId(R.id.nav_profile);
        bottomNav.setOnItemSelectedListener(item -> {
            int id = item.getItemId();
            if (id == R.id.nav_profile) return true;

            if (id == R.id.nav_chat) startActivity(new Intent(this, HomeActivity.class));
            else if (id == R.id.nav_planner) startActivity(new Intent(this, PlannerActivity.class));
            else if (id == R.id.nav_bag) startActivity(new Intent(this, BagActivity.class));
            else if (id == R.id.nav_journal) startActivity(new Intent(this, JournalActivity.class));

            finish();
            return true;
        });
    }

    private void loadProfile() {
        ApiClient.getService().getProfileMe(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            try {
                                if (response.isSuccessful() && response.body() != null) {
                                    String json = response.body().string();
                                    JSONObject obj = new JSONObject(json);
                                    tvName.setText(obj.optString("name", "Student"));
                                    tvEmail.setText(obj.optString("email", ""));
                                } else {
                                    tvName.setText("Student");
                                    tvEmail.setText("");
                                }
                            } catch (Exception e) {
                                tvName.setText("Student");
                                tvEmail.setText("");
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() -> {
                            tvName.setText("Student");
                            tvEmail.setText("");
                        });
                    }
                });
    }

    private void loadStreaks() {
        ApiClient.getService().getStreaks(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            try {
                                if (response.isSuccessful() && response.body() != null) {
                                    String json = response.body().string();
                                    JSONObject obj = new JSONObject(json);

                                    int current = obj.optInt("current_streak", 0);
                                    int longest = obj.optInt("longest_streak", 0);

                                    tvHighFiveStatus.setText(
                                            "Current streak: " + current + " days • Longest: " + longest + " days"
                                    );
                                } else {
                                    tvHighFiveStatus.setText("Tap to mark today's high‑five");
                                }
                            } catch (Exception e) {
                                tvHighFiveStatus.setText("Tap to mark today's high‑five");
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() -> tvHighFiveStatus.setText("Tap to mark today's high‑five"));
                    }
                });
    }

    private void markHighFive() {
        btnHighFive.setEnabled(false);
        btnHighFive.setText("Marking...");

        ApiClient.getService().highFive(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            btnHighFive.setEnabled(true);
                            btnHighFive.setText("Mark High‑Five");

                            if (response.isSuccessful()) {
                                Toast.makeText(ProfileActivity.this, "High‑five marked 🙌", Toast.LENGTH_SHORT).show();
                                loadStreaks(); // refresh after marking
                            } else {
                                Toast.makeText(ProfileActivity.this, "Failed to mark high‑five", Toast.LENGTH_SHORT).show();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() -> {
                            btnHighFive.setEnabled(true);
                            btnHighFive.setText("Mark High‑Five");
                            Toast.makeText(ProfileActivity.this, "Connection failed!", Toast.LENGTH_SHORT).show();
                        });
                    }
                });
    }

    private void logout() {
        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        prefs.edit().clear().apply();
        Toast.makeText(this, "Logged out", Toast.LENGTH_SHORT).show();
        startActivity(new Intent(this, LoginActivity.class));
        finishAffinity();
    }
}