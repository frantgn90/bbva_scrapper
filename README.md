# BBVA scrapper

This scraper get the last movements on your BBVA account.

## Run the scraper

In order tu run the scraper you should 1) Run the Splash service by executing 
- `sudo docker run -p 8050:8050 scrapinghub/splash --disable-private-mode --max-timeout 3600`

And then 2) just execute the scraper as it used to be with scrapy
- `scrapy crawl bbva -a user=<user> -a password=<password> -o results.jl`

This scraper accepts few parameters:
- `user` is your BBVA user (required)
- `password` is the password for your user (required)
- `debug` just save the html and a png of the webpage that has been scraped. It allows the `true|false` values. `false` by default

## Dependencies

### Splash

In order to deal with the js embedded in the webpage that is generating dynamic data with asynch calls and with the js controlled forms I've decided to go with Splash as a middleware. It is a browser w/o GUI that is executing this js and serve to Scrapy the actual view the user has. Additionally with Splash it is possible to (throw its LUA API) perform actions like a normal human user.

The installation is easy. It is dockerized.
- `sudo docker pull scrapinghub/splash`

Additionally it needs to have the Scrapy plugin installed
- `sudo pip install scrapy-splash`
