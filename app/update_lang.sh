xgettext -d base -o locales/base.pot weather.py
for lang in ca es en
do
	msgmerge --update locales/"${lang}"/LC_MESSAGES/base.po locales/base.pot
	msgfmt -o locales/"${lang}"/LC_MESSAGES/base.mo locales/"${lang}"/LC_MESSAGES/base
done
