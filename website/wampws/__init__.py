###############################################################################
##
##  Copyright (C) Crossbar.io Technologies GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

## make sure we serve the right MIME type for SVG!
##
import mimetypes
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('text/javascript', '.jgz')

import uuid

from optparse import OptionParser

from flask import Flask, Request, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.before_request
def before_request():
   session["debug"] = app.debug
   session["widgeturl"] = app.widgeturl
   session["cstatic"] = app.cstatic

@app.after_request
def after_request(response):
   return response


@app.route('/')
@app.route('/index.html')
def page_home():
   session['tab_selected'] = 'home'
   return render_template('page_t_home.html')

@app.route('/impressum/')
@app.route('/impressum/index.html')
def page_impressum():
   session['tab_selected'] = 'impressum'
   return render_template('page_t_impressum.html')

@app.route('/why/')
@app.route('/why/index.html')
def page_why():
   session['tab_selected'] = 'why'
   return render_template('page_t_why.html', disqus = True)

@app.route('/compared/')
@app.route('/compared/index.html')
def page_compared():
   session['tab_selected'] = 'compared'
   return render_template('page_t_compared.html', disqus = True)

@app.route('/faq/')
@app.route('/faq/index.html')
def page_faq():
   session['tab_selected'] = 'faq'
   return render_template('page_t_faq.html', disqus = True)

@app.route('/implementations/')
@app.route('/implementations/index.html')
def page_implementations():
   session['tab_selected'] = 'implementations'
   return render_template('page_t_implementations.html', disqus = True)

@app.route('/spec/')
@app.route('/spec/index.html')
def page_spec():
   session['tab_selected'] = 'spec'
   return render_template('page_t_spec.html')


if __name__ == "__main__":

   parser = OptionParser()

   parser.add_option ("-d",
                      "--debug",
                      dest = "debug",
                      action = "store_true",
                      default = False,
                      help = "Enable debug mode for Flask")

   parser.add_option ("-f",
                      "--freeze",
                      dest = "freeze",
                      action = "store_true",
                      default = False,
                      help = "Freeze website using Frozen-Flask")

   parser.add_option ("-s",
                      "--socketserver",
                      dest = "socketserver",
                      action = "store_true",
                      default = False,
                      help = "Run Flask web app under standard Python SocketServer, instead of under Twisted")

   parser.add_option ("-p",
                      "--port",
                      dest = "port",
                      default = 8080,
                      help = "Listening port for Web server (i.e. 8090).")

   parser.add_option ("-w",
                      "--widgeturl",
                      dest = "widgeturl",
                      default = "https://demo.crossbar.io/clandeckwidget",
                      help = "WebClan widget base URL.")

   parser.add_option ("--cstatic",
                      dest = "cstatic",
                      default = "//tavendo-common-static.s3-eu-west-1.amazonaws.com",
                      help = "Tavendo shared static assets base URL")

   (options, args) = parser.parse_args ()

   app.widgeturl = options.widgeturl
   app.cstatic = options.cstatic

   if options.freeze:

      from flask_frozen import Freezer
      freezer = Freezer(app)
      freezer.freeze()

      if options.debug:
         import sys, os
         from twisted.python import log
         log.startLogging(sys.stdout)

         from twisted.internet import reactor
         from twisted.web.server import Site
         from twisted.web.static import File

         resource = File(os.path.join(os.path.dirname(__file__), 'build'))
         site = Site(resource)
         reactor.listenTCP(int(options.port), site)
         reactor.run()

   else:
      if options.socketserver:
         print "Running Flask under standard Python SocketServer"
         app.run(host = "0.0.0.0", port = int(options.port), debug = options.debug)
      else:
         print "Running Flask under Twisted server"
         import sys
         from twisted.python import log
         from twisted.internet import reactor
         from twisted.web.server import Site
         from twisted.web.wsgi import WSGIResource

         app.debug = options.debug
         if options.debug:
            log.startLogging(sys.stdout)
         resource = WSGIResource(reactor, reactor.getThreadPool(), app)
         site = Site(resource)
         reactor.listenTCP(int(options.port), site)
         reactor.run()
