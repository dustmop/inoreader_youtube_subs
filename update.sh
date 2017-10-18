NOW=$(date +'%Y-%m-%d_%H-%m-%S')
FILENAME=$(printf "subscriptions_$NOW.xml")

echo "Downloading subscriptions from youtube..."
python3 download_youtube_rss.py $FILENAME || exit 1
echo "Done"
echo ""

echo "Importing opml into inoreader..."
python3 import_inoreader_opml.py $FILENAME || exit 1
echo "Done"
echo ""

python3 view_inoreader_subs.py || exit 1
