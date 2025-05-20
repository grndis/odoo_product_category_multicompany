# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductCategByCompany(models.Model):
    _name = 'product.categ.by.company'
    _description = 'Product Category by Company'
    
    product_tmpl_id = fields.Many2one(
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
    categ_id = fields.Many2one(
        'product.category', 
        string='Category', 
        required=True, 
        ondelete='restrict',
        index=True
    )
    
    _sql_constraints = [
        ('product_company_unique', 'unique(product_tmpl_id, company_id)', 
         'A product can only have one category per company!')
    ]

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    company_categ_ids = fields.One2many(
        'product.categ.by.company',
        'product_tmpl_id',
        string='Categories per Company'
    )
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        # Initialize company-specific category with the default category
        if 'categ_id' in vals and vals['categ_id']:
            self.env['product.categ.by.company'].create({
                'product_tmpl_id': res.id,
                'company_id': self.env.company.id,
                'categ_id': vals['categ_id'],
            })
        return res
    
    def write(self, vals):
        # If category is being changed, update the company-specific category
        if 'categ_id' in vals:
            for record in self:
                company_id = self.env.company.id
                company_category = self.env['product.categ.by.company'].search([
                    ('product_tmpl_id', '=', record.id),
                    ('company_id', '=', company_id)
                ], limit=1)
                
                if company_category:
                    company_category.write({'categ_id': vals['categ_id']})
                else:
                    self.env['product.categ.by.company'].create({
                        'product_tmpl_id': record.id,
                        'company_id': company_id,
                        'categ_id': vals['categ_id']
                    })
        
        return super(ProductTemplate, self).write(vals)

