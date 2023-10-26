#!/bin/bash -e
#
# set -x
#
# dates=$(cat SmartHouse.log | grep sensorTankTimeStamp | tail -2 | awk  {'print substr($2,2,19)'})
#
export LC_NUMERIC=nb_NO.UTF
# last time data logged from logfile
lastStamp=$(cat SmartHouse.log | grep 'Time is:' | tail -1 | awk  {'print substr($3,1,10)"T"substr($4,1,11)'})
# echo lastStamp = $lastStamp
lastStamps=$(date -d $lastStamp +"%s")
# echo lastStamps= $lastStamps
#
# time now
now=$(date -d now +"%Y-%m-%dT%H:%M:%S")
#echo now = $now
#
nows=$(date -d $now +"%s")
# echo nows= $nows
#
timeDiff=$(($nows - $lastStamps))
# echo timeDiff = $timeDiff
#
DeltaH=$(printf "%d\n" $(($timeDiff/3600)))
DeltaM=$(printf "%d\n" $((($timeDiff%3600)/60)))
DeltaS=$(printf "%d\n" $(($timeDiff%60)))
# printf '%02d:%02d:%02d\n' "$DeltaH" "$DeltaM" "$DeltaS"
#
if [ $DeltaH -gt 0 -o $DeltaM -gt 10 ]
then
    echo $(date +"%Y-%m-%d %T")
    echo -e "\tDelta time $DeltaH:$DeltaM:$DeltaS since last log."
    echo -e "\tRebooting!"
    sudo reboot
else
    echo -e "\tDelta time: $DeltaH:$DeltaM:$DeltaS since last log."
fi
