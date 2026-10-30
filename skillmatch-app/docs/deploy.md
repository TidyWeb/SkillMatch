# Deploying SkillMatch to Google Cloud Run

The repository root workflow `.github/workflows/daily-collect.yml` collects vacancies, builds the image on GitHub's runner and deploys it to Cloud Run. The image is pushed to `europe-west2-docker.pkg.dev/dummy-project-id/skillmatch/skillmatch`. The workflow does not use Cloud Build.

## 1. Schedule and deploy gate

The `deploy` job runs only when the repository variable `DEPLOY_ENABLED` is `true`.

- The main collection runs daily at 06:23 Europe/London.
- A backup run starts at 12:23 Europe/London. It skips collection if a successful run was created today (UTC).
- **Run workflow** starts collection every time, including when an earlier run succeeded.

The deploy job uses the `reed` environment. The Reed API key is available to collection through that environment.

## 2. One-time Google Cloud setup

The project has billing enabled. Replace the example values below with your project ID and number when checking or recreating the setup.

1. Enable these APIs: Cloud Run, Artifact Registry, IAM Credentials, Security Token Service, IAM, and Cloud Resource Manager (`run.googleapis.com`, `artifactregistry.googleapis.com`, `iamcredentials.googleapis.com`, `sts.googleapis.com`, `iam.googleapis.com`, `cloudresourcemanager.googleapis.com`).
2. Create the Docker repository `skillmatch` in `europe-west2`. Its cleanup rules keep the latest two images and delete the rest.
3. Create two service accounts:
   - `skillmatch-deployer` has `roles/run.admin` on the project, `roles/artifactregistry.writer` on the `skillmatch` repository only, and `roles/iam.serviceAccountUser` on `skillmatch-runtime` only.
   - `skillmatch-runtime` has no IAM roles. Cloud Run runs the app as this account.
4. Create the Workload Identity pool `github` and OIDC provider `skillmatch-repo`. Map `google.subject=assertion.sub`, `attribute.repository=assertion.repository`, `attribute.ref=assertion.ref`, and `attribute.environment=assertion.environment`. The provider condition is `assertion.repository == 'TidyWeb/SkillMatch' && assertion.ref == 'refs/heads/main' && assertion.environment == 'reed'`.
5. Grant `roles/iam.workloadIdentityUser` on `skillmatch-deployer` to `principalSet://iam.googleapis.com/projects/000000000000/locations/global/workloadIdentityPools/github/attribute.repository/TidyWeb/SkillMatch`. This lets the approved GitHub workflow act as the deployer without a stored Google key.

The setup uses the project number and ID only in these resource names. Example placeholders:

```bash
PROJECT_ID="dummy-project-id"
PROJECT_NUMBER="000000000000"
REGION="europe-west2"
GITHUB_REPO="TidyWeb/SkillMatch"
POOL="github"
PROVIDER="skillmatch-repo"
DEPLOYER="skillmatch-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME="skillmatch-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
```

Run these commands in a shell with `gcloud` configured for the project:

1. Enable the APIs:

   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com iamcredentials.googleapis.com sts.googleapis.com iam.googleapis.com cloudresourcemanager.googleapis.com --project "$PROJECT_ID"
   ```

2. Create the image repository and its cleanup policies:

   ```bash
   gcloud artifacts repositories create skillmatch --repository-format=docker --location="$REGION" --project "$PROJECT_ID" --description="SkillMatch app images"
   ```

   Save the following as `cleanup.json`:

   ```json
   [
     {
       "name": "keep-latest-2",
       "action": {"type": "Keep"},
       "mostRecentVersions": {"keepCount": 2}
     },
     {
       "name": "delete-rest",
       "action": {"type": "Delete"},
       "condition": {"tagState": "ANY"}
     }
   ]
   ```

   Apply the policies:

   ```bash
   gcloud artifacts repositories set-cleanup-policies skillmatch --location="$REGION" --project "$PROJECT_ID" --policy=cleanup.json --no-dry-run
   ```

3. Create the two service accounts:

   ```bash
   gcloud iam service-accounts create skillmatch-deployer --project "$PROJECT_ID" --display-name="SkillMatch GitHub deployer"
   gcloud iam service-accounts create skillmatch-runtime --project "$PROJECT_ID" --display-name="SkillMatch app runtime (no permissions)"
   ```

4. Grant the deployer only its required roles:

   ```bash
   gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${DEPLOYER}" --role="roles/run.admin" --condition=None
   gcloud artifacts repositories add-iam-policy-binding skillmatch --location="$REGION" --project "$PROJECT_ID" --member="serviceAccount:${DEPLOYER}" --role="roles/artifactregistry.writer"
   gcloud iam service-accounts add-iam-policy-binding "$RUNTIME" --project "$PROJECT_ID" --member="serviceAccount:${DEPLOYER}" --role="roles/iam.serviceAccountUser"
   ```

   The runtime account receives no roles.

5. Create the Workload Identity pool and provider:

   ```bash
   gcloud iam workload-identity-pools create "$POOL" --project "$PROJECT_ID" --location="global" --display-name="GitHub Actions"

   gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
     --project "$PROJECT_ID" --location="global" --workload-identity-pool="$POOL" \
     --display-name="SkillMatch repository" \
     --issuer-uri="https://token.actions.githubusercontent.com" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref,attribute.environment=assertion.environment" \
     --attribute-condition="assertion.repository=='${GITHUB_REPO}' && assertion.ref=='refs/heads/main' && assertion.environment=='reed'"
   ```

6. Allow that provider to act as the deployer:

   ```bash
   gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER" --project "$PROJECT_ID" \
     --role="roles/iam.workloadIdentityUser" \
     --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/attribute.repository/${GITHUB_REPO}"
   ```

## 3. GitHub settings

Add these repository **variables** under **Settings → Secrets and variables → Actions**:

| Variable | Value |
|---|---|
| `GCP_PROJECT_ID` | Google Cloud project ID |
| `GCP_WIF_PROVIDER` | Full Workload Identity provider resource name |
| `GCP_SERVICE_ACCOUNT` | `skillmatch-deployer` service account email |
| `DEPLOY_ENABLED` | `true` to allow the deploy job to run |

Add `REED_API_KEY` as a **secret** in the `reed` environment. Keep it out of repository secrets. Restrict that environment to the `main` branch. The workflow's identity condition also requires `main` and the `reed` environment.

The publication staging clone is `/home/Phil/C_C/Git/SkillMatch`.

## 4. Cost controls

- Cloud Run has minimum instances 0 and maximum instances 1.
- A £2/month Cloud Run spend cap is configured for this project.
- A £2/month billing budget alert covers all projects and services, with alerts at 50%, 75% and 95%.
- Artifact Registry deletes images beyond the latest two.
- There is no load balancer and no Cloud Build setup.

## Checking a deploy

- Open the `daily-collect.yml` run under **Actions** and check the `deploy` job.
- The service health endpoint is `https://<service-url>/health`; it should return `{"mode":"live","ok":true}` (on Cloud Run use `/health`; `/healthz` is reserved by Google).
- The footer badge shows the live snapshot date.

## Running the container yourself

From `skillmatch-app` in the repository:

```bash
make docker-build   # builds the database first if it's missing (fixtures if there's no Reed key)
make docker-run     # serves on http://localhost:8080
```

On machines with Podman instead of Docker: `make docker-build DOCKER=podman` and `make docker-run DOCKER=podman`.

## Rolling back

Cloud Run keeps earlier revisions. In the console, open the service, then **Revisions**, then **Manage traffic**, and send 100% of traffic to an earlier revision. Or:

```bash
gcloud run services update-traffic skillmatch --region "$REGION" --project "$PROJECT_ID" \
  --to-revisions=dummy-revision-name=100    # use the revision name from the console
```
