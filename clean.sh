python manage.py clean_dict
python manage.py clean_contents
python manage.py validate_links
python manage.py compile_sentences

git add lauvinko/lang/sentences.txt

cd pages
sed -i s/lauvinko/Lauvìnko/gi *
cd ..
