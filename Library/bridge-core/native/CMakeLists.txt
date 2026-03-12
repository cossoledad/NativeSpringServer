cmake_minimum_required(VERSION 3.20)
project(CloudLoggerNative LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(SWIG REQUIRED)
include(UseSWIG)
find_package(JNI REQUIRED)

set(CLOUD_LOGGER_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(CLOUD_LOGGER_JAVA_OUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../target/generated-sources/cloudlogger-swig")
set(CLOUD_LOGGER_LIB_OUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../target/native/lib")

file(MAKE_DIRECTORY "${CLOUD_LOGGER_JAVA_OUT_DIR}")
file(MAKE_DIRECTORY "${CLOUD_LOGGER_LIB_OUT_DIR}")

add_library(cloudlogger_bridge SHARED
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cloud_logger_bridge.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/cloud_network_bridge.cpp
)

target_include_directories(cloudlogger_bridge
  PUBLIC ${CLOUD_LOGGER_INCLUDE_DIR}
)

set_target_properties(cloudlogger_bridge PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CLOUD_LOGGER_LIB_OUT_DIR}
)

set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/swig/cloud_logger.i PROPERTIES CPLUSPLUS ON)
set(CMAKE_SWIG_OUTDIR ${CLOUD_LOGGER_JAVA_OUT_DIR})
set(CMAKE_SWIG_FLAGS
  -package com.example.cloudlogger.bridge
  -I${CLOUD_LOGGER_INCLUDE_DIR}
  -directors
)

swig_add_library(cloudlogger_jni
  TYPE SHARED
  LANGUAGE java
  SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/swig/cloud_logger.i
)

target_include_directories(${SWIG_MODULE_cloudlogger_jni_REAL_NAME}
  PRIVATE
    ${JNI_INCLUDE_DIRS}
    ${CLOUD_LOGGER_INCLUDE_DIR}
)

swig_link_libraries(cloudlogger_jni
  ${JNI_LIBRARIES}
  cloudlogger_bridge
)

set_target_properties(${SWIG_MODULE_cloudlogger_jni_REAL_NAME} PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CLOUD_LOGGER_LIB_OUT_DIR}
)

add_custom_target(print_cloudlogger_outputs ALL
  COMMAND ${CMAKE_COMMAND} -E echo "Native libs: ${CLOUD_LOGGER_LIB_OUT_DIR}"
  COMMAND ${CMAKE_COMMAND} -E echo "SWIG Java: ${CLOUD_LOGGER_JAVA_OUT_DIR}"
)
add_dependencies(print_cloudlogger_outputs cloudlogger_bridge ${SWIG_MODULE_cloudlogger_jni_REAL_NAME})
