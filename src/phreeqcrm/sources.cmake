# src/phreeqcrm: files compiled into the PhreeqcRM library,
# exactly the upstream PhreeqcRM_SOURCES entries of this layer,
# in upstream order (cmake/upstream/CMakeLists.txt lines 140-317).
set(PHREEQCRM_SOURCES_PHREEQCRM
  ${CMAKE_CURRENT_LIST_DIR}/bmi.hxx
  ${CMAKE_CURRENT_LIST_DIR}/BMIPhreeqcRM.cpp
  ${CMAKE_CURRENT_LIST_DIR}/BMIPhreeqcRM.h
  ${CMAKE_CURRENT_LIST_DIR}/BMIVariant.cpp
  ${CMAKE_CURRENT_LIST_DIR}/BMIVariant.h
  ${CMAKE_CURRENT_LIST_DIR}/IrmResult.h
  ${CMAKE_CURRENT_LIST_DIR}/PhreeqcRM.cpp
  ${CMAKE_CURRENT_LIST_DIR}/PhreeqcRM.h
  ${CMAKE_CURRENT_LIST_DIR}/RMVARS.h
  ${CMAKE_CURRENT_LIST_DIR}/VarManager.cpp
  ${CMAKE_CURRENT_LIST_DIR}/VarManager.h
  ${CMAKE_CURRENT_LIST_DIR}/YAMLPhreeqcRM.cpp
  ${CMAKE_CURRENT_LIST_DIR}/YAMLPhreeqcRM.h
)
