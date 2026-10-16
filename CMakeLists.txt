cmake_minimum_required(VERSION 3.22...4.1)

project(
  PhreeqcRM
  VERSION 3.8.0
  LANGUAGES CXX C
)

# Adapted from pyzmq's CMake build logic to be compatible with yaml-cpp
# https://github.com/zeromq/pyzmq/blob/9007d88dd316328fd3ddd11380f94914dbcf687c/CMakeLists.txt#L327-L337
if ("${CMAKE_POLICY_VERSION_MINIMUM}" STREQUAL "")
  if (CMAKE_VERSION VERSION_GREATER_EQUAL "3.31")
    set(CMAKE_POLICY_VERSION_MINIMUM "3.31")
  else()
    set(CMAKE_POLICY_VERSION_MINIMUM "${CMAKE_VERSION_MAJOR}.${CMAKE_VERSION_MINOR}")
  endif()
  message(STATUS "Setting CMAKE_POLICY_VERSION_MINIMUM=${CMAKE_POLICY_VERSION_MINIMUM} for yaml-cpp")
endif()

if(DEFINED SKBUILD)
  include(CheckPIESupported)
  check_pie_supported()
  set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

# check if this is the root project
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
  set(STANDALONE_BUILD 1)
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
  add_compile_options($<$<CXX_COMPILER_ID:MSVC>:/MP>)
else()
  set(STANDALONE_BUILD 0)
endif()

# overide docdir on windows
if(WIN32 AND NOT CMAKE_INSTALL_DOCDIR)
  set(CMAKE_INSTALL_DOCDIR "" CACHE PATH "documentation root (doc)")
  set(CMAKE_INSTALL_DOCDIR "doc")
endif()

include(GNUInstallDirs)

option(PHREEQCRM_FORTRAN_TESTING "Build Fortran test" OFF)
if(PHREEQCRM_FORTRAN_TESTING)
  enable_language(Fortran)
endif()

# Include FetchContent module
include(FetchContent)

if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)

  # Fetch zlib
  FetchContent_Declare(
    zlib
    URL https://github.com/madler/zlib/releases/download/v1.3.1/zlib-1.3.1.tar.gz
  )

  # Don't install zlib in wheel
  set(SKIP_INSTALL_ALL ON)
  # Make zlib available
  FetchContent_MakeAvailable(zlib)
endif()

option(PHREEQCRM_WITH_YAML_CPP "Build with yaml-cpp support" OFF)
if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
  set(PHREEQCRM_WITH_YAML_CPP ON)
endif()
if(PHREEQCRM_WITH_YAML_CPP)
  # Initialize a static build for yaml-cpp
  if(DEFINED SKBUILD)
    # Use force for wheel builds
    set(YAML_BUILD_SHARED_LIBS OFF CACHE STRING "" FORCE)
    set(YAML_CPP_INSTALL OFF CACHE STRING "" FORCE)
  else()
    # w/o the FORCE option the user can override using -DYAML_BUILD_SHARED_LIBS=ON
    set(YAML_BUILD_SHARED_LIBS OFF CACHE STRING "")

    # w/o the FORCE option the user can override using -DYAML_CPP_INSTALL=OFF
    set(YAML_CPP_INSTALL ON CACHE STRING "")
  endif()

  # Fetch yaml-cpp
  FetchContent_Declare(
    yaml-cpp
    URL https://github.com/jbeder/yaml-cpp/archive/refs/tags/0.8.0.tar.gz
    OVERRIDE_FIND_PACKAGE
  )

  # The following will automatically forward through to FetchContent_MakeAvailable()
  find_package(yaml-cpp REQUIRED)
  if(yaml-cpp_FOUND)
    if(DEFINED yaml-cpp_VERSION)
      message(STATUS "Found yaml-cpp: TRUE (found version \"${yaml-cpp_VERSION}\")")
    else()
      message(STATUS "Found yaml-cpp: TRUE")
    endif()
  endif()
endif()

option(PHREEQCRM_DISABLE_OPENMP "Disable openmp" OFF)
if(NOT PHREEQCRM_DISABLE_OPENMP)
  if(STANDALONE_BUILD EQUAL 1)
    # check for openmp
    find_package(OpenMP)
  endif()
endif()

# check for MPI
option(PHREEQCRM_BUILD_MPI "Build MPI configuration" OFF)
if(PHREEQCRM_BUILD_MPI)
  find_package(MPI REQUIRED)
endif()

option(PHREEQCRM_BUILD_PYTHON "Build python wrapper using SWIG" OFF)
if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
  set(PHREEQCRM_BUILD_PYTHON ON)
endif()
if(PHREEQCRM_BUILD_PYTHON)
  if(NOT PHREEQCRM_WITH_YAML_CPP)
    message(FATAL_ERROR "Building python wrapper requires PHREEQCRM_WITH_YAML_CPP.")
  endif()
  find_package(SWIG REQUIRED)
  ###find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development Development.Module NumPy)
  find_package(Python COMPONENTS Interpreter Development.Module NumPy REQUIRED)
  # Set Python_ROOT_DIR to specify which python to use
  # ie -DPython_ROOT_DIR=C:/Python38-x64
endif()

if(DEFINED SKBUILD)
  # see https://scikit-build-core.readthedocs.io/en/latest/cmakelists.html
  set(Python_SOABI ${SKBUILD_SOABI})
endif()

option(PHREEQCRM_NO_UTF8_ENCODING "Build without utf-8 encoding" OFF)

# Source list (FL-D6): one file per layer, each setting one variable with the
# upstream PhreeqcRM_SOURCES entries of that layer, in upstream order.
include(${CMAKE_CURRENT_SOURCE_DIR}/src/phreeqc_common/sources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/src/phreeqc/sources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/src/iphreeqc/sources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/src/iphreeqcphast/sources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/src/phreeqcrm/sources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/src/interfaces/c/sources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/src/interfaces/fortran/sources.cmake)

set(PhreeqcRM_SOURCES
  ${PHREEQCRM_SOURCES_PHREEQC_COMMON}
  ${PHREEQCRM_SOURCES_PHREEQC}
  ${PHREEQCRM_SOURCES_IPHREEQC}
  ${PHREEQCRM_SOURCES_IPHREEQCPHAST}
  ${PHREEQCRM_SOURCES_PHREEQCRM}
  ${PHREEQCRM_SOURCES_INTERFACES_C}
  ${PHREEQCRM_SOURCES_INTERFACES_FORTRAN}
)

# dll/shared objects
option(BUILD_SHARED_LIBS "Build Shared Libraries" OFF)

add_library(PhreeqcRM ${PhreeqcRM_SOURCES})
add_library(PhreeqcRM::PhreeqcRM ALIAS PhreeqcRM)

target_include_directories(PhreeqcRM
  PUBLIC
    $<BUILD_INTERFACE:${PhreeqcRM_BINARY_DIR}>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/phreeqcrm>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/interfaces/c>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/interfaces/fortran>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/iphreeqc>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/iphreeqcphast>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/phreeqc>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/phreeqc/keywords>
    $<BUILD_INTERFACE:${PhreeqcRM_SOURCE_DIR}/src/phreeqc_common>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# generate "${PhreeqcRM_BINARY_DIR}/irm_dll_export.h"
# based on how the PhreeqcRM library is built (BUILD_SHARED_LIBS)
include(GenerateExportHeader)
generate_export_header(PhreeqcRM BASE_NAME IRM_DLL)

# c++11
target_compile_features(PhreeqcRM PUBLIC cxx_std_11)

# iphreeqc defs
target_compile_definitions(PhreeqcRM PRIVATE SWIG_SHARED_OBJ)
target_compile_definitions(PhreeqcRM PRIVATE USE_PHRQ_ALLOC)
target_compile_definitions(PhreeqcRM PRIVATE IPhreeqc_EXPORTS)

if (PHREEQCRM_NO_UTF8_ENCODING)
  target_compile_definitions(PhreeqcRM PRIVATE NO_UTF8_ENCODING)
endif()

# Disable deprecation warnings for standard C and STL functions in VS2005
# and later
if(MSVC_VERSION EQUAL 1400 OR MSVC_VERSION GREATER 1400)
  target_compile_definitions(PhreeqcRM PRIVATE _CRT_SECURE_NO_DEPRECATE)
  target_compile_definitions(PhreeqcRM PRIVATE _SCL_SECURE_NO_WARNINGS)
endif()

if (WIN32 AND BUILD_SHARED_LIBS)
  # Required to build IMPLIB
  # (Seems to be automatically set when using Visual Studio as the generator)
  # This is only necessary to export iphreeqc methods
  # iphreeqc should be updated to use generate_export_header
  target_compile_definitions(PhreeqcRM PRIVATE _WINDLL)
endif()

# init exportPackageDependencies
set(exportPackageDependencies "")

# yaml-cpp
if(PHREEQCRM_WITH_YAML_CPP AND yaml-cpp_FOUND)
  target_compile_definitions(PhreeqcRM PUBLIC USE_YAML)
  if(TARGET yaml-cpp::yaml-cpp)
    target_link_libraries(PhreeqcRM PUBLIC yaml-cpp::yaml-cpp)
  else()
    target_link_libraries(PhreeqcRM PUBLIC yaml-cpp)
  endif()
  string(APPEND exportPackageDependencies "find_dependency(yaml-cpp)\n")
  # set(phreeqcrm_requires "yaml-cpp")
  set(useyaml_define "-DUSE_YAML")
endif()
if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
  target_compile_definitions(PhreeqcRM PUBLIC USE_YAML)
  target_link_libraries(PhreeqcRM PUBLIC yaml-cpp)
endif()

# check for zlib
if(NOT ZLIB_ROOT)
  if(EXISTS $ENV{ZLIB_ROOT})
    set(ZLIB_ROOT $ENV{ZLIB_ROOT})
  endif()
endif()
option(PHREEQCRM_USE_ZLIB "Use zlib compression for dump files" OFF)
if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
  set(PHREEQCRM_USE_ZLIB ON)
endif()
if(PHREEQCRM_USE_ZLIB AND NOT DEFINED SKBUILD)
  find_package(ZLIB REQUIRED)
endif()

if(PHREEQCRM_USE_ZLIB AND ZLIB_FOUND)
  target_compile_definitions(PhreeqcRM PRIVATE USE_GZ)
  target_link_libraries(PhreeqcRM PRIVATE ZLIB::ZLIB)
  string(APPEND exportPackageDependencies "find_dependency(ZLIB)\n")
endif()
if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
  target_compile_definitions(PhreeqcRM PRIVATE USE_GZ)
  # for the wheel link to static zlib
  target_link_libraries(PhreeqcRM PRIVATE zlibstatic)
endif()

# Allow user to override POSTFIX properties (but mandate them so that
# all builds can be installed to the same directory)
if(NOT CMAKE_DEBUG_POSTFIX)
  set_target_properties(PhreeqcRM PROPERTIES DEBUG_POSTFIX "d")
endif()

# # At least with MSMPI PhreeqcRM.dll requires MPI_CXX_LIBRARIES to link
# if(MSVC AND BUILD_SHARED_LIBS AND PHREEQCRM_BUILD_MPI)
#   target_link_libraries(PhreeqcRM ${MPI_CXX_LIBRARIES})
# endif()

# if(MSVC AND BUILD_SHARED_LIBS AND PHREEQCRM_USE_ZLIB AND ZLIB_FOUND)
#   target_link_libraries(PhreeqcRM ${ZLIB_LIBRARIES})
# endif()

set(PhreeqcRM_Headers
  ${PhreeqcRM_BINARY_DIR}/irm_dll_export.h
  ${PROJECT_SOURCE_DIR}/src/interfaces/c/BMI_interface_C.h
  ${PROJECT_SOURCE_DIR}/src/interfaces/fortran/BMI_interface_F.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/BMIVariant.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/bmi.hxx
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/BMIPhreeqcRM.h
  ${PROJECT_SOURCE_DIR}/src/iphreeqc/IPhreeqc.h
  ${PROJECT_SOURCE_DIR}/src/iphreeqc/IPhreeqc.hpp
  ${PROJECT_SOURCE_DIR}/src/iphreeqc/IPhreeqcCallbacks.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc_common/Parser.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc_common/PHRQ_base.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc_common/PHRQ_exports.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc_common/PHRQ_io.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc_common/phrqtype.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc/NameDouble.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc/keywords/Keywords.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc/StorageBin.h
  ${PROJECT_SOURCE_DIR}/src/phreeqc/System.h
  ${PROJECT_SOURCE_DIR}/src/iphreeqc/Var.h
  ${PROJECT_SOURCE_DIR}/src/iphreeqcphast/IPhreeqcPhast.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/IrmResult.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/PhreeqcRM.h
  ${PROJECT_SOURCE_DIR}/src/interfaces/c/RM_interface_C.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/RMVARS.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/VarManager.h
  ${PROJECT_SOURCE_DIR}/src/interfaces/c/YAML_interface_C.h
  ${PROJECT_SOURCE_DIR}/src/interfaces/fortran/YAML_interface_F.h
  ${PROJECT_SOURCE_DIR}/src/phreeqcrm/YAMLPhreeqcRM.h
)

set(PhreeqcRM_SRC
  ${PROJECT_SOURCE_DIR}/src/interfaces/fortran/BMI_interface.F90
  ${PROJECT_SOURCE_DIR}/src/interfaces/fortran/BMI_not_implemented.inc
  ${PROJECT_SOURCE_DIR}/src/iphreeqc/IPhreeqc_interface.F90
  ${PROJECT_SOURCE_DIR}/src/interfaces/fortran/RM_interface.F90
  ${PROJECT_SOURCE_DIR}/src/interfaces/fortran/YAML_interface.F90
)

if(PHREEQCRM_BUILD_MPI)
  # USE_MPI needs to be public in order to compile the
  # fortran interface files
  target_compile_definitions(PhreeqcRM PUBLIC USE_MPI)
  target_link_libraries(PhreeqcRM PUBLIC MPI::MPI_CXX)
  set(usempi_define "-DUSE_MPI")
  string(APPEND exportPackageDependencies "find_dependency(MPI)\n")
else()
  if(NOT PHREEQCRM_DISABLE_OPENMP)
    if(OPENMP_FOUND)
      target_compile_definitions(PhreeqcRM PRIVATE USE_OPENMP)
      target_link_libraries(PhreeqcRM PUBLIC OpenMP::OpenMP_CXX)
      string(APPEND exportPackageDependencies "find_dependency(OpenMP)\n")
      if(PHREEQCRM_FORTRAN_TESTING)
        target_link_libraries(PhreeqcRM PUBLIC OpenMP::OpenMP_Fortran)
      endif()
    endif()
  endif()
endif()

# pkg-config
# Skip imported link libraries
#
# set(PKGCONFIG_LIBS "")
# set(PKGCONFIG_INCS "")
# set(PHREEQCRM_OpenMP_C_FLAGS "")
# if(NOT PHREEQCRM_DISABLE_OPENMP AND OpenMP_FOUND)
#   set(PHREEQCRM_OpenMP_C_FLAGS ${OpenMP_C_FLAGS})
# endif()
# get_target_property(_link_libs PhreeqcRM LINK_LIBRARIES)
# if (_link_libs)
#   foreach(_link_lib ${_link_libs})
#     cmake_print_variables(_link_lib)
#     get_target_property(_imported ${_link_lib} IMPORTED)
#     if(_imported)
#       get_target_property(_incs ${_link_lib} INTERFACE_INCLUDE_DIRECTORIES)
#       if(_incs)
#         foreach(_inc ${_incs})
#           string(APPEND PKGCONFIG_INCS " -I${_inc}")
#         endforeach()
#       endif()
#       get_target_property(_loc ${_link_lib} LOCATION)
#       if (_loc)
#         string(APPEND PKGCONFIG_LIBS " ${_loc}")
#       else()
#         get_target_property(_libs ${_link_lib} INTERFACE_LINK_LIBRARIES)
#         if(_libs)
#           foreach(_lib ${_libs})
#             string(APPEND PKGCONFIG_LIBS " ${_lib}")
#           endforeach()
#         endif()
#       endif()
#     endif()
#   endforeach()
#   if(PKGCONFIG_INCS)
#     string(STRIP ${PKGCONFIG_INCS} PKGCONFIG_INCS)
#   endif()
#   if(PKGCONFIG_LIBS)
#     string(STRIP ${PKGCONFIG_LIBS} PKGCONFIG_LIBS)
#   endif()
# endif()
configure_file(cmake/templates/phreeqcrm.cmake.in phreeqcrm.pc @ONLY)

# install
if(STANDALONE_BUILD EQUAL 1 AND NOT DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)

  include(CMakePackageConfigHelpers)

  configure_package_config_file(cmake/templates/PhreeqcRMConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/PhreeqcRMConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/PhreeqcRM
  )

  write_basic_package_version_file("PhreeqcRMConfigVersion.cmake"
    VERSION ${PhreeqcRM_VERSION}
    COMPATIBILITY SameMajorVersion
  )

  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/PhreeqcRMConfig.cmake ${CMAKE_CURRENT_BINARY_DIR}/PhreeqcRMConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/PhreeqcRM
  )

  if(PHREEQCRM_WITH_YAML_CPP AND yaml-cpp_FOUND)
    install(TARGETS PhreeqcRM yaml-cpp
      EXPORT   PhreeqcRMTargets
      LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
      ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
      RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR}
      INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
  else()
    install(TARGETS PhreeqcRM
      EXPORT   PhreeqcRMTargets
      LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
      ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
      RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR}
      INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
  endif()

  install(EXPORT PhreeqcRMTargets
    FILE PhreeqcRMTargets.cmake
    NAMESPACE PhreeqcRM::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/PhreeqcRM
  )

  install(FILES ${PhreeqcRM_Headers}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )

  install(FILES ${PhreeqcRM_SRC}
    # @todo consider installing into INCLUDE directory
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/PhreeqcRM/src
  )

  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/phreeqcrm.pc
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig
  )
else()
  # option(PHREEQCRM_INSTALL_TARGETS "" OFF)
  if(PHREEQCRM_INSTALL_TARGETS)
    install(TARGETS PhreeqcRM DESTINATION ${CMAKE_INSTALL_LIBDIR})
  endif()
endif()

if(WIN32)
  # PHREEQCRM_STATIC_RUNTIME (VCOMP???.dll) cannot be made static
  option(PHREEQCRM_STATIC_RUNTIME "Build with a static runtime (excluding OpenMP dlls)" OFF)
  if(PHREEQCRM_STATIC_RUNTIME)
    # compile with static runtime
    set_property(TARGET PhreeqcRM PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
  endif()
endif()

# TODO PHREEQCRM_ENABLE_TESTING
if(STANDALONE_BUILD EQUAL 1)
  # tests
  enable_testing()

  # subdirs
  if(NOT DEFINED SKBUILD)
    # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
    add_subdirectory(database)
    add_subdirectory(docs/upstream/doc)
    add_subdirectory(docs/doxygen)
    add_subdirectory(tests)
  endif()

  if(PHREEQCRM_BUILD_PYTHON)
    add_subdirectory(python/swig)
  endif()
endif()

# Turn off Incremental Linking for Debug and RelWithDebInfo
if(MSVC)
  target_link_options(PhreeqcRM PRIVATE $<$<CONFIG:Debug,RelWithDebInfo>:/INCREMENTAL:NO>)
endif()

if(DEFINED SKBUILD)
  # SKBUILD is defined when scikit-build-core is used to build python wheels (see pyproject.toml)
  message(STATUS "SKBUILD IS defined")
  #set_target_properties(PhreeqcRM TestRM TestBMIdtor TestRMdtor PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)
  set_target_properties(PhreeqcRM PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)
  message(STATUS "SKIP_INSTALL_ALL=${SKIP_INSTALL_ALL}")
  if (SKIP_INSTALL_ALL)
    message(STATUS "SKIP_INSTALL_ALL TRUE")
  else()
    message(STATUS "SKIP_INSTALL_ALL TRUE")
  endif()
else()
  message(STATUS "SKBUILD is NOT defined")
endif()

# get_cmake_property(_variableNames VARIABLES)
# list (SORT _variableNames)
# foreach (_variableName ${_variableNames})
#   message(STATUS "${_variableName}=${${_variableName}}")
# endforeach()
