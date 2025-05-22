from odoo import http
from odoo.http import request

class ProductCategoryController(http.Controller):
    
    @http.route('/product_categ_company/update_category', type='json', auth="user")
    def update_category(self, product_id, category_id):
        """Update the category for the current company"""
        product = request.env['product.template'].browse(int(product_id))
        product.update_company_category(int(category_id))
        return {'success': True}

