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

import com.mindmate.app.model.ChatRequest;
import com.mindmate.app.model.ChatResponse;
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
    TextView navPlanner, navBag, navMemories, navProfile;

    List<ChatMessage> messages = new ArrayList<>();
    ChatAdapter adapter;
    String token;
    boolean isWaiting = false;

    Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        android.os.StrictMode.ThreadPolicy policy =
                new android.os.StrictMode.ThreadPolicy.Builder()
                        .permitAll().build();
        android.os.StrictMode.setThreadPolicy(policy);

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
        navPlanner = findViewById(R.id.navPlanner);
        navBag = findViewById(R.id.navBag);
        navMemories = findViewById(R.id.navMemories);
        navProfile = findViewById(R.id.navProfile);

        adapter = new ChatAdapter(messages);
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);
        rvMessages.setAdapter(adapter);

        addBotMessage("Hey! 👋 How's your day going? I'm here whenever you need me.");

        btnSend.setOnClickListener(v -> sendMessage());

        chipRemind.setOnClickListener(v -> sendQuickMessage("Remind me about something"));
        chipStressed.setOnClickListener(v -> sendQuickMessage("I feel stressed"));
        chipPlan.setOnClickListener(v -> sendQuickMessage("Plan my day"));
        chipBag.setOnClickListener(v -> sendQuickMessage("What to carry tomorrow?"));

        navPlanner.setOnClickListener(v ->
                startActivity(new Intent(this, PlannerActivity.class)));
        navBag.setOnClickListener(v ->
                startActivity(new Intent(this, BagActivity.class)));
        navMemories.setOnClickListener(v ->
                startActivity(new Intent(this, MemoriesActivity.class)));
        navProfile.setOnClickListener(v ->
                startActivity(new Intent(this, ProfileActivity.class)));
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

        ApiClient.getService().sendMessage(token, request)
                .enqueue(new Callback<ChatResponse>() {
                    @Override
                    public void onResponse(Call<ChatResponse> call,
                                           Response<ChatResponse> response) {
                        mainHandler.post(() -> {
                            removeLastMessage();
                            isWaiting = false;
                            btnSend.setEnabled(true);

                            if (response.isSuccessful() && response.body() != null) {
                                addBotMessage(response.body().getBotReply());
                            } else {
                                addBotMessage("Hmm something went wrong 😅 Try again!");
                            }
                        });
                    }

                    @Override
                    public void onFailure(Call<ChatResponse> call, Throwable t) {
                        mainHandler.post(() -> {
                            removeLastMessage();
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

    private void removeLastMessage() {
        if (!messages.isEmpty()) {
            messages.remove(messages.size() - 1);
            adapter.notifyItemRemoved(messages.size());
        }
    }
}