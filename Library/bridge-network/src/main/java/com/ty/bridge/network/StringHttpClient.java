package com.ty.bridge.network;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class StringHttpClient {
    private final HttpClient client;
    private final Duration timeout;

    public StringHttpClient() {
        this(Duration.ofSeconds(10));
    }

    public StringHttpClient(Duration timeout) {
        this.client = HttpClient.newHttpClient();
        this.timeout = timeout;
    }

    public String get(String url) {
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .timeout(timeout)
                .GET()
                .build();
        return send(request);
    }

    public String post(String url, String body) {
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .timeout(timeout)
                .header("Content-Type", "text/plain; charset=UTF-8")
                .POST(HttpRequest.BodyPublishers.ofString(body == null ? "" : body))
                .build();
        return send(request);
    }

    private String send(HttpRequest request) {
        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            return response.body();
        } catch (IOException | InterruptedException ex) {
            if (ex instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
            throw new RuntimeException("HTTP request failed: " + ex.getMessage(), ex);
        }
    }
}
