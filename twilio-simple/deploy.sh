#!/bin/bash
#
# SAM Deploy Script
#
# Simple deploy script that uses standard flags to deploy to AWS
# using the Server Application Model standard.
#
# EXAMPLE:
#   ./deploy.sh -s StorageAuditApp -b lambdawhatever425 -o output.yaml
#

usage()
{
    echo ""
    echo "${green}USAGE:${reset}"
    echo "  ./deploy.sh ${yellow}-s${reset} STACK_NAME ${yellow}-b${reset} S3_BUCKET ${yellow}-o${reset} OUTPUT"
    echo " "
    echo "${green}OPTIONS:${reset}"
    echo "  ${yellow}-s${reset} Choose a stackname for CloudFormation"
    echo "  ${yellow}-b${reset} s3 bucket name where code will be uploaded"
    echo "  ${yellow}-o${reset} output compiled SAM file, default: output.yaml"
    echo "${reset}"
}

#
# set terminal colors
#
red=`tput setaf 1`
green=`tput setaf 2`
yellow=`tput setaf 3`
blue=`tput setaf 6`
reset=`tput sgr0`

#
# Check flags are set
#
if [[ $1 == "" ]]; then
    usage
    exit
fi

#
# Parse options
#
while getopts 's:b:o:' flag; do
  case $flag in
    s) STACK_NAME=${OPTARG} ;;
    b) S3_BUCKET=${OPTARG} ;;
    o) SAM_OUTPUT=${OPTARG} ;;
    *)
      usage
      exit
      ;;
  esac
done

#
# Check STACK_NAME is set
#
if [ -z "${STACK_NAME}" ]; then
    echo ""
    echo "${red}==> ERROR:${reset}"
    echo "    STACK_NAME needs to be set before deploying"
    usage
    exit
fi

#
# Check S3_BUCKET is set
#
if [ -z "${S3_BUCKET}" ]; then
    echo ""
    echo "${red}==> ERROR:${reset}"
    echo "    S3_BUCKET needs to be set before deploying"
    usage
    exit
fi

#
# Set Default SAM File
#
SAM_FILE='index.yaml'

#
# Package & Deploy
#
echo "${green}==> PACKAGING${reset}"

aws cloudformation package \
   --template-file $SAM_FILE \
   --output-template-file $SAM_OUTPUT \
   --s3-bucket $S3_BUCKET

echo "${green}==> DEPLOYING${reset}"

aws cloudformation deploy \
  --template-file $SAM_OUTPUT \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM

echo "${green}==> COMPLETE${reset}"
