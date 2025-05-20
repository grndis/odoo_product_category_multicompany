# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductCategoryCompany(models.Model):
    _name = 'product.category.company'
    _description = 'Product Category per Company'
    
    product_id = fields.Many2one(
        'product.template', 
        string='Product', 
        required=True, 
        ondelete='cascade',
        index=True
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        required=True, 
        ondelete='cascade',
        index=True
    )
    category_id = fields.Many2one(
        'product.category', 
        string='Category', 
        required=True, 
        ondelete='restrict',
        index=True
    )
    
    _sql_constraints = [
        ('product_company_unique', 'unique(product_id, company_id)', 
         'A product can only have one category per company!')
    ]

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    company_category_ids = fields.One2many(
        'product.category.company',
        'product_id',
        string='Categories per Company'
    )
    
    # Override standard category field
    original_categ_id = fields.Many2one(
        related='categ_id', 
        string='Original Category',
        readonly=True
    )
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        # Initialize company-specific category with the default category
        if 'categ_id' in vals and vals['categ_id']:
            self.env['product.category.company'].create({
                'product_id': res.id,
                'company_id': self.env.company.id,
                'category_id': vals['categ_id'],
            })
        return res
    
    def write(self, vals):
        # If category is changing, update company-specific category
        if 'categ_id' in vals:
            for record in self:
                company_id = self.env.company.id
                company_category = self.env['product.category.company'].search([
                    ('product_id', '=', record.id),
                    ('company_id', '=', company_id)
                ], limit=1)
                
                if company_category:
                    company_category.write({'category_id': vals['categ_id']})
                else:
                    self.env['product

