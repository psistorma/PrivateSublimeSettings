#
# Shared macros.
#

# Add ARX support
macro(MMACRO_ARX_MODUAL)
  add_definitions(-DACRXAPP)
  add_definitions(-D_AFXDLL)
  set(CMAKE_MFC_FLAG 2)
endmacro()

# Add normal MFC support
macro(MMACRO_MFC_MODUAL)
  set(CMAKE_MFC_FLAG 2)
endmacro()

# Add As MFC EXE
macro(MMACRO_MFC_EXE)
  set(CMAKE_MFC_FLAG 2)
endmacro()

# Add PreComiler support
macro(MMACRO_ADD_PRECOMPILE)
  add_compile_options(/Yu"stdafx.h")
  set_source_files_properties(stdafx.cpp PROPERTIES COMPILE_FLAGS /Yc\"stdafx.h\")
endmacro()

# Merge list by an add list and a removed list.
macro(MMACRO_MERGE_LIST name_of_list)
  list(APPEND ${name_of_list} ${${name_of_list}_ADD})
  if(${${name_of_list}_REMOVE})
    list(REMOVE_ITEM ${name_of_list} ${${name_of_list}_REMOVE})
  endif()
endmacro()

# Determine the target output directory.
macro(MMACRO_SET_TARGET_OUT_DIR)
  set(LIBRARY_OUTPUT_PATH ${MPRJ_OUT_DIR})
endmacro()

# Copy a list of files from one directory to another. Relative files paths are maintained.
macro(COPY_FILES target file_list source_dir target_dir)
  foreach(FILENAME ${file_list})
    set(source_file ${source_dir}/${FILENAME})
    set(target_file ${target_dir}/${FILENAME})
    if(IS_DIRECTORY ${source_file})
      add_custom_command(
        TARGET ${target}
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${source_file}" "${target_file}"
        VERBATIM
        )
    else()
      add_custom_command(
        TARGET ${target}
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${source_file}" "${target_file}"
        VERBATIM
        )
    endif()
  endforeach()
endmacro()

# Rename a directory replacing the target if it already exists.
macro(RENAME_DIRECTORY target source_dir target_dir)
  add_custom_command(
    TARGET ${target}
    POST_BUILD
    # Remove the target directory if it already exists.
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${target_dir}"
    # Rename the source directory to target directory.
    COMMAND ${CMAKE_COMMAND} -E rename "${source_dir}" "${target_dir}"
    VERBATIM
    )
endmacro()

# Add custom manifest files to an executable target.
macro(ADD_WINDOWS_MANIFEST manifest_path target)
  add_custom_command(
    TARGET ${target}
    POST_BUILD
    COMMAND "mt.exe" -nologo
            -manifest \"${manifest_path}/${target}.manifest\"
            -outputresource:"${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${target}.exe"\;\#1
    COMMENT "Adding manifest..."
    )
endmacro()
