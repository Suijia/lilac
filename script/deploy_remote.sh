#!/bin/bash

function usage() {
    echo "Usage: sh $0 env"  # 第零个参数就是脚本名称
    echo "env:"
    echo "    staging|online"
    exit 1
}

if [ $# -ne 1 ];then  # $#是参数个数
    usage
fi

ENV=$1  # 变量 ENV 的值为第一个参数

if [ ${ENV} != "staging" ] && [ ${ENV} != "online" ];then
    usage
fi  # if 完了不会再往下?

echo "start deploy "${ENV}

SERVICE=lilac
PACKAGE_NAME=${SERVICE}.tgz

SCRIPT_DIR=`dirname $0`  # 返回脚本目录, `命令`
cd ${SCRIPT_DIR}/..

DATE_TIME=`date +"%Y%m%d_%H%M%S"`

sh ${SCRIPT_DIR}/build.sh ${ENV}

if [ ! -f ${PACKAGE_NAME} ];then
    echo "${PACKAGE_NAME} not exist, build error"
    exit 1
fi

scp -r ${PACKAGE_NAME} root@120.27.111.29:/root/

ssh -t -p 22 root@120.27.111.29 "mv ${SERVICE} ${SERVICE}_${DATE_TIME}"
ssh -t -p 22 root@120.27.111.29 "tar -zxf ${SERVICE}.tgz"
ssh -t -p 22 root@120.27.111.29 "sh ${SERVICE}/script/control.sh stop"
ssh -t -p 22 root@120.27.111.29 "sh ${SERVICE}/script/control.sh start"
ssh -t -p 22 root@120.27.111.29 "tail -f ${SERVICE}/logs/*"
