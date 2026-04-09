package com.mindmate.app;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.mindmate.app.network.ApiClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

import okhttp3.MediaType;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProfileActivity extends AppCompatActivity {

    // Navigation
    TextView navChat, navPlanner, navBag, navMemories;

    // Tabs
    TextView tabThought, tabFuture;
    LinearLayout thoughtLayout, futureLayout;

    // Thought Parking
    TextView moodFrustrated, moodCurious, moodHappy,
            moodAnxious, moodIdea, moodMotivated;
    EditText etThought;
    Button btnPark;
    LinearLayout thoughtContainer;
    TextView tvThoughtCount;
    String selectedMood = "😊 Happy";

    // Future Letters
    EditText etFutureLetter;
    Button btnSendLetter, btnLogout;
    TextView timer1Week, timer1Month, timer3Months,
            timer1Year, timerCustom;
    LinearLayout futureContainer;
    String selectedUnlockDate = "";

    String token;
    Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_profile);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        // Header name
        TextView tvStudentName = findViewById(R.id.tvStudentName);
        tvStudentName.setText("Hey, Student! 👋");

        // Init tabs
        tabThought = findViewById(R.id.tabThought);
        tabFuture = findViewById(R.id.tabFuture);
        thoughtLayout = findViewById(R.id.thoughtLayout);
        futureLayout = findViewById(R.id.futureLayout);

        // Init thought parking
        moodFrustrated = findViewById(R.id.moodFrustrated);
        moodCurious = findViewById(R.id.moodCurious);
        moodHappy = findViewById(R.id.moodHappy);
        moodAnxious = findViewById(R.id.moodAnxious);
        moodIdea = findViewById(R.id.moodIdea);
        moodMotivated = findViewById(R.id.moodMotivated);
        etThought = findViewById(R.id.etThought);
        btnPark = findViewById(R.id.btnPark);
        thoughtContainer = findViewById(R.id.thoughtContainer);
        tvThoughtCount = findViewById(R.id.tvThoughtCount);

        // Init future letters
        etFutureLetter = findViewById(R.id.etFutureLetter);
        btnSendLetter = findViewById(R.id.btnSendLetter);
        timer1Week = findViewById(R.id.timer1Week);
        timer1Month = findViewById(R.id.timer1Month);
        timer3Months = findViewById(R.id.timer3Months);
        timer1Year = findViewById(R.id.timer1Year);
        timerCustom = findViewById(R.id.timerCustom);
        futureContainer = findViewById(R.id.futureContainer);

        // Logout
        btnLogout = findViewById(R.id.btnLogout);

        // Navigation
        navChat = findViewById(R.id.navChat);
        navPlanner = findViewById(R.id.navPlanner);
        navBag = findViewById(R.id.navBag);
        navMemories = findViewById(R.id.navMemories);

        // Set default unlock date to 1 week
        setUnlockDate(7);

        // Setup everything
        setupTabs();
        setupMoods();
        setupTimers();
        loadThoughts();
        loadFutureLetters();

        // Park thought
        btnPark.setOnClickListener(v -> parkThought());

        // Send letter
        btnSendLetter.setOnClickListener(v -> sendFutureLetter());

        // Logout
        btnLogout.setOnClickListener(v -> {
            prefs.edit().clear().apply();
            Toast.makeText(this, "See you soon! 👋",
                    Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finishAffinity();
        });

        // Navigation clicks
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

    private void setupTabs() {
        tabThought.setOnClickListener(v -> {
            thoughtLayout.setVisibility(View.VISIBLE);
            futureLayout.setVisibility(View.GONE);
            tabThought.setBackgroundResource(R.drawable.chip_purple);
            tabFuture.setBackgroundResource(R.drawable.chip_dark);
        });

        tabFuture.setOnClickListener(v -> {
            thoughtLayout.setVisibility(View.GONE);
            futureLayout.setVisibility(View.VISIBLE);
            tabThought.setBackgroundResource(R.drawable.chip_dark);
            tabFuture.setBackgroundResource(R.drawable.chip_purple);
        });
    }

    private void setupMoods() {
        // Default mood selected
        moodHappy.setBackgroundResource(R.drawable.chip_purple);

        moodFrustrated.setOnClickListener(v -> {
            selectedMood = "😤 Frustrated";
            resetMoods();
            moodFrustrated.setBackgroundResource(R.drawable.chip_purple);
        });
        moodCurious.setOnClickListener(v -> {
            selectedMood = "💭 Curious";
            resetMoods();
            moodCurious.setBackgroundResource(R.drawable.chip_purple);
        });
        moodHappy.setOnClickListener(v -> {
            selectedMood = "😊 Happy";
            resetMoods();
            moodHappy.setBackgroundResource(R.drawable.chip_purple);
        });
        moodAnxious.setOnClickListener(v -> {
            selectedMood = "😰 Anxious";
            resetMoods();
            moodAnxious.setBackgroundResource(R.drawable.chip_purple);
        });
        moodIdea.setOnClickListener(v -> {
            selectedMood = "💡 Idea";
            resetMoods();
            moodIdea.setBackgroundResource(R.drawable.chip_purple);
        });
        moodMotivated.setOnClickListener(v -> {
            selectedMood = "🔥 Motivated";
            resetMoods();
            moodMotivated.setBackgroundResource(R.drawable.chip_purple);
        });
    }

    private void resetMoods() {
        moodFrustrated.setBackgroundResource(R.drawable.chip_dark);
        moodCurious.setBackgroundResource(R.drawable.chip_dark);
        moodHappy.setBackgroundResource(R.drawable.chip_dark);
        moodAnxious.setBackgroundResource(R.drawable.chip_dark);
        moodIdea.setBackgroundResource(R.drawable.chip_dark);
        moodMotivated.setBackgroundResource(R.drawable.chip_dark);
    }

    private void setupTimers() {
        timer1Week.setOnClickListener(v -> {
            setUnlockDate(7);
            resetTimers();
            timer1Week.setBackgroundResource(R.drawable.chip_purple);
        });
        timer1Month.setOnClickListener(v -> {
            setUnlockDate(30);
            resetTimers();
            timer1Month.setBackgroundResource(R.drawable.chip_purple);
        });
        timer3Months.setOnClickListener(v -> {
            setUnlockDate(90);
            resetTimers();
            timer3Months.setBackgroundResource(R.drawable.chip_purple);
        });
        timer1Year.setOnClickListener(v -> {
            setUnlockDate(365);
            resetTimers();
            timer1Year.setBackgroundResource(R.drawable.chip_purple);
        });
        timerCustom.setOnClickListener(v -> showDatePicker());
    }

    private void resetTimers() {
        timer1Week.setBackgroundResource(R.drawable.chip_dark);
        timer1Month.setBackgroundResource(R.drawable.chip_dark);
        timer3Months.setBackgroundResource(R.drawable.chip_dark);
        timer1Year.setBackgroundResource(R.drawable.chip_dark);
        timerCustom.setBackgroundResource(R.drawable.chip_dark);
    }

    private void setUnlockDate(int daysFromNow) {
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_YEAR, daysFromNow);
        SimpleDateFormat sdf = new SimpleDateFormat(
                "yyyy-MM-dd", Locale.getDefault());
        selectedUnlockDate = sdf.format(cal.getTime());
    }

    private void showDatePicker() {
        Calendar cal = Calendar.getInstance();
        DatePickerDialog dialog = new DatePickerDialog(
                this,
                (view, year, month, day) -> {
                    selectedUnlockDate = String.format(
                            Locale.getDefault(),
                            "%04d-%02d-%02d",
                            year, month + 1, day);
                    resetTimers();
                    timerCustom.setBackgroundResource(
                            R.drawable.chip_purple);
                    timerCustom.setText("📅 " + selectedUnlockDate);
                    Toast.makeText(this,
                            "Unlocks on " + selectedUnlockDate,
                            Toast.LENGTH_SHORT).show();
                },
                cal.get(Calendar.YEAR),
                cal.get(Calendar.MONTH),
                cal.get(Calendar.DAY_OF_MONTH)
        );
        dialog.getDatePicker().setMinDate(
                System.currentTimeMillis());
        dialog.show();
    }

    private void parkThought() {
        String thought = etThought.getText().toString().trim();
        if (thought.isEmpty()) {
            Toast.makeText(this, "Type a thought first! 🧠",
                    Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            JSONObject json = new JSONObject();
            json.put("content", thought);
            json.put("category", "thought");
            json.put("mood", selectedMood);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    json.toString()
            );

            ApiClient.getService().addMemory(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call,
                                               Response<ResponseBody> response) {
                            mainHandler.post(() -> {
                                if (response.isSuccessful()) {
                                    etThought.setText("");
                                    Toast.makeText(ProfileActivity.this,
                                            "Thought parked! 🧠",
                                            Toast.LENGTH_SHORT).show();
                                    loadThoughts();
                                } else {
                                    Toast.makeText(ProfileActivity.this,
                                            "Failed to park thought!",
                                            Toast.LENGTH_SHORT).show();
                                }
                            });
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call,
                                              Throwable t) {
                            mainHandler.post(() ->
                                    Toast.makeText(ProfileActivity.this,
                                            "Connection failed!",
                                            Toast.LENGTH_SHORT).show());
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void sendFutureLetter() {
        String letter = etFutureLetter.getText().toString().trim();
        if (letter.isEmpty()) {
            Toast.makeText(this,
                    "Write something to your future self! 💌",
                    Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            JSONObject json = new JSONObject();
            json.put("content", letter);
            json.put("category", "future");
            json.put("unlock_date", selectedUnlockDate);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    json.toString()
            );

            ApiClient.getService().addMemory(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call,
                                               Response<ResponseBody> response) {
                            mainHandler.post(() -> {
                                if (response.isSuccessful()) {
                                    etFutureLetter.setText("");
                                    Toast.makeText(ProfileActivity.this,
                                            "Letter sealed! 🔒 Opens on "
                                                    + selectedUnlockDate,
                                            Toast.LENGTH_LONG).show();
                                    loadFutureLetters();
                                } else {
                                    Toast.makeText(ProfileActivity.this,
                                            "Failed to send letter!",
                                            Toast.LENGTH_SHORT).show();
                                }
                            });
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call,
                                              Throwable t) {
                            mainHandler.post(() ->
                                    Toast.makeText(ProfileActivity.this,
                                            "Connection failed!",
                                            Toast.LENGTH_SHORT).show());
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void loadThoughts() {
        ApiClient.getService().getThoughts(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            try {
                                if (response.isSuccessful()
                                        && response.body() != null) {
                                    String json = response.body().string();
                                    JSONObject obj = new JSONObject(json);
                                    JSONArray thoughts =
                                            obj.getJSONArray("thoughts");

                                    thoughtContainer.removeAllViews();
                                    tvThoughtCount.setText(
                                            "YOUR PARKED THOUGHTS ("
                                                    + thoughts.length() + ")");

                                    if (thoughts.length() == 0) {
                                        addEmptyView(thoughtContainer,
                                                "No thoughts parked yet!\nDrop something on your mind 🧠");
                                        return;
                                    }

                                    for (int i = 0; i < thoughts.length(); i++) {
                                        JSONObject t = thoughts.getJSONObject(i);
                                        addThoughtView(
                                                t.getInt("id"),
                                                t.getString("content"),
                                                t.optString("mood", "😊 Happy"),
                                                t.getString("created_at")
                                        );
                                    }
                                }
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(ProfileActivity.this,
                                        "Failed to load thoughts",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void loadFutureLetters() {
        ApiClient.getService().getFutureLetters(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            try {
                                if (response.isSuccessful()
                                        && response.body() != null) {
                                    String json = response.body().string();
                                    JSONObject obj = new JSONObject(json);
                                    JSONArray letters =
                                            obj.getJSONArray("letters");

                                    futureContainer.removeAllViews();

                                    if (letters.length() == 0) {
                                        addEmptyView(futureContainer,
                                                "No time capsules yet!\nSeal your first letter 💌");
                                        return;
                                    }

                                    for (int i = 0; i < letters.length(); i++) {
                                        JSONObject l = letters.getJSONObject(i);
                                        addFutureLetterView(
                                                l.getInt("id"),
                                                l.getString("content"),
                                                l.getString("unlock_date"),
                                                l.getBoolean("is_unlocked"),
                                                l.getString("created_at")
                                        );
                                    }
                                }
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(ProfileActivity.this,
                                        "Failed to load letters",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void addThoughtView(int id, String content,
                                String mood, String createdAt) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackgroundResource(R.drawable.card_dark);
        card.setPadding(32, 24, 32, 24);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, 0, 0, 16);
        card.setLayoutParams(params);

        // Mood row
        LinearLayout moodRow = new LinearLayout(this);
        moodRow.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams rowParams =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
        rowParams.setMargins(0, 0, 0, 8);
        moodRow.setLayoutParams(rowParams);

        TextView tvMood = new TextView(this);
        tvMood.setText(mood);
        tvMood.setTextColor(0xFFB388FF);
        tvMood.setTextSize(12);
        LinearLayout.LayoutParams moodParams =
                new LinearLayout.LayoutParams(0,
                        LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        tvMood.setLayoutParams(moodParams);

        TextView tvDate = new TextView(this);
        tvDate.setText(createdAt.length() > 10
                ? createdAt.substring(0, 10) : createdAt);
        tvDate.setTextColor(0xFF555555);
        tvDate.setTextSize(11);
        moodRow.addView(tvMood);
        moodRow.addView(tvDate);
        card.addView(moodRow);

        // Content
        TextView tvContent = new TextView(this);
        tvContent.setText(content);
        tvContent.setTextColor(0xFFFFFFFF);
        tvContent.setTextSize(14);
        LinearLayout.LayoutParams contentParams =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
        contentParams.setMargins(0, 0, 0, 12);
        tvContent.setLayoutParams(contentParams);
        card.addView(tvContent);

        // Delete button
        TextView btnDelete = new TextView(this);
        btnDelete.setText("🗑 Release thought");
        btnDelete.setTextColor(0xFFFF5252);
        btnDelete.setTextSize(12);
        btnDelete.setOnClickListener(v -> deleteThought(id));
        card.addView(btnDelete);

        thoughtContainer.addView(card);
    }

    private void addFutureLetterView(int id, String content,
                                     String unlockDate,
                                     boolean isUnlocked,
                                     String createdAt) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackgroundResource(R.drawable.card_dark);
        card.setPadding(32, 24, 32, 24);
        LinearLayout.LayoutParams params =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, 0, 0, 16);
        card.setLayoutParams(params);

        // Lock status
        TextView tvStatus = new TextView(this);
        if (isUnlocked) {
            tvStatus.setText("💌 UNLOCKED - Open your letter!");
            tvStatus.setTextColor(0xFF4CAF50);
        } else {
            tvStatus.setText("🔒 SEALED - Opens on " + unlockDate);
            tvStatus.setTextColor(0xFFB388FF);
        }
        tvStatus.setTextSize(12);
        tvStatus.setTypeface(null, android.graphics.Typeface.BOLD);
        LinearLayout.LayoutParams statusParams =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
        statusParams.setMargins(0, 0, 0, 8);
        tvStatus.setLayoutParams(statusParams);
        card.addView(tvStatus);

        // Content - show only if unlocked
        TextView tvContent = new TextView(this);
        if (isUnlocked) {
            tvContent.setText(content);
            tvContent.setTextColor(0xFFFFFFFF);
        } else {
            tvContent.setText("████████████████\n███████████\n████████");
            tvContent.setTextColor(0xFF333333);
        }
        tvContent.setTextSize(14);
        LinearLayout.LayoutParams contentParams =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);
        contentParams.setMargins(0, 0, 0, 12);
        tvContent.setLayoutParams(contentParams);
        card.addView(tvContent);

        // Date sent
        TextView tvSent = new TextView(this);
        tvSent.setText("Sent: " + (createdAt.length() > 10
                ? createdAt.substring(0, 10) : createdAt));
        tvSent.setTextColor(0xFF555555);
        tvSent.setTextSize(11);
        card.addView(tvSent);

        futureContainer.addView(card);
    }

    private void addEmptyView(LinearLayout container, String message) {
        TextView empty = new TextView(this);
        empty.setText(message);
        empty.setTextColor(0xFF888888);
        empty.setTextSize(14);
        empty.setGravity(android.view.Gravity.CENTER);
        empty.setPadding(32, 48, 32, 32);
        container.addView(empty);
    }

    private void deleteThought(int id) {
        ApiClient.getService().deleteMemory(token, id)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            if (response.isSuccessful()) {
                                Toast.makeText(ProfileActivity.this,
                                        "Thought released! 🌬️",
                                        Toast.LENGTH_SHORT).show();
                                loadThoughts();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                    }
                });
    }
}