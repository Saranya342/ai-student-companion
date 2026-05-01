package com.mindmate.app;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.mindmate.app.network.ApiClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Calendar;
import java.util.Locale;

import okhttp3.MediaType;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class JournalActivity extends AppCompatActivity {

    private TextView tabThought, tabFuture;
    private LinearLayout thoughtLayout, futureLayout;

    private EditText etThought;
    private TextView btnSendThought;
    private LinearLayout thoughtContainer;

    private EditText etFuture;
    private Button btnSendFuture;
    private LinearLayout futureContainer;

    private String token;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_journal);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        tabThought = findViewById(R.id.tabThought);
        tabFuture = findViewById(R.id.tabFuture);
        thoughtLayout = findViewById(R.id.thoughtLayout);
        futureLayout = findViewById(R.id.futureLayout);

        etThought = findViewById(R.id.etThought);
        btnSendThought = findViewById(R.id.btnSendThought);
        thoughtContainer = findViewById(R.id.thoughtContainer);

        etFuture = findViewById(R.id.etFuture);
        btnSendFuture = findViewById(R.id.btnSendFuture);
        futureContainer = findViewById(R.id.futureContainer);

        BottomNavigationView bottomNav = findViewById(R.id.bottomNav);
        BottomNavHelper.setup(bottomNav, this, R.id.nav_journal);

        tabThought.setOnClickListener(v -> showThought());
        tabFuture.setOnClickListener(v -> showFuture());

        btnSendThought.setOnClickListener(v -> {
            String text = etThought.getText().toString().trim();
            if (text.isEmpty()) {
                Toast.makeText(this, "Type a thought first", Toast.LENGTH_SHORT).show();
                return;
            }
            addThought(text);
        });

        btnSendFuture.setOnClickListener(v -> {
            String text = etFuture.getText().toString().trim();
            if (text.isEmpty()) {
                Toast.makeText(this, "Write something first", Toast.LENGTH_SHORT).show();
                return;
            }
            addFutureLetter(text);
        });

        showThought();
        loadThoughts();
        loadFutureLetters();
    }

    private void showThought() {
        thoughtLayout.setVisibility(View.VISIBLE);
        futureLayout.setVisibility(View.GONE);
        tabThought.setBackgroundResource(R.drawable.chip_purple);
        tabFuture.setBackgroundResource(R.drawable.chip_dark);
    }

    private void showFuture() {
        thoughtLayout.setVisibility(View.GONE);
        futureLayout.setVisibility(View.VISIBLE);
        tabThought.setBackgroundResource(R.drawable.chip_dark);
        tabFuture.setBackgroundResource(R.drawable.chip_purple);
    }

    private void loadThoughts() {
        ApiClient.getService().getThoughtParking(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                        try {
                            if (!response.isSuccessful() || response.body() == null) return;
                            String json = response.body().string();
                            JSONObject obj = new JSONObject(json);
                            JSONArray thoughts = obj.getJSONArray("thoughts");
                            thoughtContainer.removeAllViews();

                            for (int i = 0; i < thoughts.length(); i++) {
                                JSONObject t = thoughts.getJSONObject(i);
                                int id = t.getInt("id");
                                String content = t.getString("content");
                                String createdAt = t.optString("created_at", "");
                                addThoughtCard(id, content, createdAt);
                            }
                        } catch (Exception ignored) {}
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {}
                });
    }

    private void addThought(String content) {
        try {
            JSONObject json = new JSONObject();
            json.put("content", content);
            RequestBody body = RequestBody.create(MediaType.parse("application/json"), json.toString());

            ApiClient.getService().addThoughtParking(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                            if (response.isSuccessful()) {
                                etThought.setText("");
                                loadThoughts();
                            }
                        }
                        @Override
                        public void onFailure(Call<ResponseBody> call, Throwable t) {}
                    });
        } catch (Exception ignored) {}
    }

    private void addThoughtCard(int id, String content, String createdAt) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackgroundResource(R.drawable.card_dark);
        card.setPadding(28, 22, 28, 22);

        TextView tv = new TextView(this);
        tv.setText(content);
        tv.setTextColor(0xFFFFFFFF);
        tv.setTextSize(14);

        TextView del = new TextView(this);
        del.setText("Delete");
        del.setTextColor(0xFFFF5252);
        del.setPadding(0, 12, 0, 0);
        del.setOnClickListener(v -> confirmDeleteThought(id));

        card.addView(tv);
        card.addView(del);
        thoughtContainer.addView(card, 0);
    }

    private void confirmDeleteThought(int id) {
        new AlertDialog.Builder(this)
                .setTitle("Delete thought?")
                .setPositiveButton("Delete", (d, w) -> deleteThought(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteThought(int id) {
        ApiClient.getService().deleteThoughtParking(token, id)
                .enqueue(new Callback<ResponseBody>() {
                    @Override public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) { loadThoughts(); }
                    @Override public void onFailure(Call<ResponseBody> call, Throwable t) {}
                });
    }

    private void loadFutureLetters() {
        ApiClient.getService().getMemories(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                        try {
                            if (!response.isSuccessful() || response.body() == null) return;
                            String json = response.body().string();
                            JSONObject obj = new JSONObject(json);
                            JSONArray memories = obj.getJSONArray("memories");

                            futureContainer.removeAllViews();
                            for (int i = 0; i < memories.length(); i++) {
                                JSONObject m = memories.getJSONObject(i);
                                if (!"future".equalsIgnoreCase(m.optString("category",""))) continue;
                                addFutureCard(m.getInt("id"), m.optString("unlock_date",""));
                            }
                        } catch (Exception ignored) {}
                    }
                    @Override public void onFailure(Call<ResponseBody> call, Throwable t) {}
                });
    }

    private void addFutureLetter(String content) {
        try {
            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.DAY_OF_YEAR, 7);
            String unlockDate = String.format(Locale.getDefault(), "%04d-%02d-%02d",
                    cal.get(Calendar.YEAR), cal.get(Calendar.MONTH) + 1, cal.get(Calendar.DAY_OF_MONTH));

            JSONObject json = new JSONObject();
            json.put("content", content);
            json.put("category", "future");
            json.put("unlock_date", unlockDate);

            RequestBody body = RequestBody.create(MediaType.parse("application/json"), json.toString());

            ApiClient.getService().addMemory(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                            if (response.isSuccessful()) { etFuture.setText(""); loadFutureLetters(); }
                        }
                        @Override public void onFailure(Call<ResponseBody> call, Throwable t) {}
                    });
        } catch (Exception ignored) {}
    }

    private void addFutureCard(int id, String unlockDate) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackgroundResource(R.drawable.card_dark);
        card.setPadding(24, 18, 24, 18);

        TextView title = new TextView(this);
        title.setText("Opens on: " + (unlockDate.isEmpty() ? "Locked" : unlockDate));
        title.setTextColor(0xFFB388FF);

        TextView del = new TextView(this);
        del.setText("Delete");
        del.setTextColor(0xFFFF5252);
        del.setPadding(0, 12, 0, 0);
        del.setOnClickListener(v -> confirmDeleteFuture(id));

        card.addView(title);
        card.addView(del);
        futureContainer.addView(card, 0);
    }

    private void confirmDeleteFuture(int id) {
        new AlertDialog.Builder(this)
                .setTitle("Delete future letter?")
                .setPositiveButton("Delete", (d, w) -> deleteFuture(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteFuture(int id) {
        ApiClient.getService().deleteMemory(token, id)
                .enqueue(new Callback<ResponseBody>() {
                    @Override public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) { loadFutureLetters(); }
                    @Override public void onFailure(Call<ResponseBody> call, Throwable t) {}
                });
    }
    @Override
    protected void onResume() {
        super.onResume();
        loadThoughts();
        loadFutureLetters();
    }
}