find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_SIGMF_UTILS gnuradio-sigmf_utils)

FIND_PATH(
    GR_SIGMF_UTILS_INCLUDE_DIRS
    NAMES gnuradio/sigmf_utils/api.h
    HINTS $ENV{SIGMF_UTILS_DIR}/include
        ${PC_SIGMF_UTILS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_SIGMF_UTILS_LIBRARIES
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

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-sigmf_utilsTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_SIGMF_UTILS DEFAULT_MSG GR_SIGMF_UTILS_LIBRARIES GR_SIGMF_UTILS_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_SIGMF_UTILS_LIBRARIES GR_SIGMF_UTILS_INCLUDE_DIRS)
