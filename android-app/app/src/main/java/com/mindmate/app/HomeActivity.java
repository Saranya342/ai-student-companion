package com.mindmate.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.mindmate.app.model.AgentChatResponse;
import com.mindmate.app.model.ChatRequest;
import com.mindmate.app.network.ApiClient;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HomeActivity extends AppCompatActivity {

    RecyclerView rvMessages;
    EditText etMessage;
    Button btnSend;
    TextView chipRemind, chipStressed, chipPlan, chipBag;

    List<ChatMessage> messages = new ArrayList<>();
    ChatAdapter adapter;

    String token;
    boolean isWaiting = false;
    Handler mainHandler = new Handler(Looper.getMainLooper());

    private static boolean greetedThisSession = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        SharedPreferences prefs = getSharedPreferences("MindMate", MODE_PRIVATE);
        token = "Bearer " + prefs.getString("token", "");

        rvMessages = findViewById(R.id.rvMessages);
        etMessage = findViewById(R.id.etMessage);
        btnSend = findViewById(R.id.btnSend);

        chipRemind = findViewById(R.id.chipRemind);
        chipStressed = findViewById(R.id.chipStressed);
        chipPlan = findViewById(R.id.chipPlan);
        chipBag = findViewById(R.id.chipBag);

        adapter = new ChatAdapter(messages);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);
        rvMessages.setAdapter(adapter);

        if (!greetedThisSession) {
            messages.clear();
            adapter.notifyDataSetChanged();
            addBotMessage("Hey! 👋 Tell me what you're working on today.");
            greetedThisSession = true;
        }

        btnSend.setOnClickListener(v -> sendMessage());

        chipRemind.setOnClickListener(v -> sendQuickMessage("Remind me to do something"));
        chipStressed.setOnClickListener(v -> sendQuickMessage("I feel stressed"));
        chipPlan.setOnClickListener(v -> sendQuickMessage("Plan my day"));
        chipBag.setOnClickListener(v -> sendQuickMessage("Bag checklist for Monday"));

        BottomNavigationView bottomNav = findViewById(R.id.bottomNav);
        bottomNav.setSelectedItemId(R.id.nav_chat);
        bottomNav.setOnItemSelectedListener(item -> {
            int id = item.getItemId();
            if (id == R.id.nav_chat) return true;

            if (id == R.id.nav_planner) startActivity(new Intent(this, PlannerActivity.class));
            else if (id == R.id.nav_bag) startActivity(new Intent(this, BagActivity.class));
            else if (id == R.id.nav_journal) startActivity(new Intent(this, JournalActivity.class));
            else if (id == R.id.nav_profile) startActivity(new Intent(this, ProfileActivity.class));

            return true;
        });
    }

    private void sendQuickMessage(String message) {
        etMessage.setText(message);
        sendMessage();
    }

    private void sendMessage() {
        if (isWaiting) {
            Toast.makeText(this, "Please wait for reply...", Toast.LENGTH_SHORT).show();
            return;
        }

        String message = etMessage.getText().toString().trim();
        if (message.isEmpty()) return;

        addUserMessage(message);
        etMessage.setText("");

        isWaiting = true;
        btnSend.setEnabled(false);
        addBotMessage("typing... ⏳");

        ChatRequest request = new ChatRequest(message);

        ApiClient.getService().agentChat(token, request)
                .enqueue(new Callback<AgentChatResponse>() {
                    @Override
                    public void onResponse(Call<AgentChatResponse> call,
                                           Response<AgentChatResponse> response) {
                        mainHandler.post(() -> {
                            removeLastTyping();
                            isWaiting = false;
                            btnSend.setEnabled(true);

                            if (response.isSuccessful() && response.body() != null) {
                                AgentChatResponse body = response.body();

                                String reply = body.getResponse();
                                if (reply == null || reply.trim().isEmpty()) {
                                    reply = "I didn't get that. Can you try again?";
                                }
                                addBotMessage(reply);

                                if (body.getTasksAddedToPlanner() > 0) {
                                    Toast.makeText(
                                            HomeActivity.this,
                                            "✅ Added " + body.getTasksAddedToPlanner() + " task(s) to Planner",
                                            Toast.LENGTH_SHORT
                                    ).show();
                                }

                                if (body.getBagDay() != null
                                        && !body.getBagDay().isEmpty()
                                        && body.getBagItemsAdded() > 0) {
                                    Toast.makeText(
                                            HomeActivity.this,
                                            "🎒 Bag ready for " + body.getBagDay()
                                                    + "! " + body.getBagItemsAdded() + " item(s) added",
                                            Toast.LENGTH_LONG
                                    ).show();

                                    Intent bagIntent = new Intent(HomeActivity.this, BagActivity.class);
                                    bagIntent.putExtra("selected_day", body.getBagDay());
                                    startActivity(bagIntent);
                                }

                                // ✅ Thought Parking toast
                                if (body.isThoughtParked()) {
                                    Toast.makeText(
                                            HomeActivity.this,
                                            "🧠 Saved to Thought Parking",
                                            Toast.LENGTH_SHORT
                                    ).show();
                                }

                            } else {
                                addBotMessage("Hmm something went wrong 😅 Try again!");
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<AgentChatResponse> call, Throwable t) {
                        mainHandler.post(() -> {
                            removeLastTyping();
                            isWaiting = false;
                            btnSend.setEnabled(true);
                            addBotMessage("Can't connect to server 😔 Is backend running?");
                        });
                    }
                });
    }

    private void addUserMessage(String text) {
        messages.add(new ChatMessage(text, true));
        adapter.notifyItemInserted(messages.size() - 1);
        rvMessages.scrollToPosition(messages.size() - 1);
    }

    private void addBotMessage(String text) {
        messages.add(new ChatMessage(text, false));
        adapter.notifyItemInserted(messages.size() - 1);
        rvMessages.scrollToPosition(messages.size() - 1);
    }

    private void removeLastTyping() {
        if (!messages.isEmpty()) {
            ChatMessage last = messages.get(messages.size() - 1);
            if (!last.isUser() && last.getText() != null && last.getText().startsWith("typing")) {
                messages.remove(messages.size() - 1);
                adapter.notifyItemRemoved(messages.size());
            }
        }
    }
}