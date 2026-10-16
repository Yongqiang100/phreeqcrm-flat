# src/interfaces/c: files compiled into the PhreeqcRM library,
# exactly the upstream PhreeqcRM_SOURCES entries of this layer,
# in upstream order (cmake/upstream/CMakeLists.txt lines 140-317).
set(PHREEQCRM_SOURCES_INTERFACES_C
  ${CMAKE_CURRENT_LIST_DIR}/BMI_interface_C.cpp
  ${CMAKE_CURRENT_LIST_DIR}/BMI_interface_C.h
  ${CMAKE_CURRENT_LIST_DIR}/RM_interface_C.cpp
  ${CMAKE_CURRENT_LIST_DIR}/RM_interface_C.h
  ${CMAKE_CURRENT_LIST_DIR}/YAML_interface_C.cpp
  ${CMAKE_CURRENT_LIST_DIR}/YAML_interface_C.h
)
