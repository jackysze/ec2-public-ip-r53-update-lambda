import boto3
import datetime
import json
import logging
import os


def defaultconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


logger = logging.getLogger()
logger.setLevel(logging.INFO)
instance_id = os.environ.get('EC2_INSTANCE_ID')
route53_hosted_zone_id = os.environ.get('ROUTE53_HOSTED_ZONE_ID')
route53_dns_record_name = os.environ.get('ROUTE53_DNS_RECORD_NAME')
route53_dns_record_ttl = os.environ.get('ROUTE53_DNS_RECORD_TTL')
route53_dns_record_type = os.environ.get('ROUTE53_DNS_RECORD_TYPE')
session = boto3.Session()


def update_route_53(event):
    event_detail = event.get('detail')
    event_instance_id = event_detail.get('instance-id')
    event_state = event_detail.get('state')
    logger.info('Received EC2 state change notification, instance {event_instance_id} transistion to {event_state} state.'.format(
        event_instance_id=event_instance_id, event_state=event_state))
    if event_instance_id == instance_id and event_state == 'running':
        ec2_client = session.client('ec2')
        # fetch EC2 public ip
        descriptions = ec2_client.describe_instances(
            InstanceIds=[event_instance_id])
        reservations = descriptions.get('Reservations')
        instances = reservations[0].get('Instances')
        public_ip_address = instances[0].get('PublicIpAddress')
        logger.info('Public IP address of instance {event_instance_id} is {public_ip_address}'.format(
            event_instance_id=event_instance_id, public_ip_address=public_ip_address))
        logger.info('Updating Route53 record {route53_dns_record_name}'.format(
            route53_dns_record_name=route53_dns_record_name))
        # update route53 record
        route53_client = session.client('route53')
        response = route53_client.change_resource_record_sets(
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': route53_dns_record_name,
                            'ResourceRecords': [
                                {
                                    'Value': public_ip_address,
                                },
                            ],
                            'TTL': int(route53_dns_record_ttl),
                            'Type': route53_dns_record_type
                        },
                    },
                ]
            },
            HostedZoneId=route53_hosted_zone_id,
        )
    return json.dumps(response, default=defaultconverter)


def lambda_handler(event, _):
    return update_route_53(event)
