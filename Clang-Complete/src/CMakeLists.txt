#---------------------------Target--------------------------------------------
set(MMOD_TARGET "src")
# MMACRO_MFC_EXE()
#---------------------------Source--------------------------------------------
file(GLOB MMOD_HEADER_ADD *.h *.hpp)
file(GLOB MMOD_SRC_ADD *.c *.cpp *.cc)
file(GLOB MMOD_RES_ADD res/* *.rc)

file(GLOB MMOD_HEADER_REMOVE )
file(GLOB MMOD_SRC_REMOVE )
file(GLOB MMOD_RES_REMOVE )

MMACRO_MERGE_LIST(MMOD_HEADER)
MMACRO_MERGE_LIST(MMOD_SRC)
MMACRO_MERGE_LIST(MMOD_RES)


set(MMOD_FILE ${MMOD_HEADER} ${MMOD_SRC} ${MMOD_RES})

source_group("Inculde Files" FILES ${MMOD_HEADER})
source_group("Source Files" FILES ${MMOD_SRC})
source_group("Resource Files" FILES ${MMOD_RES})
#----------------------------Support---------------------------------------------
# MMACRO_ADD_PRECOMPILE()
# MMACRO_SET_TARGET_OUT_DIR()
add_executable(${MMOD_TARGET} WIN32 ${MMOD_FILE})

# add_library(libclang SHARED IMPORTED)
# set_target_properties(libclang PROPERTIES IMPORTED_LOCATION "C:\\Program Files\\LLVM\\lib\\libclang.lib")

target_link_libraries(${MMOD_TARGET} "C:\\Program Files\\LLVM\\lib\\libclang.lib" "C:\\Program Files\\LLVM\\lib\\clang\\3.7.1\\lib\\windows\\clang_rt.ubsan_standalone_cxx-x86_64.lib")
#----------------------------Post---------------------------------------------
# Add the custom manifest files to the executable.
# ADD_WINDOWS_MANIFEST("${CMAKE_CURRENT_SOURCE_DIR}" "${MMOD_TARGET}")

