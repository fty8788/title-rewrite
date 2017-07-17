#!/bin/bash
# @author zhang,xiang
# @date 2012/11/21

baseDir=$(cd "$(dirname "$0")"; pwd)

logMsg(){
    echo -e `date +"%Y/%m/%d %H:%M:%S "` "$1"
}

build(){ 
    if [ -d "$baseDir/output" ]; then
        rm -rf $baseDir/output 
    fi
    mkdir -p ./output
    logMsg "Generating output..."
    cp -r bin/* output
    if [ $? -eq 0 ]; then
        logMsg "Build success."
    else
        logMsg "Build fail."
    fi
}

build
