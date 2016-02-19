
cmake_minimum_required(VERSION 2.8.12.1)

# Configuration types.
set(CMAKE_CONFIGURATION_TYPES Debug Release)

# Project name.
project(ClangCompletion)

# Project Type.
set(MPRJ_TYPE "Default")


# Project architecture.
if(NOT DEFINED MPRJ_ARCH)
  set(MPRJ_ARCH "x86")
endif()

# Project language.
if(NOT DEFINED MPRJ_LANG)
  set(MPRJ_LANG "LANGUAGE_CH")
endif()

# Result Files
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "C:\\Programs\\${CMAKE_NAME}\\${MPRJ_TYPE}\\$<CONFIGURATION>\\${MPRJ_LANG}\\")

# Include cmake macros.
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}")
include("macros")

# Source include directory.
include_directories(CMAKE_CURRENT_SOURCE_DIR, "${CMAKE_SOURCE_DIR}/lib/include")

# Consumers who run into LNK4099 warnings can pass /Z7 instead (see issue #385).
set(MPRJ_DEBUG_INFO_FLAG "/Zi" CACHE STRING "Optional flag specifying specific /Z flag to use")

# Platform-specific compiler/linker flags.
set(MPRJ_LIBTYPE                 SHARED)
# /MP                   = Multiprocess compilation
# /Gy                   = Enable function-level linking
# /GR-                  = Disable run-time type information
# /W4                   = Warning level 4
# /WX                   = Treat warnings as errors
# /wd"4100"             = Ignore "unreferenced formal parameter" warning
# /wd"4127"             = Ignore "conditional expression is constant" warning
# /wd"4244"             = Ignore "conversion possible loss of data" warning
# /wd"4512"             = Ignore "assignment operator could not be generated" warning
# /wd"4701"             = Ignore "potentially uninitialized local variable" warning
# /wd"4702"             = Ignore "unreachable code" warning
# /wd"4996"             = Ignore "function or variable may be unsafe" warning
set(MPRJ_COMPILER_FLAGS          "/MP /Gy /GR- /W4 /wd\"4100\" /wd\"4127\" /wd\"4244\" /wd\"4512\" /wd\"4701\" /wd\"4702\" /wd\"4996\" ${MPRJ_DEBUG_INFO_FLAG}")
# /MDd                  = Multithreaded Dll debug runtime
# /Od                   = Disable optimizations
# /RTC1                 = Enable basic run-time checks
set(MPRJ_COMPILER_FLAGS_DEBUG    "/MDd /RTC1 /Od")
# /MD                   = Multithreaded Dll release runtime
# /O2                   = Optimize for maximum speed
# /Ob2                  = Inline any suitable function
# /GF                   = Enable string pooling
# /D NDEBUG /D _NDEBUG  = Not a debug build
set(MPRJ_COMPILER_FLAGS_RELEASE  "/MD /O2 /Ob2 /GF /D NDEBUG /D _NDEBUG")
# /DEBUG                = Generate debug information
set(MPRJ_LINKER_FLAGS_DEBUG      "/DEBUG")
# /MANIFEST:NO          = No default manifest (see ADD_WINDOWS_MANIFEST macro usage)
set(MPRJ_EXE_LINKER_FLAGS        "/MANIFEST:NO")
# /SUBSYSTEM:CONSOLE    = CONSOLE
# /SUBSYSTEM:WINDOWS    = WINDOWS
set(MPRJ_EXE_LINKER_FLAGS        "/SUBSYSTEM:CONSOLE")


# Standard definitions
# -DWIN32 -D_WIN32 -D_WINDOWS           = Windows platform
# -DUNICODE -D_UNICODE                  = Unicode build
# -DWINVER=0x0602 -D_WIN32_WINNT=0x602  = Targeting Windows 8
# -DNOMINMAX                            = Use the standard's templated min/max
# -DWIN32_LEAN_AND_MEAN                 = Exclude less common API declarations
# -D_HAS_EXCEPTIONS=0                   = Disable exceptions
add_definitions(-DWIN32 -D_WIN32 -D_WINDOWS -DUNICODE -D_UNICODE)


# MPRJ directory paths.
set(MPRJ_RESOURCE_DIR        "${CMAKE_CURRENT_SOURCE_DIR}/Resources")
set(MPRJ_BINARY_DIR          "${CMAKE_CURRENT_SOURCE_DIR}/$<CONFIGURATION>")
set(MPRJ_BINARY_DIR_DEBUG    "${CMAKE_CURRENT_SOURCE_DIR}/Debug")
set(MPRJ_BINARY_DIR_RELEASE  "${CMAKE_CURRENT_SOURCE_DIR}/Release")

#---------------------------------------------------------------------------------------------------------
set(CMAKE_C_FLAGS                     "${MPRJ_COMPILER_FLAGS} ${MPRJ_C_COMPILER_FLAGS}")
set(CMAKE_C_FLAGS_DEBUG               "${MPRJ_COMPILER_FLAGS_DEBUG} ${MPRJ_C_COMPILER_FLAGS_DEBUG}")
set(CMAKE_C_FLAGS_RELEASE             "${MPRJ_COMPILER_FLAGS_RELEASE} ${MPRJ_C_COMPILER_FLAGS_RELEASE}")
set(CMAKE_CXX_FLAGS                   "${MPRJ_COMPILER_FLAGS} ${MPRJ_CXX_COMPILER_FLAGS}")
set(CMAKE_CXX_FLAGS_DEBUG             "${MPRJ_COMPILER_FLAGS_DEBUG} ${MPRJ_CXX_COMPILER_FLAGS_DEBUG}")
set(CMAKE_CXX_FLAGS_RELEASE           "${MPRJ_COMPILER_FLAGS_RELEASE} ${MPRJ_CXX_COMPILER_FLAGS_RELEASE}")
set(CMAKE_EXE_LINKER_FLAGS            "${MPRJ_LINKER_FLAGS} ${MPRJ_EXE_LINKER_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS_DEBUG      "${MPRJ_LINKER_FLAGS_DEBUG} ${MPRJ_EXE_LINKER_FLAGS_DEBUG}")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE    "${MPRJ_LINKER_FLAGS_RELEASE} ${MPRJ_EXE_LINKER_FLAGS_RELEASE}")
set(CMAKE_SHARED_LINKER_FLAGS         "${MPRJ_LINKER_FLAGS} ${MPRJ_SHARED_LINKER_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS_DEBUG   "${MPRJ_LINKER_FLAGS_DEBUG} ${MPRJ_SHARED_LINKER_FLAGS_DEBUG}")
set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${MPRJ_LINKER_FLAGS_RELEASE} ${MPRJ_SHARED_LINKER_FLAGS_RELEASE}")
#---------------------------------------------------------------------------------------------------------
add_subdirectory(src)


#---------------------------------------------------------------------------------------------------------
message(STATUS "*** CONFIGURATION SETTINGS ***")
message(STATUS "Generator:                    ${CMAKE_GENERATOR}")
message(STATUS "Platform:                     ${CMAKE_SYSTEM_NAME}")
message(STATUS "Project architecture:         ${MPRJ_ARCH}")
message(STATUS "Project Language:             ${MPRJ_LANG}")

set(LIBRARIES ${MPRJ_STANDARD_LIBS})
message(STATUS "Standard libraries:           ${LIBRARIES}")

get_directory_property(DEFINITIONS COMPILE_DEFINITIONS)
message(STATUS "Compiler definitions:         ${DEFINITIONS}")

message(STATUS "C_FLAGS:                      ${CMAKE_C_FLAGS}")
message(STATUS "C_FLAGS_DEBUG:                ${CMAKE_C_FLAGS_DEBUG}")
message(STATUS "C_FLAGS_RELEASE:              ${CMAKE_C_FLAGS_RELEASE}")
message(STATUS "CXX_FLAGS:                    ${CMAKE_CXX_FLAGS}")
message(STATUS "CXX_FLAGS_DEBUG:              ${CMAKE_CXX_FLAGS_DEBUG}")
message(STATUS "CXX_FLAGS_RELEASE:            ${CMAKE_CXX_FLAGS_RELEASE}")
message(STATUS "EXE_LINKER_FLAGS:             ${CMAKE_EXE_LINKER_FLAGS}")
message(STATUS "EXE_LINKER_FLAGS_DEBUG:       ${CMAKE_EXE_LINKER_FLAGS_DEBUG}")
message(STATUS "EXE_LINKER_FLAGS_RELEASE:     ${CMAKE_EXE_LINKER_FLAGS_RELEASE}")
message(STATUS "SHARED_LINKER_FLAGS:          ${CMAKE_SHARED_LINKER_FLAGS}")
message(STATUS "SHARED_LINKER_FLAGS_DEBUG:    ${CMAKE_SHARED_LINKER_FLAGS_DEBUG}")
message(STATUS "SHARED_LINKER_FLAGS_RELEASE:  ${CMAKE_SHARED_LINKER_FLAGS_RELEASE}")

message(STATUS "MPRJ Binary files:             ${MPRJ_BINARY_FILES}")
message(STATUS "MPRJ Resource files:           ${MPRJ_RESOURCE_FILES}")
