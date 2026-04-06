package com.mindmate.app.network;

import com.mindmate.app.model.LoginRequest;
import com.mindmate.app.model.LoginResponse;
import com.mindmate.app.model.RegisterRequest;
import com.mindmate.app.model.ChatRequest;
import com.mindmate.app.model.ChatResponse;

import okhttp3.RequestBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.PUT;
import retrofit2.http.Path;

public interface ApiService {

    @POST("users/register")
    Call<Void> register(@Body RegisterRequest request);

    @POST("users/login")
    Call<LoginResponse> login(@Body LoginRequest request);

    @POST("chat/send")
    Call<ChatResponse> sendMessage(
            @Header("Authorization") String token,
            @Body ChatRequest request);

    @GET("chat/history")
    Call<Object> getChatHistory(@Header("Authorization") String token);

    @GET("planner/tasks")
    Call<ResponseBody> getTasks(@Header("Authorization") String token);

    @POST("planner/tasks/add")
    Call<ResponseBody> addTask(
            @Header("Authorization") String token,
            @Body RequestBody body);

    @PUT("planner/tasks/complete/{id}")
    Call<ResponseBody> completeTask(
            @Header("Authorization") String token,
            @Path("id") int id);

    @DELETE("planner/tasks/delete/{id}")
    Call<ResponseBody> deleteTask(
            @Header("Authorization") String token,
            @Path("id") int id);

    @GET("planner/tasks/ai-plan")
    Call<ResponseBody> getAiPlan(@Header("Authorization") String token);

    @GET("bag/day/{day}")
    Call<ResponseBody> getBagItems(
            @Header("Authorization") String token,
            @Path("day") String day);

    @PUT("bag/item/check/{id}")
    Call<ResponseBody> checkBagItem(
            @Header("Authorization") String token,
            @Path("id") int id,
            @Body RequestBody body);
}