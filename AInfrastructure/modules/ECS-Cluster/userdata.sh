#!/bin/bash
set -e

# ── 1. Register EC2 instance to ECS cluster ──────────────────
echo ECS_CLUSTER=${cluster_name} >> /etc/ecs/ecs.config
echo ECS_ENABLE_TASK_IAM_ROLE=true >> /etc/ecs/ecs.config
echo ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true >> /etc/ecs/ecs.config

# ── 2. Install SSM Agent ──────────────────────────────────────
# SSM agent allows connecting to EC2 without SSH key pair
# Required for: debugging, running commands, viewing logs
yum install -y amazon-ssm-agent

# ── 3. Enable and start SSM agent ────────────────────────────
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# ── 4. Verify SSM agent is running ───────────────────────────
systemctl status amazon-ssm-agent >> /var/log/ssm-install.log 2>&1

# ── 5. Signal that userdata completed successfully ────────────
echo "Userdata completed successfully" >> /var/log/userdata.log
