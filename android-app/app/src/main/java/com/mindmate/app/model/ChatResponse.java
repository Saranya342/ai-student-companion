package com.mindmate.app.model;

public class ChatResponse {
    private String your_message;
    private String bot_reply;
    private int chat_id;

    public String getBotReply() {
        return bot_reply;
    }

    public String getYourMessage() {
        return your_message;
    }
}