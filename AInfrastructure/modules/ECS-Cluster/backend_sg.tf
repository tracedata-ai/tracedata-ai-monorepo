# ---------------------------------------------------------------------------
# Backend SG — ALB ingress rule
#
# The allow-all-TCP ingress rule from the ALB SG is now managed as an inline
# rule inside aws_security_group.backend_sg in modules/API-Gateway/main.tf.
#
# Keeping a separate aws_security_group_rule here would conflict with that
# inline definition: Terraform enforces the inline set and removes any rules
# added outside the resource block on every apply.
# ---------------------------------------------------------------------------
