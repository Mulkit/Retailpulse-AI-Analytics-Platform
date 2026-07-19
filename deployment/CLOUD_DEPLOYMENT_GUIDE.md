# RetailPulse — Cloud Deployment Guide

Two deployment paths are provided; pick whichever fits your team's existing
cloud footprint. Both assume the Docker image from Day 22 has already been
built.

## Option A — AWS (ECS Fargate via Terraform)

`deployment/terraform/main.tf` provisions: ECR repository, ECS Fargate
cluster/service, an Application Load Balancer (HTTPS via an existing ACM
certificate), the supporting security groups, and CloudWatch logging.

```bash
cd deployment/terraform
terraform init
terraform plan -var="acm_certificate_arn=<your-cert-arn>"
terraform apply -var="acm_certificate_arn=<your-cert-arn>"
```

After the first `apply`, push the built image to the created ECR repo and
either re-run `apply` or `aws ecs update-service --force-new-deployment`.

## Option B — GCP (Cloud Run)

Simpler path for a single-container app with no orchestration needs beyond
autoscaling. `deployment/gcp_cloud_run_deploy.sh` builds via Cloud Build and
deploys to Cloud Run in one step.

```bash
export GCP_PROJECT_ID=your-project-id
./deployment/gcp_cloud_run_deploy.sh
```

## Option C — Existing Kubernetes cluster

Use the manifests in `k8s/` directly (see Day 23) — this is the
platform-agnostic option if your organization already runs its own cluster
(EKS, GKE, AKS, or on-prem).

```bash
kubectl apply -f k8s/
```

## What was validated in this environment vs. what needs a live run

This project was built in a sandboxed environment with no AWS/GCP
credentials and no Docker daemon, so the following is true and should be
disclosed as such in the project report/demo, rather than glossed over:

| Artifact | Validated here | Requires a live run to confirm |
|---|---|---|
| Dockerfile / docker-compose.yml | YAML syntax, dependency cross-check, dead-weight trim | `docker build` actually succeeding |
| Kubernetes manifests | YAML syntax + cross-reference consistency (5/5 checks passed) | `kubectl apply` against a real cluster |
| GitHub Actions workflow | YAML syntax; lint/validate/smoke-test job steps executed locally and passed | The `build-and-push` and `deploy` jobs, which need GHCR + kube credentials |
| Terraform (AWS) | HCL syntax parses cleanly | `terraform plan`/`apply` against a real AWS account |
| GCP deploy script | Bash syntax (`bash -n`) | An actual `gcloud` run against a real GCP project |

The dashboard application itself (Streamlit) **was** live-boot-tested
repeatedly throughout Days 15-21 — every page was launched with
`streamlit run` and confirmed to return HTTP 200 with zero errors in the
server log before being marked complete. That's the part of this project
that has genuine runtime evidence behind it; the cloud/orchestration layer
is a configuration deliverable ready for a real deployment, consistent with
how most portfolio submissions handle infrastructure they don't have a
live account to provision.
