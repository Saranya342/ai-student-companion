package com.mindmate.app;

import android.app.AlertDialog;
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
import java.util.Date;
import java.util.Locale;

import okhttp3.MediaType;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PlannerActivity extends AppCompatActivity {

    TextView navChat, navBag, navMemories, navProfile;
    TextView tvProgress, tvDate;
    Button btnAddTask, btnAiPlan;
    LinearLayout taskContainer;
    String token;
    Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        android.os.StrictMode.ThreadPolicy policy =
                new android.os.StrictMode.ThreadPolicy.Builder()
                        .permitAll().build();
        android.os.StrictMode.setThreadPolicy(policy);

        setContentView(R.layout.activity_planner);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        tvProgress = findViewById(R.id.tvProgress);
        tvDate = findViewById(R.id.tvDate);
        btnAddTask = findViewById(R.id.btnAddTask);
        btnAiPlan = findViewById(R.id.btnAiPlan);
        taskContainer = findViewById(R.id.taskContainer);
        navChat = findViewById(R.id.navChat);
        navBag = findViewById(R.id.navBag);
        navMemories = findViewById(R.id.navMemories);
        navProfile = findViewById(R.id.navProfile);

        String date = new SimpleDateFormat("EEEE, MMM d",
                Locale.getDefault()).format(new Date());
        tvDate.setText(date);

        loadTasks();

        btnAddTask.setOnClickListener(v -> showAddTaskDialog());
        btnAiPlan.setOnClickListener(v -> getAiPlan());

        navChat.setOnClickListener(v -> {
            startActivity(new Intent(this, HomeActivity.class));
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
        navProfile.setOnClickListener(v -> {
            startActivity(new Intent(this, ProfileActivity.class));
            finish();
        });
    }

    private void loadTasks() {
        ApiClient.getService().getTasks(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            try {
                                if (response.isSuccessful() && response.body() != null) {
                                    String json = response.body().string();
                                    JSONObject obj = new JSONObject(json);
                                    int total = obj.getInt("total");
                                    int completed = obj.getInt("completed");
                                    tvProgress.setText(completed + "/" + total);

                                    JSONArray tasks = obj.getJSONArray("tasks");
                                    taskContainer.removeAllViews();

                                    for (int i = 0; i < tasks.length(); i++) {
                                        JSONObject task = tasks.getJSONObject(i);
                                        addTaskView(
                                                task.getInt("id"),
                                                task.getString("title"),
                                                task.getString("due_date"),
                                                task.getString("priority"),
                                                task.getBoolean("is_completed")
                                        );
                                    }
                                }
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(PlannerActivity.this,
                                        "Failed to load tasks",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void addTaskView(int id, String title, String dueDate,
                             String priority, boolean isCompleted) {
        View taskView = LayoutInflater.from(this)
                .inflate(R.layout.item_task, taskContainer, false);

        TextView tvTitle = taskView.findViewById(R.id.tvTaskTitle);
        TextView tvDue = taskView.findViewById(R.id.tvTaskDue);
        TextView tvPriority = taskView.findViewById(R.id.tvTaskPriority);
        Button btnComplete = taskView.findViewById(R.id.btnCompleteTask);

        tvTitle.setText(title);
        tvDue.setText("Due: " + dueDate);
        tvPriority.setText(priority.toUpperCase());

        if (isCompleted) {
            tvTitle.setPaintFlags(tvTitle.getPaintFlags() |
                    android.graphics.Paint.STRIKE_THRU_TEXT_FLAG);
            btnComplete.setText("✓ Done");
            btnComplete.setEnabled(false);
            btnComplete.getBackground().setTint(0xFF4CAF50);
        } else {
            btnComplete.setText("Mark Done");
            btnComplete.setOnClickListener(v -> completeTask(id));
        }

        switch (priority.toLowerCase()) {
            case "high":
                tvPriority.setTextColor(0xFFFF5252);
                break;
            case "medium":
                tvPriority.setTextColor(0xFFFFAB76);
                break;
            case "low":
                tvPriority.setTextColor(0xFF69F0AE);
                break;
        }

        taskContainer.addView(taskView);
    }

    private void completeTask(int taskId) {
        ApiClient.getService().completeTask(token, taskId)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            if (response.isSuccessful()) {
                                Toast.makeText(PlannerActivity.this,
                                        "Task completed! 🎉",
                                        Toast.LENGTH_SHORT).show();
                                loadTasks();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(PlannerActivity.this,
                                        "Failed!", Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void getAiPlan() {
        Toast.makeText(this, "Generating AI plan... ⏳",
                Toast.LENGTH_SHORT).show();

        ApiClient.getService().getAiPlan(token)
                .enqueue(new Callback<ResponseBody>() {
                    @Override
                    public void onResponse(Call<ResponseBody> call,
                                           Response<ResponseBody> response) {
                        mainHandler.post(() -> {
                            try {
                                if (response.isSuccessful() && response.body() != null) {
                                    String json = response.body().string();
                                    JSONObject obj = new JSONObject(json);
                                    String plan = obj.getString("ai_study_plan");

                                    new AlertDialog.Builder(PlannerActivity.this)
                                            .setTitle("🤖 Your AI Study Plan")
                                            .setMessage(plan)
                                            .setPositiveButton("Got it!", null)
                                            .show();
                                }
                            } catch (Exception e) {
                                e.printStackTrace();
                                Toast.makeText(PlannerActivity.this,
                                        "Error getting plan",
                                        Toast.LENGTH_SHORT).show();
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ResponseBody> call, Throwable t) {
                        mainHandler.post(() ->
                                Toast.makeText(PlannerActivity.this,
                                        "Failed to get plan!",
                                        Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void showAddTaskDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Add New Task");

        View dialogView = LayoutInflater.from(this)
                .inflate(R.layout.dialog_add_task, null);
        builder.setView(dialogView);

        EditText etTitle = dialogView.findViewById(R.id.etTaskTitle);
        EditText etDesc = dialogView.findViewById(R.id.etTaskDesc);
        EditText etDate = dialogView.findViewById(R.id.etTaskDate);
        EditText etPriority = dialogView.findViewById(R.id.etTaskPriority);

        builder.setPositiveButton("Add", (dialog, which) -> {
            String title = etTitle.getText().toString().trim();
            String desc = etDesc.getText().toString().trim();
            String date = etDate.getText().toString().trim();
            String priority = etPriority.getText().toString().trim().toLowerCase();

            if (title.isEmpty() || date.isEmpty()) {
                Toast.makeText(this, "Title and date required!",
                        Toast.LENGTH_SHORT).show();
                return;
            }

            if (!priority.equals("high") && !priority.equals("medium")
                    && !priority.equals("low")) {
                priority = "medium";
            }

            addTask(title, desc, date, priority);
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void addTask(String title, String desc,
                         String date, String priority) {
        try {
            JSONObject json = new JSONObject();
            json.put("title", title);
            json.put("description", desc);
            json.put("due_date", date);
            json.put("priority", priority);

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    json.toString()
            );

            ApiClient.getService().addTask(token, body)
                    .enqueue(new Callback<ResponseBody>() {
                        @Override
                        public void onResponse(Call<ResponseBody> call,
                                               Response<ResponseBody> response) {
                            mainHandler.post(() -> {
                                if (response.isSuccessful()) {
                                    Toast.makeText(PlannerActivity.this,
                                            "Task added! ✅",
                                            Toast.LENGTH_SHORT).show();
                                    loadTasks();
                                } else {
                                    Toast.makeText(PlannerActivity.this,
                                            "Failed to add task",
                                            Toast.LENGTH_SHORT).show();
                                }
                            });
                        }

                        @Override
                        public void onFailure(Call<ResponseBody> call, Throwable t) {
                            mainHandler.post(() ->
                                    Toast.makeText(PlannerActivity.this,
                                            "Connection failed!",
                                            Toast.LENGTH_SHORT).show());
                        }
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}