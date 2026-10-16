# src/interfaces/fortran: files compiled into the PhreeqcRM library,
# exactly the upstream PhreeqcRM_SOURCES entries of this layer,
# in upstream order (cmake/upstream/CMakeLists.txt lines 140-317).
set(PHREEQCRM_SOURCES_INTERFACES_FORTRAN
  ${CMAKE_CURRENT_LIST_DIR}/BMI_interface_F.cpp
  ${CMAKE_CURRENT_LIST_DIR}/BMI_interface_F.h
  ${CMAKE_CURRENT_LIST_DIR}/RM_interface_F.cpp
  ${CMAKE_CURRENT_LIST_DIR}/RM_interface_F.h
  ${CMAKE_CURRENT_LIST_DIR}/YAML_interface_F.cpp
  ${CMAKE_CURRENT_LIST_DIR}/YAML_interface_F.h
)
