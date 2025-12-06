# Deployment Checklist

Before cutting over to production:

- [ ] **Build**: Docker image built and pushed to ECR with Git SHA tag.
- [ ] **Secrets**: Production secrets (API keys, DB creds) updated in AWS Secrets Manager.
- [ ] **Task Def**: Task Definition updated with new Image URI and Secret ARNs.
- [ ] **Terraform**: Infrastructure (ALB, ECS Cluster, DB) applied and green.
- [ ] **Deploy**: ECS Service updated to new Task Definition.
- [ ] **Health**: ALB Target Group shows healthy hosts.
- [ ] **Smoke Test**: Run `infra/scripts/smoke_test.sh` against ALB DNS.
- [ ] **Monitoring**: Check Grafana/CloudWatch for error rates and latency.
- [ ] **Logs**: Verify logs are flowing to CloudWatch.
- [ ] **Scale**: Verify autoscaling triggers (simulate load if needed).
