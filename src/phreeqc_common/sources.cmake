# src/phreeqc_common: files compiled into the PhreeqcRM library,
# exactly the upstream PhreeqcRM_SOURCES entries of this layer,
# in upstream order (cmake/upstream/CMakeLists.txt lines 140-317).
set(PHREEQCRM_SOURCES_PHREEQC_COMMON
  ${CMAKE_CURRENT_LIST_DIR}/Parser.cxx
  ${CMAKE_CURRENT_LIST_DIR}/Parser.h
  ${CMAKE_CURRENT_LIST_DIR}/PHRQ_base.cxx
  ${CMAKE_CURRENT_LIST_DIR}/PHRQ_base.h
  ${CMAKE_CURRENT_LIST_DIR}/PHRQ_exports.h
  ${CMAKE_CURRENT_LIST_DIR}/PHRQ_io.cpp
  ${CMAKE_CURRENT_LIST_DIR}/PHRQ_io.h
  ${CMAKE_CURRENT_LIST_DIR}/phrqtype.h
  ${CMAKE_CURRENT_LIST_DIR}/Utils.cxx
  ${CMAKE_CURRENT_LIST_DIR}/Utils.h
)
