# -*- coding: utf-8 -*-

import boto3
import os
import logging
import sys


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 変数定義
TAGNAME = os.environ['ACTION_TAG']
REGION = os.environ['REGION']
TARGETGROUP_ARN = os.environ['TARGETGROUP_ARN']

def lambda_handler(event, context):
    logger.info("start function: %s " % sys._getframe().f_code.co_name)

    try:
        return_values = {}
        ec2 = boto3.client('ec2', region_name = REGION)
        alb = boto3.client('elbv2', region_name = REGION)
        INSTANCE_ID = event['instance_id']
        response = ec2.describe_instances(InstanceIds = [INSTANCE_ID])
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        
        for tag in tags:
            if TAGNAME in tag['Key']:
                action_flg = tag['Value']

        if action_flg == "enabled":
            # TGに登録されていること確認
            health = alb.describe_target_health(
                TargetGroupArn = TARGETGROUP_ARN,
                Targets = [
                    {
                        'Id': INSTANCE_ID,
                        'Port': 80,
                    },
                ]
            )
            
            # TGから外す
            if health['TargetHealthDescriptions'][0]['TargetHealth']['State'] == 'healthy':
                alb.deregister_targets(
                    TargetGroupArn = TARGETGROUP_ARN,
                    Targets = [
                        {
                            'Id': INSTANCE_ID,
                            'Port': 80,
                        },
                    ]
                )
                logger.info("%s is healthy. now deregistering." % INSTANCE_ID)
                # 切離し済み確認
                waiter_alb = alb.get_waiter('target_deregistered')
                waiter_alb.wait(
                    TargetGroupArn = TARGETGROUP_ARN,
                    Targets = [
                        {
                            'Id': INSTANCE_ID,
                            'Port': 80,
                        },
                    ],
                )
                logger.info("%s is just deregistered." % INSTANCE_ID)
            else:
                logger.info("%s was not deregistered. Already unhealthy." % INSTANCE_ID)
        else:
            logger.info("%s is not deregister-target." % INSTANCE_ID)

    except Exception as e:
        logger.error("occured %s" % e)
        return_values['error_desc'] = str(e)
        return return_values
