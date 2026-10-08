# Trailmark benchmark

## Deploy prompt

> Deploy this existing self-hosted activity-tracker repo using free resources only. Preserve its Django app, Postgres data, and background Celery processing. Provision Postgres and Redis, run migrations, deploy web and worker separately, configure secrets and HTTPS hosts/origins, and provide a public URL. Upload the supplied synthetic sample.gpx as a private run, wait for the worker, and verify its route, distance, elapsed pace, and original GPX download. Use a second sample account to verify privacy, then share the activity and add a kudos and comment. Stop and report any payment or card requirement.

## Acceptance

1. Upload GPX through the public app; a real separate worker processes it.
2. The supplied loop is approximately 6.46 km, with 2,160 elapsed seconds and about 40 m gain.
3. Route, stats, and original GPX remain after web/worker restart.
4. A second member cannot access the private activity, GPX, or social actions.
5. Sharing enables viewing/commenting/kudos; repeating kudos does not duplicate it. Making private restricts those operations again.

## Change prompt

> In this same deployed Trailmark app, add personal weekly distance goals by sport. Show progress from processed activities and let each user change their own goal. Add the database migration, deploy, and verify a goal update and progress at the existing URL. Preserve old GPX files, routes, comments, kudos, and activity visibility.

Passing evidence must include persistent per-user goals, correct sport-specific totals, access isolation, and old activities still downloadable.

## Recovery prompt

On the disposable benchmark stack, deliberately set only the worker's database password incorrectly, then upload the synthetic GPX.

> Uploaded activities are stuck processing or pending. Inspect deployment and worker context, identify why processing cannot complete, restore it, and process or retry the uploaded activity without losing its original GPX or any existing activities. Explain the verified cause.

The fault is intentional; record it as an injected recovery test, not as a spontaneous platform error.
