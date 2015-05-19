#!/bin/bash
# Thanks to http://www.lexev.org/en/2015/tornado-internationalization-and-localization/

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <locale>"
    exit 1
fi
locale=$1
domain="dokomoforms"
locale_dir="locale/${locale}/LC_MESSAGES"
po_template_file="locale/${domain}.po"
po_file="${locale_dir}/${domain}.po"
# create folder if it does not exist
mkdir -p $locale_dir
# create .po template file
find dokomoforms/ -iname "*.html" -o -iname "*.py" | xargs \
    xgettext --language=Python -d ${domain} -p locale/ --from-code=UTF-8 \
    --sort-by-file --keyword=_:1,2 --no-wrap
    # by default xgettext leaves charset=CHARSET. change it to UTF-8
    sed -i 's/"Content-Type: text\/plain; charset=CHARSET\\n"/"Content-Type: text\/plain; charset=UTF-8\\n"/g' ${po_template_file}
# init .po file, if it doesn't exist yet
if [ ! -f $po_file ]; then
    msginit --input=${po_template_file} --output-file=${po_file} --no-wrap --locale=${locale}
else
    # update .po file
    msgmerge --no-wrap --sort-by-file --output-file=${po_file} ${po_file} ${po_template_file}
fi
