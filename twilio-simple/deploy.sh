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
    echo "  ./deploy.sh ${yellow}-s${reset} STACK_NAME ${yellow}-b${reset} S3_BUCKET ${yellow}-o${reset} OUTPUT ${yellow}-a${reset} TWILIO_AUTH ${yellow}-t${reset} TWILIO_SID"
    echo " "
    echo "${green}OPTIONS:${reset}"
    echo "  ${yellow}-s${reset} Choose a stackname for CloudFormation"
    echo "  ${yellow}-b${reset} s3 bucket name where code will be uploaded"
    echo "  ${yellow}-o${reset} output compiled SAM file, default: output.yaml"
    echo "  ${yellow}-t${reset} set twilio sid"
    echo "  ${yellow}-a${reset} set twilio auth token"
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
while getopts 's:b:o:t:a:' flag; do
  case $flag in
    s) STACK_NAME=${OPTARG} ;;
    b) S3_BUCKET=${OPTARG} ;;
    o) SAM_OUTPUT=${OPTARG} ;;
    t) TWILIO_SID=${OPTARG} ;;
    a) TWILIO_AUTH=${OPTARG} ;;
    *)
      usage
      exit
      ;;
  esac
done

if [[ -z $STACK_NAME || -z $S3_BUCKET || -z $TWILIO_SID || -z $TWILIO_AUTH ]]; then 
    echo ""
    echo "${red}==> ERROR:${reset}"
    echo "    Correct flags are not set on command"
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
  --capabilities CAPABILITY_IAM \
  --parameter-overrides TwilioSid=$TWILIO_SID TwilioToken=$TWILIO_AUTH

echo "${green}==> COMPLETE${reset}"
