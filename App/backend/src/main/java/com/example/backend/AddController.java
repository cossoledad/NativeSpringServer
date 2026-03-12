package com.example.backend;

import com.ty.nss.foundation.docs.MarkdownDocumentApi;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AddController {

    @GetMapping("/add")
    public Map<String, Integer> add(@RequestParam("a") int a, @RequestParam("b") int b) {
        FoundationDocsNativeLoader.load();
        int result = MarkdownDocumentApi.add(a, b);
        return Map.of("a", a, "b", b, "result", result);
    }

    @GetMapping("/foundation/network/get")
    public Map<String, String> foundationNetworkGet(
        @RequestParam("url") String url,
        @RequestParam(name = "params", defaultValue = "") String params
    ) {
        FoundationDocsNativeLoader.load();
        String response = MarkdownDocumentApi.bridgeGet(url, params);
        Map<String, String> result = new LinkedHashMap<>();
        result.put("url", url);
        result.put("params", params);
        result.put("response", response);
        return result;
    }

    @PostMapping("/foundation/network/post")
    public Map<String, String> foundationNetworkPost(
        @RequestParam("url") String url,
        @RequestBody(required = false) String body
    ) {
        FoundationDocsNativeLoader.load();
        String payload = body == null ? "" : body;
        String response = MarkdownDocumentApi.bridgePost(url, payload);
        Map<String, String> result = new LinkedHashMap<>();
        result.put("url", url);
        result.put("body", payload);
        result.put("response", response);
        return result;
    }

    @GetMapping("/foundation/echo-get")
    public String foundationEchoGet(@RequestParam(name = "msg", defaultValue = "ping") String msg) {
        return "echo-get:" + msg;
    }

    @PostMapping("/foundation/echo-post")
    public String foundationEchoPost(@RequestBody(required = false) String body) {
        return "echo-post:" + (body == null ? "" : body);
    }
}
