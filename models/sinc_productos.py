from odoo import api, models, tools

import logging
import xmlrpclib

class sinc_productos(models.Model):
    _name = 'sinc_productos.sinc_productos'

    def sincronizar_productos(self):
        url = 'http://50.116.34.232'
        db = 'grupor2c'
        username = 'info@solucionesprisma.com'
        password = 'prismasa'
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        logging.warn(common.version())
        uid = common.authenticate(db, username, password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # Obtener Productos
        ids = models.execute_kw(db, uid, password, 'product.product', 'search', [[['default_code', '!=', False], ['available_in_pos', '=', True]]])
        record = models.execute_kw(db, uid, password, 'product.product', 'read', [ids], {'fields': ['name','default_code','description','available_in_pos', 'list_price', 'standard_price','type','product_tmpl_id']})
        for pr in record:
            # Buscar producto con default code
            producto = self.env['product.product'].search([('default_code','=',pr['default_code'])])
            if producto:
                 # Producto ya sincronizado, update de producto
                 # Setear id del template local
                 pr['product_tmpl_id'] = producto.product_tmpl_id.id
                 producto.write(pr)
            else:
                # Producto no sincronizado, insert de producto
                pr['product_tmpl_id'] = False
                pr_id = self.env['product.product'].create(pr)

        bom_ids = models.execute_kw(db, uid, password, 'mrp.bom', 'search', [[ ['active', '=', True]]])
        record_bom = models.execute_kw(db, uid, password, 'mrp.bom', 'read', [bom_ids], {'fields': ['code','active','type','product_tmpl_id','product_id','sequence']})
        for bom in record_bom:
            bom_template_id = bom['product_tmpl_id'][0]
            # Buscar template del bom recibido
            record_template = models.execute_kw(db, uid, password, 'product.template', 'read', [bom_template_id],{'fields': ['default_code']})
            bom_id_record = bom['id']
            # Buscar producto local con default code
            producto = self.env['product.product'].search([('default_code','=',record_template[0]['default_code'])])
            # Buscar bom  local con producto encontrado
            bom_local = self.env['mrp.bom'].search([('product_tmpl_id','=',producto.product_tmpl_id.id)])
            if bom_local:
                # Ya existe BOM, setear codigo de template local en bom
                bom['product_tmpl_id'] = producto.product_tmpl_id.id
                bom_local.write(bom)
                # BUscar lineas de bom para eliminar
                bom_lines = self.env['mrp.bom.line'].search([('bom_id','=',bom_local.id)])
                for bom_line_local in bom_lines:
                    bom_line_local.unlink()

                # Buscar detalle de bom para insertar lineas en bom local
                bom_line_ids = models.execute_kw(db, uid, password, 'mrp.bom.line', 'search', [[ ['bom_id', '=', bom_id_record]]])
                record_bom_line = models.execute_kw(db, uid, password, 'mrp.bom.line', 'read', [bom_line_ids], {'fields': ['product_id','product_qty','sequence']})
                for bom_line in record_bom_line:
                    # Buscar codigo de producto local en base al default code
                    record_prod_line = models.execute_kw(db, uid, password, 'product.product', 'read', [[bom_line['product_id'][0]]],{
                        'fields': ['name','default_code','description','available_in_pos', 'list_price', 'standard_price','type','product_tmpl_id']
                    })
                    producto_line = self.env['product.product'].search([('default_code','=',record_prod_line[0]['default_code'])])
                    if not producto_line:
                        # No existe producto, insertar de record_prod_line
                        record_prod_line[0]['product_tmpl_id'] = False
                        pr_line_id = self.env['product.product'].create(record_prod_line[0])
                        bom_line['product_id'] = pr_line_id.id
                    else:
                        bom_line['product_id'] = producto_line.id

                    bom_line['bom_id'] = bom_local.id
                    bom_line_id = self.env['mrp.bom.line'].create(bom_line)
            else:
                # No existe BOM
                # Insertar el bom solo si el producto ya existe localmente
                if producto:
                    # Setear a bom el id del template local
                    bom['product_tmpl_id'] = producto.product_tmpl_id.id
                    bom_id = self.env['mrp.bom'].create(bom)
                    bom_id_nuevo = bom_id.id
                    # Buscar detalle
                    bom_line_ids = models.execute_kw(db, uid, password, 'mrp.bom.line', 'search', [[ ['bom_id', '=', bom['id']]]])
                    record_bom_line = models.execute_kw(db, uid, password, 'mrp.bom.line', 'read', [bom_line_ids], {'fields': ['product_id','product_qty','sequence']})
                    for bom_line in record_bom_line:
                        # Buscar codigo de producto local en base al default code
                        record_prod_line = models.execute_kw(db, uid, password, 'product.product', 'read', [[bom_line['product_id'][0]]],{
                              'fields': ['name','default_code','description','available_in_pos', 'list_price', 'standard_price','type','product_tmpl_id']
                        })
                        producto_line = self.env['product.product'].search([('default_code','=',record_prod_line[0]['default_code'])])
                        if not producto_line:
                           # insertar de record_prod_line
                            record_prod_line[0]['product_tmpl_id'] = False
                            pr_line_id = self.env['product.product'].create(record_prod_line[0])
                            bom_line['product_id'] = pr_line_id.id
                        else:
                            bom_line['product_id'] = producto_line.id

                        bom_line['bom_id'] = bom_id_nuevo
                        bom_line_id = self.env['mrp.bom.line'].create(bom_line)

        logging.warn("PROCESO TERMINADO")
        return {'type': 'ir.actions.act_window_close'}
