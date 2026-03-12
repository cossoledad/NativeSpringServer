package com.ty.bridge.network.internal;

import com.example.cloudlogger.bridge.CloudNetwork;
import com.ty.bridge.network.StringHttpClient;

public class DefaultCloudNetwork extends CloudNetwork {
    private final StringHttpClient client = new StringHttpClient();

    @Override
    public String get(String url, String params) {
        String fullUrl = url;
        if (params != null && !params.isBlank()) {
            String separator = url.contains("?") ? "&" : "?";
            fullUrl = url + separator + params;
        }
        return client.get(fullUrl);
    }

    @Override
    public String post(String url, String body) {
        return client.post(url, body);
    }
}
