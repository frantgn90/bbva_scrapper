import scrapy
import re
from scrapy_splash import SplashRequest


class BBVASpider(scrapy.Spider):
    name = "bbva"

    def start_requests(self):
        self.user = getattr(self, "user", None)
        self.password = getattr(self, "password", None)
        self.debug = getattr(self, "debug", "false") == "true"
        urls = ['https://www.bbva.es/']

        login_script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(10))

            splash:set_viewport_full()

            local button_show = splash:select("#client-access-controller")
            assert(button_show:info()["visible"])
            button_show:click()

            assert(splash:wait(0))   -- Needed to have the click event processed

            local form = splash:select("#loginEmpleados")
            -- Just to be sure the button has been clicked
            assert(form:info()["visible"])

            splash:send_text("{}")    -- Entering username
            splash:send_keys("<Tab>")
            splash:send_text("{}")    -- Entering password
            splash:send_keys("<Return>")
            assert(splash:wait(15))

            return {{
                html = splash:html(),
                png = splash:png(),
            }}
        end
        """.format(self.user, self.password)

        yield SplashRequest(
                urls[0],
                callback=self.parse,
                endpoint="execute",
                args={"splash.private_mode_enabled": False, 
                      "lua_source": login_script,
                      "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"\
                            "(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"})

    def parse(self, response):
        css_selector = "#CUENTAS_ORDINARIAS_Y_DIVISA > div > table > tbody > "\
            "tr > th > div > div > div > p.c-link.text_14.text-medium"
        cuentas = [(item.get(), item.attrib["data-link"]) 
                   for item in response.css(css_selector)]

        ncuenta_pattern = re.compile("^<p .*>(.*)</p>$")
        for cuenta in cuentas:
            ncuenta = ncuenta_pattern.search(cuenta[0]).groups()[0]
            cuenta_enlace_rel = cuenta[1]

            self.logger.info("Cuenta {} enlace {}".format(ncuenta, cuenta_enlace_rel))
            yield response.follow(cuenta_enlace_rel, 
                                  self.parse_account_page, 
                                  cb_kwargs={"account": ncuenta})

    def parse_account_page(self, response, account):
        self.logger.info("Parsing last movements of account {}".format(account))
        if self.debug:
            self._show_page(response)

    def _show_page(self, response):
        import base64
        if "data" in dir(response):  # If it is a SplashResponse
            with open("file.png", "w") as imgf:
                imgf.write(base64.b64decode(response.data['png']))
        with open("bbva.html", "w") as f:
            f.write(response.text.encode('utf-8').strip())
