# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CompanyProductCategory(models.Model):
    _name = 'company.product.category'
    _description = 'Company-specific Product Category'
    
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
        'company.product.category',
        'product_id',
        string='Categories per Company'
    )
    
    def _get_company_category(self):
        self.ensure_one()
        company_id = self.env.company.id
        company_category = self.env['company.product.category'].search([
            ('product_id', '=', self.id),
            ('company_id', '=', company_id)
        ], limit=1)
        
        if company_category:
            return company_category.category_id
        return self.categ_id
    
    def _set_company_category(self, category):
        self.ensure_one()
        company_id = self.env.company.id
        company_category = self.env['company.product.category'].search([
            ('product_id', '=', self.id),
            ('company_id', '=', company_id)
        ], limit=1)
        
        if company_category:
            company_category.write({'category_id': category.id})
        else:
            self.env['company.product.category'].create({
                'product_id': self.id,
                'company_id': company_id,
                'category_id': category.id
            })
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        # Initialize company-specific category with the default category
        if 'categ_id' in vals and vals['categ_id']:
            self.env['company.product.category'].create({
                'product_id': res.id,
                'company_id': self.env.company.id,
                'category_id': vals['categ_id'],
            })
        return res

