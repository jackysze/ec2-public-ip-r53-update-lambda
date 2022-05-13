# AWS EC2 public ip address Route53 DNS record update lambda

EC2 without elastic ip assignment will change it's public ip address during instance start stop cycle. This lambda works with EventBridge's EC2 state change event and update Route53 DNS record up on the instance is changed to `running` state.