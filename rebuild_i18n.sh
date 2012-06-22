#! /bin/sh

I18NDOMAIN="plone"
BASE_DIRECTORY="plone/app/tiles"

# Synchronise the templates and scripts with the .pot.
i18ndude rebuild-pot --pot ${BASE_DIRECTORY}/locales/${I18NDOMAIN}.pot \
    --create ${I18NDOMAIN} \
    ${BASE_DIRECTORY}

# Synchronise the resulting .pot with all .po files
for po in ${BASE_DIRECTORY}/locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot ${BASE_DIRECTORY}/locales/${I18NDOMAIN}.pot $po
done

# Report of errors and suspect untranslated messages
i18ndude find-untranslated -n ${BASE_DIRECTORY}
