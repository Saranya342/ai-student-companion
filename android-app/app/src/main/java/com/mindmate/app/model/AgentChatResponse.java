package com.mindmate.app.model;

import java.util.List;

public class AgentChatResponse {
    private String response;
    private String emotion_detected;
    private String vibe_detected;
    private List<String> agents_used;

    private int tasks_extracted;
    private int tasks_added_to_planner;
    private int micro_tasks_generated;

    private String bag_day;
    private int bag_items_added;

    private boolean thought_parked;
    private Integer thought_id;

    public String getResponse() { return response; }
    public String getEmotionDetected() { return emotion_detected; }
    public String getVibeDetected() { return vibe_detected; }
    public List<String> getAgentsUsed() { return agents_used; }

    public int getTasksExtracted() { return tasks_extracted; }
    public int getTasksAddedToPlanner() { return tasks_added_to_planner; }
    public int getMicroTasksGenerated() { return micro_tasks_generated; }

    public String getBagDay() { return bag_day; }
    public int getBagItemsAdded() { return bag_items_added; }

    public boolean isThoughtParked() { return thought_parked; }
    public Integer getThoughtId() { return thought_id; }
}