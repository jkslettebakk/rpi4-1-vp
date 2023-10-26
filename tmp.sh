#!/bin/sh -e
#
# set -x
#
string_var=$(ps -ef | grep \.py$ | awk '/.py/ { print $9 }')
number_py=$(echo $string_var | tr ' ' '\n' | grep -c '.py')
log_file="/home/pi/Documents/check_jobs.log"
log_file_write=false
#
# In crontab no input is expected
#
# Manual imput expect
#   Parameter $1 = log_file_write = false or true
#   Parameter $2 = simulate number_py scrips running (any number)
if [ $# -ge 1 ] ;
then
  echo "Manual start with input to $0. Parameter(s) is: $@"
  test "$1" != "" && log_file_write=$1; #Setting log status dynamically 
  test "$2" != "" && number_py=$2; # testing number_py logic 
fi
#
# Write log time to file
test $log_file_write = true && echo $(date +"%Y-%m-%d %T") >> $log_file
#
if [ $number_py -ge 1 ] ;
then
  # Some python scripts is running
  i=1;
  # Write number of .py files running to log file
  test $log_file_write = true && echo "\tPython files found. Looping from $i to $number_py file(s)" >> $log_file
  # echo "\tPython files found. Looping from $i to $number_py file(s)"
  while [ $i -le $number_py ]
  do
    # write file names (.py files) to log file
    test $log_file_write = true && echo $string_var | awk '/.py/ { print "\t", $'$i' }' >> $log_file
    # echo $string_var | awk '/.py/ { print "\t", $'$i' }'
    i=$(($i+1))
  done
else
  if [ $number_py -eq 0 ];
  then
    test $log_file_write = false && echo $(date +"%Y-%m-%d %T") >> $log_file
    echo "\tNo ($number_py) expected python scripts is running. Will reboot!" >> $log_file;
    $(sudo reboot);
  else
    # unknown number of python scrips is running
    echo "\tStrange results or input parameter '$string_var',\n\t number of files is $number_py" >> $log_file;
  fi
fi
