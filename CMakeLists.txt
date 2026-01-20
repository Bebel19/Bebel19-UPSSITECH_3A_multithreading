cmake_minimum_required(VERSION 3.16)
project(tp4_low_level LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# CPR (HTTP)
FetchContent_Declare(
  cpr
  GIT_REPOSITORY https://github.com/libcpr/cpr.git
  GIT_TAG 1.10.5
)
FetchContent_MakeAvailable(cpr)

# nlohmann/json (JSON)
FetchContent_Declare(
  nlohmann_json
  GIT_REPOSITORY https://github.com/nlohmann/json.git
  GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(nlohmann_json)

# Eigen via paquet système (libeigen3-dev)
find_package(Eigen3 REQUIRED)

add_executable(low_level low_level.cpp)
target_link_libraries(low_level PRIVATE cpr::cpr nlohmann_json::nlohmann_json Eigen3::Eigen)
