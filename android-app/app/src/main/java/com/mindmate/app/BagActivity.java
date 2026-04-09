package com.mindmate.app;

import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

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

public class BagActivity extends AppCompatActivity {

    TextView navChat, navPlanner, navMemories, navProfile;
    TextView dayMon, dayTue, dayWed, dayThu, dayFri, daySat;
    TextView tvProgressLabel, tvProgressCount, btnAddItem;
    TextView catAll, catBooks, catStationery, catLab, catPersonal;
    ProgressBar progressBar;
    LinearLayout bagContainer;
    String token;
    String selectedDay = "Monday";
    String selectedCategory = "all";
    String selectedItemCategory = "Books";
    Handler mainHandler = new Handler(Looper.getMainLooper());

    List<JSONObject> allItems = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bag);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        // Init views
        tvProgressLabel = findViewById(R.id.tvProgressLabel);
        tvProgressCount = findViewById(R.id.tvProgressCount);
        progressBar = findViewById(R.id.progressBar);
        btnAddItem = findViewById(R.id.btnAddItem);
        dayMon = findViewById(R.id.dayMon);
        dayTue = findViewById(R.id.dayTue);
        dayWed = findViewById(R.id.dayWed);
        dayThu = findViewById(R.id.dayThu);
        dayFri = findViewById(R.id.dayFri);
        daySat = findViewById(R.id.daySat);
        catAll = findViewById(R.id.catAll);
        catBooks = findViewById(R.id.catBooks);
        catStationery = findViewById(R.id.catStationery);
        catLab = findViewById(R.id.catLab);
        catPersonal = findViewById(R.id.catPersonal);
        navChat = findViewById(R.id.navChat);
        navPlanner = findViewById(R.id.navPlanner);
        navMemories = findViewById(R.id.navMemories);
        navProfile = findViewById(R.id.navProfile);

        // Setup bag container inside scrollview
        bagContainer = new LinearLayout(this);
        bagContainer.setOrientation(LinearLayout.VERTICAL);
        bagContainer.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));

        ScrollView scrollView = findViewById(R.id.rvBagItems);
        scrollView.addView(bagContainer);

        // Load default day - Monday
        loadBagItems(selectedDay);
        highlightDay(dayMon);

        // Day clicks
        dayMon.setOnClickListener(v -> {
            selectedDay = "Monday";
            loadBagItems(selectedDay);
            highlightDay(dayMon);
        });
        dayTue.setOnClickListener(v -> {
            selectedDay = "Tuesday";
            loadBagItems(selectedDay);
            highlightDay(dayTue);
        });
        dayWed.setOnClickListener(v -> {
            selectedDay = "Wednesday";
            loadBagItems(selectedDay);
            highlightDay(dayWed);
        });
        dayThu.setOnClickListener(v -> {
            selectedDay = "Thursday";
            loadBagItems(selectedDay);
            highlightDay(dayThu);
        });
        dayFri.setOnClickListener(v -> {
            selectedDay = "Friday";
            loadBagItems(selectedDay);
            highlightDay(dayFri);
        });
        daySat.setOnClickListener(v -> {
            selectedDay = "Saturday";
            loadBagItems(selectedDay);
            highlightDay(daySat);
        });

        // Category filter clicks
        catAll.setOnClickListener(v -> {
            selectedCategory = "all";
            updateCategoryChips(catAll);
            displayItems(allItems);
        });
        catBooks.setOnClickListener(v -> {
            selectedCategory = "books";
            updateCategoryChips(catBooks);
            filterByCategory("books");
        });
        catStationery.setOnClickListener(v -> {
            selectedCategory = "stationery";
            updateCategoryChips(catStationery);
            filterByCategory("stationery");
        });
        catLab.setOnClickListener(v -> {
            selectedCategory = "lab";
            updateCategoryChips(catLab);
            filterByCategory("lab");
        });
        catPersonal.setOnClickListener(v -> {
            selectedCategory = "personal";
            updateCategoryChips(catPersonal);
            filterByCategory("personal");
        });

        // Add item button
        btnAddItem.setOnClickListener(v -> showAddItemDialog());

        // Navigation
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

    private void highlightDay(TextView selected) {
        dayMon.setBackgroundResource(R.drawable.chip_dark);
        dayTue.setBackgroundResource(R.drawable.chip_dark);
        dayWed.setBackgroundResource(R.drawable.chip_dark);
        dayThu.setBackgroundResource(R.drawable.chip_dark);
        dayFri.setBackgroundResource(R.drawable.chip_dark);
        daySat.setBackgroundResource(R.drawable.chip_dark);
        selected.setBackgroundResource(R.drawable.chip_purple);

        String shortDay = selectedDay.substring(0, 3).toUpperCase();
        tvProgressLabel.setText(shortDay + " CHECKLIST");
    }

    private void updateCategoryChips(TextView selected) {
        catAll.setBackgroundResource(R.drawable.chip_dark);
        catBooks.setBackgroundResource(R.drawable.chip_dark);
        catStationery.setBackgroundResource(R.drawable.chip_dark);
        catLab.setBackgroundResource(R.drawable.chip_dark);
        catPersonal.setBackgroundResource(R.drawable.chip_dark);
        selected.setBackgroundResource(R.drawable.chip_purple);
    }

    private void filterByCategory(String category) {
        List<JSONObject> filtered = new ArrayList<>();
        for (JSONObject item : allItems) {
            try {
                String itemCat = item.optString(
                        "category", "personal").toLowerCase();
                if (itemCat.equals(category)) {
                    filtered.add(item);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        displayItems(filtered);
    }

    private String getEmojiForItem(String itemName) {
        String name = itemName.toLowerCase();
        if (name.contains("notebook") || name.contains("book")
                || name.contains("record")) return "📓";
        if (name.contains("pen") || name.contains("pencil")) return "✏️";
        if (name.contains("water")) return "💧";
        if (name.contains("id") || name.contains("card")) return "🪪";
        if (name.contains("lab") || name.contains("coat")) return "🥼";
        if (name.contains("calculator")) return "🔢";
        if (name.contains("phone")) return "📱";
        if (name.contains("charger")) return "🔌";
        if (name.contains("lunch") || name.contains("food")) return "🍱";
        if (name.contains("umbrella")) return "☂️";
        if (name.contains("bag") || name.contains("backpack")) return "🎒";
        if (name.contains("glasses")) return "👓";
        if (name.contains("headphone")
                || name.contains("earphone")) return "🎧";
        if (name.contains("key")) return "🔑";
        if (name.contains("mask")) return "😷";
        if (name.contains("sanitizer")) return "🧴";
        return "📦";
    }

    private String getEmojiForCategory(String category) {
        if (category == null) return "📦";
        switch (category.toLowerCase()) {
            case "books": return "📚";
            case "stationery": return "✏️";
            case "lab": return "🧪";
            case "personal": return "👤";
            default: return "📦";
        }
    }

    private void loadBagItems(String day) {
        bagContainer.removeAllViews();
        allItems.clear();

        ApiClient.getService().getBagItems(token, day)
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
                                    JSONArray items = obj.getJSONArray("items");
                                    int total = obj.getInt("total");
                                    int checked = obj.getInt("checked");

                                    allItems.clear();
                                    for (int i = 0; i < items.length(); i++) {
                                        allItems.add(items.getJSONObject(i));
                                    }

                                    updateProgress(checked, total);
                                    displayItems(allItems);
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
                                Toast.makeText(BagActivity.this,
                                        "Failed to load items",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void updateProgress(int checked, int total) {
        tvProgressCount.setText(checked + "/" + total + " packed");
        if (total > 0) {
            int progress = (checked * 100) / total;
            progressBar.setProgress(progress);
        } else {
            progressBar.setProgress(0);
        }
    }

    private void displayItems(List<JSONObject> items) {
        bagContainer.removeAllViews();

        if (items.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText("No items here!\nTap + to add items 🎒");
            empty.setTextColor(0xFF888888);
            empty.setTextSize(14);
            empty.setGravity(android.view.Gravity.CENTER);
            empty.setPadding(32, 64, 32, 32);
            bagContainer.addView(empty);
            return;
        }

        for (JSONObject item : items) {
            try {
                addBagItemView(
                        item.getInt("id"),
                        item.getString("item_name"),
                        item.optString("category", "personal"),
                        item.getString("is_checked").equals("true")
                );
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void addBagItemView(int id, String name,
                                String category, boolean isChecked) {
        View itemView = LayoutInflater.from(this)
                .inflate(R.layout.item_bag, bagContainer, false);

        TextView tvEmoji = itemView.findViewById(R.id.tvItemEmoji);
        TextView tvName = itemView.findViewById(R.id.tvBagItemName);
        TextView tvCategory = itemView.findViewById(R.id.tvItemCategory);
        TextView btnDelete = itemView.findViewById(R.id.btnDeleteItem);
        CheckBox checkBox = itemView.findViewById(R.id.checkBagItem);

        tvEmoji.setText(getEmojiForItem(name));
        tvName.setText(name);
        tvCategory.setText(getEmojiForCategory(category)
                + " " + category.toUpperCase());
        checkBox.setChecked(isChecked);

        if (isChecked) {
            tvName.setPaintFlags(tvName.getPaintFlags()
                    | android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);
            tvName.setTextColor(0xFF555555);
        } else {
            tvName.setPaintFlags(tvName.getPaintFlags()
                    & ~android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);
            tvName.setTextColor(0xFFFFFFFF);
        }

        checkBox.setOnCheckedChangeListener((btn, checked) -> {
            if (checked) {
                tvName.setPaintFlags(tvName.getPaintFlags()
                        | android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);
                tvName.setTextColor(0xFF555555);
            } else {
                tvName.setPaintFlags(tvName.getPaintFlags()
                        & ~android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);
                tvName.setTextColor(0xFFFFFFFF);
            }
            updateItemCheck(id, checked);
        });

        // Long press to delete
        itemView.setOnLongClickListener(v -> {
            showDeleteConfirm(id, name);
            return true;
        });

        // Delete button click
        btnDelete.setOnClickListener(v -> showDeleteConfirm(id, name));

        bagContainer.addView(itemView);
    }

    private void showDeleteConfirm(int id, String name) {
        new AlertDialog.Builder(this)
                .setTitle("Remove Item?")
                .setMessage("Remove \""
                        + name + "\" from "
                        + selectedDay + "'s bag?")
                .setPositiveButton("Remove", (dialog, which) ->
                        deleteItem(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteItem(int itemId) {
        // FIXED: use deleteBagItem not deleteTask
        ApiClient.getService().deleteBagItem(token, itemId)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            if (response.isSuccessful()) {
                                Toast.makeText(BagActivity.this,
                                        "Item removed ✅",
                                        Toast.LENGTH_SHORT).show();
                                loadBagItems(selectedDay);
                            } else {
                                Toast.makeText(BagActivity.this,
                                        "Failed to remove!",
                                        Toast.LENGTH_SHORT).show();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(BagActivity.this,
                                        "Connection failed!",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void showAddItemDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        View dialogView = LayoutInflater.from(this)
                .inflate(R.layout.dialog_add_bag_item, null);
        builder.setView(dialogView);

        EditText etItemName = dialogView.findViewById(R.id.etItemName);
        TextView dCatBooks = dialogView.findViewById(R.id.catBooks);
        TextView dCatStationery = dialogView.findViewById(R.id.catStationery);
        TextView dCatLab = dialogView.findViewById(R.id.catLab);
        TextView dCatPersonal = dialogView.findViewById(R.id.catPersonal);

        // Default selected
        selectedItemCategory = "Books";
        dCatBooks.setBackgroundResource(R.drawable.chip_purple);

        dCatBooks.setOnClickListener(v -> {
            selectedItemCategory = "Books";
            dCatBooks.setBackgroundResource(R.drawable.chip_purple);
            dCatStationery.setBackgroundResource(R.drawable.chip_dark);
            dCatLab.setBackgroundResource(R.drawable.chip_dark);
            dCatPersonal.setBackgroundResource(R.drawable.chip_dark);
        });
        dCatStationery.setOnClickListener(v -> {
            selectedItemCategory = "Stationery";
            dCatBooks.setBackgroundResource(R.drawable.chip_dark);
            dCatStationery.setBackgroundResource(R.drawable.chip_purple);
            dCatLab.setBackgroundResource(R.drawable.chip_dark);
            dCatPersonal.setBackgroundResource(R.drawable.chip_dark);
        });
        dCatLab.setOnClickListener(v -> {
            selectedItemCategory = "Lab";
            dCatBooks.setBackgroundResource(R.drawable.chip_dark);
            dCatStationery.setBackgroundResource(R.drawable.chip_dark);
            dCatLab.setBackgroundResource(R.drawable.chip_purple);
            dCatPersonal.setBackgroundResource(R.drawable.chip_dark);
        });
        dCatPersonal.setOnClickListener(v -> {
            selectedItemCategory = "Personal";
            dCatBooks.setBackgroundResource(R.drawable.chip_dark);
            dCatStationery.setBackgroundResource(R.drawable.chip_dark);
            dCatLab.setBackgroundResource(R.drawable.chip_dark);
            dCatPersonal.setBackgroundResource(R.drawable.chip_purple);
        });

        builder.setTitle("Add to " + selectedDay + "'s Bag 🎒");
        builder.setPositiveButton("Add ✅", (dialog, which) -> {
            String itemName = etItemName.getText().toString().trim();
            if (itemName.isEmpty()) {
                Toast.makeText(this,
                        "Please enter item name!",
                        Toast.LENGTH_SHORT).show();
                return;
            }
            addBagItem(itemName, selectedItemCategory);
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void addBagItem(String itemName, String category) {
        try {
            JSONObject json = new JSONObject();
            json.put("day", selectedDay);
            json.put("item_name", itemName);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    json.toString()
            );

            // FIXED: use addBagItem not addTask
            ApiClient.getService().addBagItem(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call,
                                               Response<ResponseBody> response) {
                            mainHandler.post(() -> {
                                if (response.isSuccessful()) {
                                    Toast.makeText(BagActivity.this,
                                            getEmojiForItem(itemName)
                                                    + " "
                                                    + itemName
                                                    + " added to bag!",
                                            Toast.LENGTH_SHORT).show();
                                    loadBagItems(selectedDay);
                                } else {
                                    Toast.makeText(BagActivity.this,
                                            "Item already exists for "
                                                    + selectedDay + "!",
                                            Toast.LENGTH_SHORT).show();
                                }
                            });
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call,
                                              Throwable t) {
                            mainHandler.post(() ->
                                    Toast.makeText(BagActivity.this,
                                            "Connection failed!",
                                            Toast.LENGTH_SHORT).show());
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void updateItemCheck(int itemId, boolean checked) {
        try {
            JSONObject json = new JSONObject();
            json.put("is_checked", checked ? "true" : "false");

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    json.toString()
            );

            ApiClient.getService().checkBagItem(token, itemId, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call,
                                               Response<ResponseBody> response) {
                            mainHandler.post(() ->
                                    loadBagItems(selectedDay));
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call,
                                              Throwable t) {
                            mainHandler.post(() ->
                                    Toast.makeText(BagActivity.this,
                                            "Update failed!",
                                            Toast.LENGTH_SHORT).show());
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}