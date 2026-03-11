%module(directors="1") cloudlogger

%{
#include "cloud_logger_bridge.hpp"
%}

%include <std_string.i>
%feature("director") cloudlogger::CloudLogger;

%include "cloud_logger_bridge.hpp"
