# BBVA scrapper

## Dependencies

### Splash

In order to deal with the js embedded in the webpage that is generating dynamic data with asynch calls and with the js controlled forms I've decided to go with Splash as a middleware. It is a browser w/o GUI that is executing this js and serve to Scrapy the actual view the user has. Additionally with Splash it is possible to (throw its LUA API) perform actions like a normal human user.

The installation is easy. It is dockerized.
- `sudo docker pull scrapinghub/splash`

And you can run it with
- `sudo docker run -p 8050:8050 scrapinghub/splash`

Additionally it needs to have the Scrapy plugin installed
- `sudo pip install scrapy-splash`
