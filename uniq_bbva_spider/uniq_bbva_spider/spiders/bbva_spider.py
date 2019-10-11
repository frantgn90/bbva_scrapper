import scrapy
import re
from scrapy_splash import SplashRequest


class BBVASpider(scrapy.Spider):
    name = "bbva"

    def start_requests(self):
        self.user = getattr(self, "user", None)
        self.password = getattr(self, "password", None)
        self.debug = getattr(self, "debug", "false") == "true"
        assert self.user is not None and self.password is not None

        urls = ['https://www.bbva.es/']

        cssselector = '#CUENTAS_ORDINARIAS_Y_DIVISA > div > table > tbody > tr > th > div > div > div > p.c-link.text_14.text-medium'

        login_script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(5))

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

            local account_link = splash:select('{}')
            print(account_link.info()["html"])
            account_link:click()

            assert(splash:wait(5))

            return {{
                html = splash:html(),
                png = splash:png(),
            }}
        end
        """.format(self.user, self.password, cssselector)

        yield SplashRequest(
                urls[0],
                callback=self.parse_account_page,
                endpoint="execute",
                args={"splash.private_mode_enabled": False, 
                      "lua_source": login_script,
                      "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"\
                            "(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"})

    def parse_account_page(self, response):
        for x in response.css("#_movimientosCollection-buscadorMovimientos_Ficha"
                              "> table > tbody > tr[role=row]"):
            day, month = x.css("div.contieneFechas b").re("<span .*>(.*)</span>(.*)</b>")[:2]
            concept = x.css("div.descripcionEspecifica b").re("<b .*>(.*)</b>")[0]
            payment = x.css("td.dato.numerico span").re("<span .*>(.*)</span>")[0]

            yield {"day": day.strip(), 
                   "month": month.strip(), 
                   "concept": concept.strip(),
                   "payment": payment.strip()}

        if self.debug:
            self._show_page(response)

    def _show_page(self, response):
        import base64
        if "data" in dir(response):  # If it is a SplashResponse
            with open("file.png", "w") as imgf:
                imgf.write(base64.b64decode(response.data['png']))
        with open("bbva.html", "w") as f:
            f.write(response.text.encode('utf-8').strip())
        scrapy.shell.inspect_response(response, self)
