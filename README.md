# inoreader_youtube_subs

A script to download subscriptions from Youtube, import them into Inoreader, then display untagged channels.

# Getting started

* Create a new Inoreader application.
* The redirect URI must be "http://localhost:8000/". TODO: More directions.
* Copy the AppId and AppKey and put their contents into the files `app/client_id.dat` and `app/client_secret.dat`.
* Copy your Inoreader cookie and put it into `user/inoreader.cookie`.
* Copy your Youtube cookie and put it into `user/youtube.cookie`.

# Running

```
./update.sh
```
