%module(directors="1") cloudlogger

%{
#include "cloud_logger_bridge.hpp"
#include "cloud_network_bridge.hpp"
%}

%include <std_string.i>
%feature("director") cloudlogger::CloudLogger;
%feature("director") cloudlogger::CloudNetwork;

%include "cloud_logger_bridge.hpp"
%include "cloud_network_bridge.hpp"
