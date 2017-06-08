from aiohttp import web
import asyncio
import aiohttp_jinja2
import jinja2
import os
import sys
sys.path.append("".join(x + '/' for x in
                (os.path.abspath(__file__).split('/')[:-2])))
from linux_daemons import views


def main():
    host = "127.0.0.1"
    port = 8080
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/', views.index)
    app.router.add_post('/change_daemon', views.change_daemon)
    app.router.add_post('/save_checkbox', views.save_checkbox)
    static_folder = "".join(x + '/' for x in
                            (os.path.abspath(__file__).split('/')[:-1]))
    static_folder += "static/"
    app.router.add_static("/static/",
                          path=static_folder,
                          name='static')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    web.run_app(app, host=host, port=port)

if __name__ == "__main__":
    main()

