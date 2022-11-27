find_package(PkgConfig)

PKG_CHECK_MODULES(PC_SIGMF_UTILS sigmf_utils)

FIND_PATH(
    SIGMF_UTILS_INCLUDE_DIRS
    NAMES sigmf_utils/api.h
    HINTS $ENV{SIGMF_UTILS_DIR}/include
        ${PC_SIGMF_UTILS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SIGMF_UTILS_LIBRARIES
    NAMES gnuradio-sigmf_utils
    HINTS $ENV{SIGMF_UTILS_DIR}/lib
        ${PC_SIGMF_UTILS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/sigmf_utilsTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SIGMF_UTILS DEFAULT_MSG SIGMF_UTILS_LIBRARIES SIGMF_UTILS_INCLUDE_DIRS)
MARK_AS_ADVANCED(SIGMF_UTILS_LIBRARIES SIGMF_UTILS_INCLUDE_DIRS)
