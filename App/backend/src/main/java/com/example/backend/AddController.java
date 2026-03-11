package com.example.backend;

import com.example.cloudlogger.bridge.CloudLoggerRegistry;
import com.example.foundation.math.MathApi;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AddController {

    @GetMapping("/add")
    public Map<String, Integer> add(@RequestParam("a") int a, @RequestParam("b") int b) {
        FoundationMathNativeLoader.load();
        int result = MathApi.add(a, b);
        CloudLoggerRegistry.upload("backend", "backend add(" + a + ", " + b + ") = " + result);
        return Map.of("a", a, "b", b, "result", result);
    }
}
