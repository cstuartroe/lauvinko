python manage.py clean_dict
python manage.py clean_contents
python manage.py validate_links
python manage.py compile_sentences

cd pages
sed -i s/lauvinko/Lauvìnko/gi *
cd ..
