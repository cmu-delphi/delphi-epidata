#!/usr/bin/env sh
set -e

# If a New Relic license key is found then we start with custom New Relic
# commands, otherwise we start via start.sh.
if [ -z "${NEW_RELIC_LICENSE_KEY}" ]; then
  sh /start.sh
else
  newrelic-admin run-command /start.sh
fi
