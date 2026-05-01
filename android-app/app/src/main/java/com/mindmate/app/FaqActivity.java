package com.mindmate.app;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.mindmate.app.network.ApiClient;

import org.json.JSONArray;
import org.json.JSONObject;

import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class FaqActivity extends AppCompatActivity {

    TextView tvFaq;
    Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_faq);

        tvFaq = findViewById(R.id.tvFaq);
        tvFaq.setText("Loading FAQ...");

        loadFaq();
    }

    private void loadFaq() {
        ApiClient.getService().getFaq().enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                mainHandler.post(() -> {
                    try {
                        if (!response.isSuccessful() || response.body() == null) {
                            tvFaq.setText("Failed to load FAQ.");
                            return;
                        }
                        String json = response.body().string();
                        JSONObject obj = new JSONObject(json);
                        JSONArray faqs = obj.getJSONArray("faqs");

                        StringBuilder sb = new StringBuilder();
                        for (int i = 0; i < faqs.length(); i++) {
                            JSONObject f = faqs.getJSONObject(i);
                            sb.append("Q: ").append(f.optString("question")).append("\n");
                            sb.append("A: ").append(f.optString("answer")).append("\n\n");
                        }

                        tvFaq.setText(sb.toString().trim());
                    } catch (Exception e) {
                        tvFaq.setText("Error parsing FAQ.");
                    }
                });
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                mainHandler.post(() -> {
                    tvFaq.setText("Connection failed.");
                    Toast.makeText(FaqActivity.this, "Connection failed!", Toast.LENGTH_SHORT).show();
                });
            }
        });
    }
}