import scrapy
from scrapy_splash import SplashRequest


class BBVASpider(scrapy.Spider):
    name = "bbva"

    def start_requests(self):
        self.user = getattr(self, "user", None)
        self.password = getattr(self, "password", None)
        urls = ['https://www.bbva.es/']

        # https://stackoverflow.com/questions/41989252/scrapy-splash-log-in
        login_script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(10))

            splash:set_viewport_full()

            local form = splash:select("#loginEmpleados")
            assert(form:fill({{ text_eai_user='{}', text_eai_password='{}' }}))
            assert(form:submit())

            assert(splash:wait(10))

            return {{
                html = splash:html(),
                png = splash:png(),
            }}
        end
        """.format(self.user, self.password)

        yield SplashRequest(
                urls[0],
                callback=self.parse_after_login,
                endpoint="execute",
                args={"lua_source": login_script,
                      "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"\
                              "(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"})

    def parse(self, response):
        pass

    def parse_after_login(self, response):
        print("Response after login %d" % response.status)
        print(response.body)
