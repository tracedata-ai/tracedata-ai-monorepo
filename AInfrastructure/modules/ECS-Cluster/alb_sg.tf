# ---------------------------------------------------------------------------
# ALB SG — egress
#
# The ALB SG already has an inline egress rule (all protocols to VPC CIDR)
# declared in modules/ALB/main.tf.  That rule covers ALB → backend traffic
# on all dynamic ports because the backend instances are inside the VPC.
#
# A separate aws_security_group_rule targeting the backend SG would conflict
# with the ALB module's inline egress set and gets removed on every apply.
# ---------------------------------------------------------------------------
