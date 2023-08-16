# Install script for directory: /home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "0")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64" TYPE STATIC_LIBRARY FILES "/home/fmeneghetti/Projects/elettra/opt/poppler/build/qt5/src/libpoppler-qt5.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/poppler/qt5" TYPE FILE FILES
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-qt5.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-link.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-annotation.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-form.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-optcontent.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-page-transition.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/qt5/src/poppler-media.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/build/qt5/src/poppler-export.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/build/qt5/src/poppler-version.h"
    )
endif()

