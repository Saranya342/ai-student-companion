package com.mindmate.app;

import android.app.AlertDialog;
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

public class BagActivity extends AppCompatActivity {

    TextView dayMon, dayTue, dayWed, dayThu, dayFri, daySat;
    TextView tvProgressLabel, tvProgressCount, btnAddItem;
    TextView catAll, catBooks, catStationery, catLab, catPersonal;
    ProgressBar progressBar;
    LinearLayout bagContainer;
    String token;
    String selectedDay = "Monday";
    Handler mainHandler = new Handler(Looper.getMainLooper());

    List<JSONObject> allItems = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bag);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

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

        bagContainer = new LinearLayout(this);
        bagContainer.setOrientation(LinearLayout.VERTICAL);

        ScrollView scrollView = findViewById(R.id.rvBagItems);
        scrollView.addView(bagContainer);

        BottomNavigationView bottomNav = findViewById(R.id.bottomNav);
        BottomNavHelper.setup(bottomNav, this, R.id.nav_bag);

        // ✅ Check if opened from chat with specific day
        String dayFromChat = getIntent().getStringExtra("selected_day");
        if (dayFromChat != null && !dayFromChat.isEmpty()) {
            selectedDay = dayFromChat;
        }

        loadBagItems(selectedDay);
        highlightCorrectDay();

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

        catAll.setOnClickListener(v -> displayItems(allItems));
        catBooks.setOnClickListener(v -> filterByCategory("books"));
        catStationery.setOnClickListener(v -> filterByCategory("stationery"));
        catLab.setOnClickListener(v -> filterByCategory("lab"));
        catPersonal.setOnClickListener(v -> filterByCategory("personal"));

        btnAddItem.setOnClickListener(v -> showAddItemDialog());
    }

    // ✅ Highlight the correct day button on open
    private void highlightCorrectDay() {
        switch (selectedDay) {
            case "Monday":    highlightDay(dayMon); break;
            case "Tuesday":   highlightDay(dayTue); break;
            case "Wednesday": highlightDay(dayWed); break;
            case "Thursday":  highlightDay(dayThu); break;
            case "Friday":    highlightDay(dayFri); break;
            case "Saturday":  highlightDay(daySat); break;
            default:          highlightDay(dayMon); break;
        }
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

    private void filterByCategory(String category) {
        List<JSONObject> filtered = new ArrayList<>();
        for (JSONObject item : allItems) {
            String itemCat = item.optString(
                    "category", "personal").toLowerCase();
            if (itemCat.equals(category)) filtered.add(item);
        }
        displayItems(filtered);
    }

    private String getEmojiForItem(String itemName) {
        String name = itemName == null ? "" : itemName.toLowerCase();
        if (name.contains("notebook") || name.contains("book")
                || name.contains("record")) return "\uD83D\uDCD3";
        if (name.contains("pen") || name.contains("pencil")) return "\u270F\uFE0F";
        if (name.contains("water")) return "\uD83D\uDCA7";
        if (name.contains("id") || name.contains("card")) return "\uD83E\uDEAA";
        if (name.contains("lab") || name.contains("coat")) return "\uD83E\uDDBC";
        if (name.contains("calculator")) return "\uD83D\uDD22";
        if (name.contains("charger")) return "\uD83D\uDD0C";
        if (name.contains("laptop")) return "\uD83D\uDCBB";
        return "\uD83D\uDCE6";
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
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(BagActivity.this,
                                        "Failed to load items",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void updateProgress(int checked, int total) {
        tvProgressCount.setText(checked + "/" + total + " packed");
        progressBar.setProgress(total > 0 ? (checked * 100) / total : 0);
    }

    private void displayItems(List<JSONObject> items) {
        bagContainer.removeAllViews();

        if (items.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText("No items here! Tap + to add items 🎒");
            empty.setTextColor(0xFF888888);
            empty.setTextSize(14);
            empty.setPadding(32, 64, 32, 32);
            bagContainer.addView(empty);
            return;
        }

        for (JSONObject item : items) {
            try {
                addBagItemView(
                        item.getInt("id"),
                        item.getString("item_name"),
                        item.getString("is_checked").equals("true")
                );
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void addBagItemView(int id, String name, boolean isChecked) {
        View itemView = LayoutInflater.from(this)
                .inflate(R.layout.item_bag, bagContainer, false);

        TextView tvEmoji = itemView.findViewById(R.id.tvItemEmoji);
        TextView tvName = itemView.findViewById(R.id.tvBagItemName);
        TextView btnDelete = itemView.findViewById(R.id.btnDeleteItem);
        CheckBox checkBox = itemView.findViewById(R.id.checkBagItem);

        tvEmoji.setText(getEmojiForItem(name));
        tvName.setText(name);
        checkBox.setChecked(isChecked);

        if (isChecked) {
            tvName.setPaintFlags(tvName.getPaintFlags()
                    | android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);
            tvName.setTextColor(0xFF888888);
        }

        checkBox.setOnCheckedChangeListener(
                (btn, checked) -> updateItemCheck(id, checked));
        btnDelete.setOnClickListener(v -> showDeleteConfirm(id, name));

        bagContainer.addView(itemView);
    }

    private void showDeleteConfirm(int id, String name) {
        new AlertDialog.Builder(this)
                .setTitle("Remove Item?")
                .setMessage("Remove \"" + name + "\" from "
                        + selectedDay + "?")
                .setPositiveButton("Remove",
                        (dialog, which) -> deleteItem(id))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deleteItem(int itemId) {
        ApiClient.getService().deleteBagItem(token, itemId)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> loadBagItems(selectedDay));
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call,
                                          Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(BagActivity.this,
                                        "Failed to remove!",
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

        builder.setTitle("Add item to " + selectedDay + " 🎒");
        builder.setPositiveButton("Add", (dialog, which) -> {
            String itemName = etItemName.getText().toString().trim();
            if (itemName.isEmpty()) {
                Toast.makeText(this,
                        "Enter item name!",
                        Toast.LENGTH_SHORT).show();
                return;
            }
            addBagItem(itemName);
        });
        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void addBagItem(String itemName) {
        try {
            JSONObject json = new JSONObject();
            json.put("day", selectedDay);
            json.put("item_name", itemName);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    json.toString()
            );

            ApiClient.getService().addBagItem(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call,
                                               Response<ResponseBody> response) {
                            mainHandler.post(() -> {
                                if (response.isSuccessful()) {
                                    Toast.makeText(BagActivity.this,
                                            itemName + " added! ✅",
                                            Toast.LENGTH_SHORT).show();
                                }
                                loadBagItems(selectedDay);
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
                            mainHandler.post(() -> loadBagItems(selectedDay));
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