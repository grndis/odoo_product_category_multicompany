# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Fields for Company 1
    company1_categ_id = fields.Many2one(
        'product.category', 
        string='Category (Company 1)'
    )
    
    # Fields for Company 2
    company2_categ_id = fields.Many2one(
        'product.category', 
        string='Category (Company 2)'
    )
    
    # Override the default categ_id field to make it computed
    categ_id = fields.Many2one(
        'product.category', 
        string='Category', 
        compute='_compute_category',
        inverse='_inverse_category',
        store=True,
        readonly=False,
        required=True
    )
    
    @api.depends('company1_categ_id', 'company2_categ_id')
    def _compute_category(self):
        company1 = self.env.ref('base.main_company')  # Replace with your Company 1 ID
        company2 = self.env.ref('__export__.res_company_2_abcdef')  # Replace with your Company 2 ID
        
        for product in self:
            if self.env.company == company1 and product.company1_categ_id:
                product.categ_id = product.company1_categ_id
            elif self.env.company == company2 and product.company2_categ_id:
                product.categ_id = product.company2_categ_id
            elif not product.categ_id:
                # Fallback to default category
                product.categ_id = self.env.ref('product.product_category_all', raise_if_not_found=False) or self.env['product.category'].search([], limit=1)
    
    def _inverse_category(self):
        company1 = self.env.ref('base.main_company')  # Replace with your Company 1 ID
        company2 = self.env.ref('__export__.res_company_2_abcdef')  # Replace with your Company 2 ID
        
        for product in self:
            if self.env.company == company1:
                product.company1_categ_id = product.categ_id
            elif self.env.company == company2:
                product.company2_categ_id = product.categ_id

