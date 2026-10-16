# src/iphreeqc: files compiled into the PhreeqcRM library,
# exactly the upstream PhreeqcRM_SOURCES entries of this layer,
# in upstream order (cmake/upstream/CMakeLists.txt lines 140-317).
set(PHREEQCRM_SOURCES_IPHREEQC
  ${CMAKE_CURRENT_LIST_DIR}/CSelectedOutput.cpp
  ${CMAKE_CURRENT_LIST_DIR}/CSelectedOutput.hxx
  ${CMAKE_CURRENT_LIST_DIR}/CVar.hxx
  ${CMAKE_CURRENT_LIST_DIR}/Debug.h
  ${CMAKE_CURRENT_LIST_DIR}/ErrorReporter.hxx
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqc_interface_F.cpp
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqc_interface_F.h
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqc.cpp
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqc.h
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqc.hpp
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqcCallbacks.h
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqcLib.cpp
  ${CMAKE_CURRENT_LIST_DIR}/thread.h
  ${CMAKE_CURRENT_LIST_DIR}/Var.c
  ${CMAKE_CURRENT_LIST_DIR}/Var.h
  ${CMAKE_CURRENT_LIST_DIR}/Version.h
)
