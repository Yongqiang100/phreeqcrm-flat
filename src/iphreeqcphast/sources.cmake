# src/iphreeqcphast: files compiled into the PhreeqcRM library,
# exactly the upstream PhreeqcRM_SOURCES entries of this layer,
# in upstream order (cmake/upstream/CMakeLists.txt lines 140-317).
set(PHREEQCRM_SOURCES_IPHREEQCPHAST
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqcPhast.cxx
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqcPhast.h
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqcPhastLib.cpp
  ${CMAKE_CURRENT_LIST_DIR}/IPhreeqcPhastLib.h
)
