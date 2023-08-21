# Install script for directory: /home/fmeneghetti/Projects/elettra/opt/poppler/glib

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64" TYPE STATIC_LIBRARY FILES "/home/fmeneghetti/Projects/elettra/opt/poppler/build/glib/libpoppler-glib.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/poppler/glib" TYPE FILE FILES
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-action.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-date.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-document.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-page.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-attachment.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-form-field.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-annot.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-layer.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-movie.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-media.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/glib/poppler-structure-element.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/build/glib/poppler-enums.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/build/glib/poppler-features.h"
    "/home/fmeneghetti/Projects/elettra/opt/poppler/build/glib/poppler-macros.h"
    )
endif()

