cmake_minimum_required(VERSION 3.20)
project(FoundationDocs LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(nss-native CONFIG REQUIRED)
find_package(SWIG REQUIRED)
include(UseSWIG)
find_package(JNI REQUIRED)

set(FOUNDATION_DOCS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(FOUNDATION_DOCS_JAVA_PACKAGE "com.ty.nss.foundation.docs")
string(REPLACE "." "/" FOUNDATION_DOCS_JAVA_PACKAGE_PATH "${FOUNDATION_DOCS_JAVA_PACKAGE}")
set(FOUNDATION_DOCS_SWIG_OUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/java/${FOUNDATION_DOCS_JAVA_PACKAGE_PATH}")
set(FOUNDATION_DOCS_LIB_OUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/native/lib")

file(MAKE_DIRECTORY "${FOUNDATION_DOCS_SWIG_OUT_DIR}")
file(MAKE_DIRECTORY "${FOUNDATION_DOCS_LIB_OUT_DIR}")

add_library(foundation_docs SHARED
  ${CMAKE_CURRENT_SOURCE_DIR}/src/foundation_docs.cpp
)

target_include_directories(foundation_docs
  PUBLIC ${FOUNDATION_DOCS_INCLUDE_DIR}
)

target_link_libraries(foundation_docs
  PRIVATE nss-native::nss-native
)

set_target_properties(foundation_docs PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${FOUNDATION_DOCS_LIB_OUT_DIR}
)

set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/swig/foundation_docs.i PROPERTIES CPLUSPLUS ON)
set(CMAKE_SWIG_OUTDIR ${FOUNDATION_DOCS_SWIG_OUT_DIR})
set(CMAKE_SWIG_FLAGS
  -package ${FOUNDATION_DOCS_JAVA_PACKAGE}
  -I${FOUNDATION_DOCS_INCLUDE_DIR}
)

swig_add_library(foundation_docs_jni
  TYPE SHARED
  LANGUAGE java
  SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/swig/foundation_docs.i
)

target_include_directories(${SWIG_MODULE_foundation_docs_jni_REAL_NAME}
  PRIVATE
    ${JNI_INCLUDE_DIRS}
    ${FOUNDATION_DOCS_INCLUDE_DIR}
)

swig_link_libraries(foundation_docs_jni
  ${JNI_LIBRARIES}
  foundation_docs
)

set_target_properties(${SWIG_MODULE_foundation_docs_jni_REAL_NAME} PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${FOUNDATION_DOCS_LIB_OUT_DIR}
)
