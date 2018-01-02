# -*- coding: utf-8 -*-
from odoo import http

# class SincProductos(http.Controller):
#     @http.route('/sinc_productos/sinc_productos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sinc_productos/sinc_productos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sinc_productos.listing', {
#             'root': '/sinc_productos/sinc_productos',
#             'objects': http.request.env['sinc_productos.sinc_productos'].search([]),
#         })

#     @http.route('/sinc_productos/sinc_productos/objects/<model("sinc_productos.sinc_productos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sinc_productos.object', {
#             'object': obj
#         })