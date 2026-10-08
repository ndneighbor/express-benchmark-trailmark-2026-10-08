# Trailmark

A self-hosted activity journal inspired by Strava. Accounts upload timestamped GPX tracks; a Celery worker computes distance, elapsed pace, elevation gain, and route geometry. The feed includes the user's own activities and public activities from other members. Members can give one kudos per activity, comment, and download original GPX files when allowed by activity visibility.

Activities are private by default. Sharing reveals the full route and original file to other signed-in members. Making an activity private immediately restricts its page, comments, kudos actions, and download. Only its owner can delete it or change visibility.

**Services:** Django/Gunicorn/WhiteNoise web, Celery worker, Postgres, Redis. Both original GPX bytes and processed routes live in Postgres. There is no shared filesystem or map-provider API key. GPX input is limited to 2 MB and 50,000 track points, validates coordinates/timestamps, and rejects XML entities.

## Local run

```sh
python3 configure.py
docker compose up -d --build
DEMO_PASSWORD='choose-a-local-demo-password' docker compose exec -e DEMO_PASSWORD web python manage.py seed_demo
```

Open http://localhost:8102. Sample accounts: `demo` and `jules`, with the password you supplied. `sample.gpx` is a synthetic park loop for uploading another activity. The seeder also generates synthetic activities without depending on a running worker.

```sh
docker compose exec -e TASKS_EAGER=1 web python manage.py test
docker compose exec web python verify_worker.py
```

The second command checks a real worker and creates a synthetic verification activity. `/healthz` executes a database query.

## Cloud deployment

Deploy this directory as web using its Dockerfile, plus a second service with the same image/source and command `celery -A config worker --loglevel=info --concurrency=2`. Add Postgres and persistent Redis. Run `python manage.py migrate --noinput` as a web pre-deploy command.

On both services set a unique `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `DEBUG=0`, `TASKS_EAGER=0`. On web set `HTTPS=1`, exact `ALLOWED_HOSTS`, and HTTPS `CSRF_TRUSTED_ORIGINS`. The listener uses `PORT` (default 8000). `/healthz` is exempt from SSL redirects for internal HTTP health probes.

`railway.json` is the web config; use `worker.railway.json` for the worker's config file. Set this directory as the root when importing from a larger repo. Cloud deployment of these configs is still unmeasured.

## Scope of the activity metrics

Distance uses haversine distances between consecutive points within each GPX track segment. Duration is elapsed timestamp time within segments, not moving time. Elevation gain sums positive GPX elevation changes without GPS-noise smoothing. The display is an equirectangular route outline on a grid, not a street map. The app does not provide live GPS recording, map tiles, segments, clubs, or wearable integrations. These limits are visible in the activity page and should not be represented as full Strava feature parity.

See `BENCHMARK.md` for deployment and maintenance tasks.
