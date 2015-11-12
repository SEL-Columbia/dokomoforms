#!/bin/bash
# Thanks to http://www.lexev.org/en/2015/tornado-internationalization-and-localization/

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <locale>"
    exit 1
fi
locale=$1
domain="dokomoforms"
locale_dir="locale/${locale}/LC_MESSAGES"
po_file="${locale_dir}/${domain}.po"
mo_file="${locale_dir}/${domain}.mo"
# create .mo file from .po
msgfmt ${po_file} --output-file=${mo_file}
echo "Created ${mo_file}."
