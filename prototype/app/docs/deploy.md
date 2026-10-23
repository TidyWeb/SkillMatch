# Deploying SkillMatch to Google Cloud Run

SkillMatch runs as a single container on Cloud Run. Each night a GitHub Actions workflow (`.github/workflows/refresh-and-deploy.yml`) does the following:

1. Rebuilds the vacancy database from the live sources.
2. Runs the tests.
3. Bakes the fresh SQLite file into a new image.
4. Deploys the image.

There is no database server and no user storage, and vacancy data is never committed to git. GitHub authenticates to Google with **Workload Identity Federation**, so no long-lived Google key is stored anywhere.

> Nothing here has been run yet. These are the one-time steps for whoever owns the Google Cloud project. They create billable resources (Cloud Run scales to zero, so an idle service costs close to nothing, but Artifact Registry storage and egress are charged).

## Before you start

- A Google Cloud project with billing enabled, and the `gcloud` CLI signed in as a project owner.
- The GitHub repository that holds this code. The team's convention is to stage it from `/home/Phil/C_C/Git/skillmatch-app`.
- A Reed Jobseeker API key.

Set these once in your terminal. Replace each `dummy…` value with your own.

```bash
PROJECT_ID="dummy1dummy1"            # your Google Cloud project id
GITHUB_REPO="dummy2dummy2/skillmatch" # owner/name of the GitHub repository
REGION="europe-west2"                 # London
POOL="github"
PROVIDER="skillmatch-repo"
SA_NAME="skillmatch-deployer"
SA="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
```

## 1. Turn on the services

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  iamcredentials.googleapis.com sts.googleapis.com --project "$PROJECT_ID"
```

## 2. Create the image repository

```bash
gcloud artifacts repositories create skillmatch \
  --repository-format=docker --location="$REGION" --project "$PROJECT_ID" \
  --description="SkillMatch images"
```

Optional: add a cleanup policy in the console so old nightly images are removed after, say, 14 days.

## 3. Create the deploying service account and its roles

```bash
gcloud iam service-accounts create "$SA_NAME" --project "$PROJECT_ID" \
  --display-name="SkillMatch GitHub deployer"

for ROLE in roles/run.admin roles/artifactregistry.writer roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA}" --role="$ROLE"
done
```

`iam.serviceAccountUser` lets the deployer run the service as Cloud Run's default runtime identity. The app itself needs no Google permissions.

## 4. Let GitHub Actions act as that service account (Workload Identity Federation)

```bash
gcloud iam workload-identity-pools create "$POOL" --project "$PROJECT_ID" \
  --location="global" --display-name="GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" --project "$PROJECT_ID" \
  --location="global" --workload-identity-pool="$POOL" \
  --display-name="SkillMatch repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='${GITHUB_REPO}'"

gcloud iam service-accounts add-iam-policy-binding "$SA" --project "$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/attribute.repository/${GITHUB_REPO}"

echo "GCP_WIF_PROVIDER=projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/providers/${PROVIDER}"
echo "GCP_SERVICE_ACCOUNT=${SA}"
```

The attribute condition means only workflows from this one repository can use the identity.

## 5. Add the GitHub settings

In the repository, open **Settings → Secrets and variables → Actions**.

| Kind | Name | Value |
|---|---|---|
| Variable | `GCP_PROJECT_ID` | your project id |
| Variable | `GCP_WIF_PROVIDER` | printed by step 4 |
| Variable | `GCP_SERVICE_ACCOUNT` | printed by step 4 |
| Secret | `REED_API_KEY` | your Reed key |
| Secret | `CVLIBRARY_FEED_URL` | leave unset until CV-Library sends it |

## 6. First deploy

Under **Actions**, open **refresh-and-deploy** and choose **Run workflow**. The run takes about 25–40 minutes, mostly Reed's one-request-a-second limit. After that it runs every night at 02:30 UTC. The service URL is printed at the end of the deploy step and shown in the Cloud Run console.

Cloud Run settings, as set in the workflow:

- region `europe-west2`;
- minimum instances 0, so the service scales to zero when idle;
- maximum instances 1;
- 512 MiB memory and 1 CPU;
- open to the public (`--allow-unauthenticated`).

## Checking a deploy

- `https://<service-url>/healthz` returns `{"mode": "live", "ok": true}`.
- The footer badge shows "Live snapshot · <date>".
- Each run's data-quality report is kept as a workflow artifact (`quality-report`) for 30 days.

## Running the container yourself

```bash
make docker-build   # builds the database first if it's missing (fixtures if there's no Reed key)
make docker-run     # serves on http://localhost:8080
```

On machines with Podman instead of Docker: `make docker-build DOCKER=podman` and `make docker-run DOCKER=podman`.

## Rolling back

Cloud Run keeps earlier revisions. In the console, open the service, then **Revisions**, then **Manage traffic**, and send 100% of traffic to an earlier revision. Or:

```bash
gcloud run services update-traffic skillmatch --region "$REGION" --project "$PROJECT_ID" \
  --to-revisions=dummy3dummy3=100    # the revision name from the console
```
