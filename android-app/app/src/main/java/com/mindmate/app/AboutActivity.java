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

public class AboutActivity extends AppCompatActivity {

    TextView tvAbout;
    Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_about);

        tvAbout = findViewById(R.id.tvAbout);
        tvAbout.setText("Loading...");

        loadAbout();
    }

    private void loadAbout() {
        ApiClient.getService().getAbout().enqueue(new Callback<ResponseBody>() {
            @Override
            public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
                mainHandler.post(() -> {
                    try {
                        if (!response.isSuccessful() || response.body() == null) {
                            tvAbout.setText("Failed to load About.");
                            return;
                        }
                        String json = response.body().string();
                        JSONObject obj = new JSONObject(json);

                        String appName = obj.optString("app_name", "MindMate");
                        String version = obj.optString("version", "");
                        String description = obj.optString("description", "");

                        StringBuilder sb = new StringBuilder();
                        sb.append(appName).append("\n");
                        if (!version.isEmpty()) sb.append("Version: ").append(version).append("\n\n");
                        sb.append(description).append("\n\n");

                        JSONArray features = obj.optJSONArray("features");
                        if (features != null) {
                            sb.append("Features:\n");
                            for (int i = 0; i < features.length(); i++) {
                                sb.append("• ").append(features.getString(i)).append("\n");
                            }
                        }

                        tvAbout.setText(sb.toString().trim());
                    } catch (Exception e) {
                        tvAbout.setText("Error parsing About.");
                    }
                });
            }

            @Override
            public void onFailure(Call<ResponseBody> call, Throwable t) {
                mainHandler.post(() -> {
                    tvAbout.setText("Connection failed.");
                    Toast.makeText(AboutActivity.this, "Connection failed!", Toast.LENGTH_SHORT).show();
                });
            }
        });
    }
}