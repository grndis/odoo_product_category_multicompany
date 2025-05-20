# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductCompanyCategory(models.Model):
    _name = 'product.company.category'
    _description = 'Product Category per Company'
    
    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True)
    categ_id = fields.Many2one('product.category', string='Category', required=True)
    
    _sql_constraints = [
        ('product_company_uniq', 'unique (product_tmpl_id, company_id)', 'A product can only have one category per company!')
    ]

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    company_category_ids = fields.One2many('product.company.category', 'product_tmpl_id', string='Categories per Company')
    
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
    
    @api.depends('company_category_ids', 'company_category_ids.categ_id')
    def _compute_category(self):
        for product in self:
            current_company = self.env.company
            company_category = product.company_category_ids.filtered(lambda cc: cc.company_id == current_company)
            
            if company_category:
                product.categ_id = company_category[0].categ_id
            else:
                # Fallback to default category if no company-specific category is set
                default_category = self.env['product.category'].search([], limit=1)
                product.categ_id = default_category
    
    def _inverse_category(self):
        for product in self:
            current_company = self.env.company
            company_category = product.company_category_ids.filtered(lambda cc: cc.company_id == current_company)
            
            if company_category:
                company_category[0].categ_id = product.categ_id
            else:
                self.env['product.company.category'].create({
                    'product_tmpl_id': product.id,
                    'company_id': current_company.id,
                    'categ_id': product.categ_id.id,
                })

