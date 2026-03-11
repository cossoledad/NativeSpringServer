cmake_minimum_required(VERSION 3.20)
project(FoundationMath LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(cloudlogger-native CONFIG REQUIRED)
find_package(SWIG REQUIRED)
include(UseSWIG)
find_package(JNI REQUIRED)

set(FOUNDATION_MATH_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(FOUNDATION_MATH_SWIG_OUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/target/generated-sources/foundation-math-swig")
set(FOUNDATION_MATH_LIB_OUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/native/lib")

file(MAKE_DIRECTORY "${FOUNDATION_MATH_SWIG_OUT_DIR}")
file(MAKE_DIRECTORY "${FOUNDATION_MATH_LIB_OUT_DIR}")

add_library(foundation_math SHARED
  ${CMAKE_CURRENT_SOURCE_DIR}/src/foundation_math.cpp
)

target_include_directories(foundation_math
  PUBLIC ${FOUNDATION_MATH_INCLUDE_DIR}
)

target_link_libraries(foundation_math
  PRIVATE cloudlogger-native::cloudlogger-native
)

set_target_properties(foundation_math PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${FOUNDATION_MATH_LIB_OUT_DIR}
)

set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/swig/foundation_math.i PROPERTIES CPLUSPLUS ON)
set(CMAKE_SWIG_OUTDIR ${FOUNDATION_MATH_SWIG_OUT_DIR})
set(CMAKE_SWIG_FLAGS
  -package com.example.foundation.math
  -I${FOUNDATION_MATH_INCLUDE_DIR}
)

swig_add_library(foundation_math_jni
  TYPE SHARED
  LANGUAGE java
  SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/swig/foundation_math.i
)

target_include_directories(${SWIG_MODULE_foundation_math_jni_REAL_NAME}
  PRIVATE
    ${JNI_INCLUDE_DIRS}
    ${FOUNDATION_MATH_INCLUDE_DIR}
)

swig_link_libraries(foundation_math_jni
  ${JNI_LIBRARIES}
  foundation_math
)

set_target_properties(${SWIG_MODULE_foundation_math_jni_REAL_NAME} PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${FOUNDATION_MATH_LIB_OUT_DIR}
)

add_executable(foundation_smoke src/main.cpp)
target_include_directories(foundation_smoke PRIVATE ${FOUNDATION_MATH_INCLUDE_DIR})
target_link_libraries(foundation_smoke PRIVATE foundation_math cloudlogger-native::cloudlogger-native)
