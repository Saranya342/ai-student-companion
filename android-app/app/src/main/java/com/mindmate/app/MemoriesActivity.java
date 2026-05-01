package com.mindmate.app;

import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.mindmate.app.network.ApiClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import okhttp3.MediaType;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MemoriesActivity extends AppCompatActivity {

    TextView tvMemoryCount, btnSearch, btnCancelSearch;
    LinearLayout searchLayout;
    EditText etSearch;
    Button btnAddMemory;

    TextView chipAll, chipAchievement, chipWin, chipGrowth, chipNote;
    LinearLayout memoryContainer;

    String token;
    String selectedCategory = "all";
    List<JSONObject> allMemories = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_memories);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        tvMemoryCount = findViewById(R.id.tvMemoryCount);
        btnSearch = findViewById(R.id.btnSearch);
        searchLayout = findViewById(R.id.searchLayout);
        etSearch = findViewById(R.id.etSearch);
        btnCancelSearch = findViewById(R.id.btnCancelSearch);
        btnAddMemory = findViewById(R.id.btnAddMemory);

        chipAll = findViewById(R.id.chipAll);
        chipAchievement = findViewById(R.id.chipAchievement);
        chipWin = findViewById(R.id.chipWin);
        chipGrowth = findViewById(R.id.chipGrowth);
        chipNote = findViewById(R.id.chipNote);

        ScrollView scroll = findViewById(R.id.rvMemories);
        memoryContainer = new LinearLayout(this);
        memoryContainer.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(memoryContainer);

        BottomNavigationView bottomNav = findViewById(R.id.bottomNav);
        BottomNavHelper.setup(bottomNav, this, R.id.nav_profile);

        btnSearch.setOnClickListener(v -> {
            searchLayout.setVisibility(View.VISIBLE);
            etSearch.requestFocus();
        });

        btnCancelSearch.setOnClickListener(v -> {
            searchLayout.setVisibility(View.GONE);
            etSearch.setText("");
            applyFiltersAndRender();
        });

        etSearch.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void afterTextChanged(Editable s) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                applyFiltersAndRender();
            }
        });

        chipAll.setOnClickListener(v -> { selectedCategory = "all"; applyFiltersAndRender(); });
        chipAchievement.setOnClickListener(v -> { selectedCategory = "achievement"; applyFiltersAndRender(); });
        chipWin.setOnClickListener(v -> { selectedCategory = "win"; applyFiltersAndRender(); });
        chipGrowth.setOnClickListener(v -> { selectedCategory = "growth"; applyFiltersAndRender(); });
        chipNote.setOnClickListener(v -> { selectedCategory = "note"; applyFiltersAndRender(); });

        btnAddMemory.setOnClickListener(v -> showAddMemoryDialog());

        loadMemories();
    }

    private void loadMemories() {
        tvMemoryCount.setText("Loading...");

        ApiClient.getService().getMemories(token).enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                try {
                    if (!response.isSuccessful() || response.body() == null) {
                        tvMemoryCount.setText("Failed to load");
                        return;
                    }

                    String json = response.body().string();
                    JSONObject obj = new JSONObject(json);
                    JSONArray arr = obj.getJSONArray("memories");

                    allMemories.clear();
                    for (int i = 0; i < arr.length(); i++) allMemories.add(arr.getJSONObject(i));

                    tvMemoryCount.setText(allMemories.size() + " saved");
                    applyFiltersAndRender();
                } catch (Exception e) {
                    tvMemoryCount.setText("Error");
                }
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                tvMemoryCount.setText("Connection failed");
            }
        });
    }

    private void applyFiltersAndRender() {
        String query = etSearch.getText().toString().trim().toLowerCase();
        List<JSONObject> filtered = new ArrayList<>();

        for (JSONObject m : allMemories) {
            String category = m.optString("category", "").toLowerCase();
            String content = m.optString("content", "");

            if (!selectedCategory.equals("all") && !category.equals(selectedCategory)) continue;
            if (!query.isEmpty() && !content.toLowerCase().contains(query)) continue;

            filtered.add(m);
        }
        renderMemories(filtered);
    }

    private void renderMemories(List<JSONObject> list) {
        memoryContainer.removeAllViews();

        if (list.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText("No memories found. Add one using +");
            empty.setTextColor(0xFF888888);
            empty.setPadding(32, 64, 32, 32);
            memoryContainer.addView(empty);
            return;
        }

        for (JSONObject m : list) {
            try {
                int id = m.getInt("id");
                String content = m.getString("content");
                String category = m.optString("category", "note");
                String createdAt = m.optString("created_at", "");

                View item = LayoutInflater.from(this).inflate(R.layout.item_memory, memoryContainer, false);
                TextView tvCategory = item.findViewById(R.id.tvMemoryCategory);
                TextView tvDate = item.findViewById(R.id.tvMemoryDate);
                TextView tvContent = item.findViewById(R.id.tvMemoryContent);
                TextView btnDelete = item.findViewById(R.id.btnDeleteMemory);
                TextView btnShare = item.findViewById(R.id.btnShareMemory);

                tvCategory.setText(category.toUpperCase());
                tvDate.setText(createdAt.length() >= 10 ? createdAt.substring(0,10) : createdAt);
                tvContent.setText(content);

                btnShare.setOnClickListener(v -> shareMemory(content, category));
                btnDelete.setOnClickListener(v -> confirmDelete(id));

                memoryContainer.addView(item);

            } catch (Exception ignored) {}
        }
    }

    private void showAddMemoryDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Add Memory");

        View dialog = LayoutInflater.from(this).inflate(R.layout.dialog_add_memory, null);
        builder.setView(dialog);

        EditText etContent = dialog.findViewById(R.id.etMemoryContent);

        builder.setPositiveButton("Save", (d, w) -> {
            String content = etContent.getText().toString().trim();
            if (content.isEmpty()) {
                Toast.makeText(this, "Enter something", Toast.LENGTH_SHORT).show();
                return;
            }
            addMemory(content, "note");
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void addMemory(String content, String category) {
        try {
            JSONObject json = new JSONObject();
            json.put("content", content);
            json.put("category", category);

            RequestBody body = RequestBody.create(MediaType.parse("application/json"), json.toString());

            ApiClient.getService().addMemory(token, body).enqueue(new Callback<ResponseBody>() {
                @Override public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) { loadMemories(); }
                @Override public void onFailure(Call<ResponseBody> call, Throwable t) {}
            });
        } catch (Exception ignored) {}
    }

    private void confirmDelete(int id) {
        new AlertDialog.Builder(this)
                .setTitle("Delete memory?")
                .setMessage("This cannot be undone.")
                .setPositiveButton("Delete", (d, w) -> deleteMemory(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteMemory(int id) {
        ApiClient.getService().deleteMemory(token, id).enqueue(new Callback<ResponseBody>() {
            @Override public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) { loadMemories(); }
            @Override public void onFailure(Call<ResponseBody> call, Throwable t) {}
        });
    }

    private void shareMemory(String content, String category) {
        String text = "MindMate - " + category.toUpperCase() + "\n\n" + content;
        Intent share = new Intent(Intent.ACTION_SEND);
        share.setType("text/plain");
        share.putExtra(Intent.EXTRA_TEXT, text);
        startActivity(Intent.createChooser(share, "Share Memory"));
    }
}