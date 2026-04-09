package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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
import android.app.AlertDialog;
import android.content.Intent;

import androidx.appcompat.app.AppCompatActivity;

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

    TextView navChat, navPlanner, navBag, navProfile;
    TextView btnSearch, btnCancelSearch;
    TextView chipAll, chipWin, chipStudy, chipGrowth, chipNote;
    TextView tvMemoryCount;
    Button btnAddMemory;
    EditText etSearch;
    LinearLayout searchLayout, memoryContainer;
    String token;
    String selectedCategory = "all";
    Handler mainHandler = new Handler(Looper.getMainLooper());

    // Store all memories for filtering
    List<JSONObject> allMemories = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_memories);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        // Init views
        tvMemoryCount = findViewById(R.id.tvMemoryCount);
        btnAddMemory = findViewById(R.id.btnAddMemory);
        btnSearch = findViewById(R.id.btnSearch);
        btnCancelSearch = findViewById(R.id.btnCancelSearch);
        etSearch = findViewById(R.id.etSearch);
        searchLayout = findViewById(R.id.searchLayout);
        chipAll = findViewById(R.id.chipAll);
        chipWin = findViewById(R.id.chipWin);
        chipStudy = findViewById(R.id.chipStudy);
        chipGrowth = findViewById(R.id.chipGrowth);
        chipNote = findViewById(R.id.chipNote);
        navChat = findViewById(R.id.navChat);
        navPlanner = findViewById(R.id.navPlanner);
        navBag = findViewById(R.id.navBag);
        navProfile = findViewById(R.id.navProfile);

        // Setup memory container inside scrollview
        memoryContainer = new LinearLayout(this);
        memoryContainer.setOrientation(LinearLayout.VERTICAL);
        memoryContainer.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        ScrollView scrollView = findViewById(R.id.rvMemories);
        scrollView.addView(memoryContainer);

        // Load memories
        loadMemories();

        // Search toggle
        btnSearch.setOnClickListener(v -> {
            searchLayout.setVisibility(View.VISIBLE);
            etSearch.requestFocus();
        });

        btnCancelSearch.setOnClickListener(v -> {
            searchLayout.setVisibility(View.GONE);
            etSearch.setText("");
            displayMemories(allMemories);
        });

        // Search text watcher
        etSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                filterMemories(s.toString());
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        // Category chips
        chipAll.setOnClickListener(v -> {
            selectedCategory = "all";
            updateChips(chipAll);
            displayMemories(allMemories);
        });
        chipWin.setOnClickListener(v -> {
            selectedCategory = "win";
            updateChips(chipWin);
            filterByCategory("win");
        });
        chipStudy.setOnClickListener(v -> {
            selectedCategory = "study";
            updateChips(chipStudy);
            filterByCategory("study");
        });
        chipGrowth.setOnClickListener(v -> {
            selectedCategory = "growth";
            updateChips(chipGrowth);
            filterByCategory("growth");
        });
        chipNote.setOnClickListener(v -> {
            selectedCategory = "note";
            updateChips(chipNote);
            filterByCategory("note");
        });

        // Add memory
        btnAddMemory.setOnClickListener(v -> showAddMemoryDialog());

        // Navigation
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

    private void updateChips(TextView selected) {
        chipAll.setBackgroundResource(R.drawable.chip_dark);
        chipWin.setBackgroundResource(R.drawable.chip_dark);
        chipStudy.setBackgroundResource(R.drawable.chip_dark);
        chipGrowth.setBackgroundResource(R.drawable.chip_dark);
        chipNote.setBackgroundResource(R.drawable.chip_dark);
        selected.setBackgroundResource(R.drawable.chip_purple);
    }

    private void filterByCategory(String category) {
        List<JSONObject> filtered = new ArrayList<>();
        for (JSONObject memory : allMemories) {
            try {
                if (memory.getString("category")
                        .equalsIgnoreCase(category)) {
                    filtered.add(memory);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        displayMemories(filtered);
    }

    private void filterMemories(String query) {
        if (query.isEmpty()) {
            displayMemories(allMemories);
            return;
        }
        List<JSONObject> filtered = new ArrayList<>();
        for (JSONObject memory : allMemories) {
            try {
                if (memory.getString("content")
                        .toLowerCase()
                        .contains(query.toLowerCase())) {
                    filtered.add(memory);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        displayMemories(filtered);
    }

    private void loadMemories() {
        ApiClient.getService().getMemories(token)
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
                                    JSONArray memories =
                                            obj.getJSONArray("memories");

                                    allMemories.clear();
                                    for (int i = 0; i < memories.length(); i++) {
                                        allMemories.add(
                                                memories.getJSONObject(i));
                                    }

                                    tvMemoryCount.setText(
                                            allMemories.size()
                                                    + " memories saved");
                                    displayMemories(allMemories);
                                }
                            } catch (Exception e) {
                                e.printStackTrace();
                                Toast.makeText(MemoriesActivity.this,
                                        "Error loading memories",
                                        Toast.LENGTH_SHORT).show();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(MemoriesActivity.this,
                                        "Connection failed!",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void displayMemories(List<JSONObject> memories) {
        memoryContainer.removeAllViews();

        if (memories.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText("No memories found!\nAdd your proud moments ✨");
            empty.setTextColor(0xFF888888);
            empty.setTextSize(14);
            empty.setGravity(android.view.Gravity.CENTER);
            empty.setPadding(32, 64, 32, 32);
            memoryContainer.addView(empty);
            return;
        }

        for (JSONObject memory : memories) {
            try {
                addMemoryView(
                        memory.getInt("id"),
                        memory.getString("content"),
                        memory.getString("category"),
                        memory.getString("created_at")
                );
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void addMemoryView(int id, String content,
                               String category, String createdAt) {
        View itemView = LayoutInflater.from(this)
                .inflate(R.layout.item_memory, memoryContainer, false);

        TextView tvContent = itemView.findViewById(R.id.tvMemoryContent);
        TextView tvCategory = itemView.findViewById(R.id.tvMemoryCategory);
        TextView tvDate = itemView.findViewById(R.id.tvMemoryDate);
        TextView tvEmoji = itemView.findViewById(R.id.tvMemoryEmoji);
        TextView btnShare = itemView.findViewById(R.id.btnShareMemory);
        TextView btnDelete = itemView.findViewById(R.id.btnDeleteMemory);

        tvContent.setText(content);
        tvCategory.setText(category.toUpperCase());

        // Date formatting
        if (createdAt.length() > 10) {
            tvDate.setText(createdAt.substring(0, 10));
        } else {
            tvDate.setText(createdAt);
        }

        // Set emoji + color based on category
        switch (category.toLowerCase()) {
            case "win":
                tvEmoji.setText("🏆");
                tvCategory.setTextColor(0xFFFFD700);
                break;
            case "study":
                tvEmoji.setText("📚");
                tvCategory.setTextColor(0xFF00BCD4);
                break;
            case "growth":
                tvEmoji.setText("💪");
                tvCategory.setTextColor(0xFF4CAF50);
                break;
            case "note":
                tvEmoji.setText("📝");
                tvCategory.setTextColor(0xFFFF9800);
                break;
            case "chat":
                tvEmoji.setText("💬");
                tvCategory.setTextColor(0xFF7C4DFF);
                break;
            default:
                tvEmoji.setText("✨");
                tvCategory.setTextColor(0xFFB388FF);
                break;
        }

        // Share button
        btnShare.setOnClickListener(v -> shareMemory(content, category));

        // Delete button
        btnDelete.setOnClickListener(v ->
                showDeleteConfirm(id));

        memoryContainer.addView(itemView);
    }

    private void shareMemory(String content, String category) {
        String shareText = "✨ My " + category + " moment:\n\n"
                + content + "\n\n- via MindMate App";
        Intent shareIntent = new Intent(Intent.ACTION_SEND);
        shareIntent.setType("text/plain");
        shareIntent.putExtra(Intent.EXTRA_TEXT, shareText);
        startActivity(Intent.createChooser(shareIntent, "Share Memory"));
    }

    private void showDeleteConfirm(int id) {
        new AlertDialog.Builder(this)
                .setTitle("Delete Memory?")
                .setMessage("Are you sure you want to delete this memory?")
                .setPositiveButton("Delete", (dialog, which) ->
                        deleteMemory(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteMemory(int id) {
        ApiClient.getService().deleteMemory(token, id)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            if (response.isSuccessful()) {
                                Toast.makeText(MemoriesActivity.this,
                                        "Memory deleted ✅",
                                        Toast.LENGTH_SHORT).show();
                                loadMemories();
                            } else {
                                Toast.makeText(MemoriesActivity.this,
                                        "Delete failed!",
                                        Toast.LENGTH_SHORT).show();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(MemoriesActivity.this,
                                        "Connection failed!",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void showAddMemoryDialog() {
        AlertDialog.Builder builder =
                new AlertDialog.Builder(this);
        builder.setTitle("Add Proud Moment ✨");

        View dialogView = LayoutInflater.from(this)
                .inflate(R.layout.dialog_add_memory, null);
        builder.setView(dialogView);

        EditText etContent =
                dialogView.findViewById(R.id.etMemoryContent);

        // Category selection
        TextView catWin = dialogView.findViewById(R.id.catWin);
        TextView catStudy = dialogView.findViewById(R.id.catStudy);
        TextView catGrowth = dialogView.findViewById(R.id.catGrowth);
        TextView catNote = dialogView.findViewById(R.id.catNote);

        // Track selected category
        final String[] selectedCat = {"win"};

        catWin.setOnClickListener(v -> {
            selectedCat[0] = "win";
            catWin.setBackgroundResource(R.drawable.chip_purple);
            catStudy.setBackgroundResource(R.drawable.chip_dark);
            catGrowth.setBackgroundResource(R.drawable.chip_dark);
            catNote.setBackgroundResource(R.drawable.chip_dark);
        });
        catStudy.setOnClickListener(v -> {
            selectedCat[0] = "study";
            catWin.setBackgroundResource(R.drawable.chip_dark);
            catStudy.setBackgroundResource(R.drawable.chip_purple);
            catGrowth.setBackgroundResource(R.drawable.chip_dark);
            catNote.setBackgroundResource(R.drawable.chip_dark);
        });
        catGrowth.setOnClickListener(v -> {
            selectedCat[0] = "growth";
            catWin.setBackgroundResource(R.drawable.chip_dark);
            catStudy.setBackgroundResource(R.drawable.chip_dark);
            catGrowth.setBackgroundResource(R.drawable.chip_purple);
            catNote.setBackgroundResource(R.drawable.chip_dark);
        });
        catNote.setOnClickListener(v -> {
            selectedCat[0] = "note";
            catWin.setBackgroundResource(R.drawable.chip_dark);
            catStudy.setBackgroundResource(R.drawable.chip_dark);
            catGrowth.setBackgroundResource(R.drawable.chip_dark);
            catNote.setBackgroundResource(R.drawable.chip_purple);
        });

        builder.setPositiveButton("Add ✨", (dialog, which) -> {
            String content = etContent.getText().toString().trim();
            if (content.isEmpty()) {
                Toast.makeText(this,
                        "Please enter your moment!",
                        Toast.LENGTH_SHORT).show();
                return;
            }
            addMemory(content, selectedCat[0]);
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void addMemory(String content, String category) {
        try {
            JSONObject json = new JSONObject();
            json.put("content", content);
            json.put("category", category);

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
                                    Toast.makeText(MemoriesActivity.this,
                                            "Memory added! ✨",
                                            Toast.LENGTH_SHORT).show();
                                    loadMemories();
                                } else {
                                    Toast.makeText(MemoriesActivity.this,
                                            "Failed to add!",
                                            Toast.LENGTH_SHORT).show();
                                }
                            });
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call,
                                              Throwable t) {
                            mainHandler.post(() ->
                                    Toast.makeText(MemoriesActivity.this,
                                            "Connection failed!",
                                            Toast.LENGTH_SHORT).show());
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}