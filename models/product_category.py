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
    
    # Store the original category field
    original_categ_id = fields.Many2one(
        'product.category',
        string='Original Category',
        related='categ_id',
        store=True,
        readonly=True
    )
    
    # Override the standard categ_id field
    categ_id = fields.Many2one(
        'product.category',
        string='Category',
        compute='_compute_company_category',
        inverse='_set_company_category',
        store=False,  # Don't store this computed field
        required=True
    )
    
    @api.depends('company_categ_ids', 'company_categ_ids.categ_id')
    def _compute_company_category(self):
        """Compute the category based on the current company"""
        for product in self:
            current_company = self.env.company
            company_category = self.env['product.categ.by.company'].search([
                ('product_tmpl_id', '=', product.id),
                ('company_id', '=', current_company.id)
            ], limit=1)
            
            if company_category:
                product.categ_id = company_category.categ_id
            else:
                # Fallback to the original category if no company-specific one is found
                product.categ_id = product.original_categ_id or self.env.ref('product.product_category_all', raise_if_not_found=False)
    
    def _set_company_category(self):
        """When categ_id is set, update the company-specific category"""
        for product in self:
            current_company = self.env.company
            company_category = self.env['product.categ.by.company'].search([
                ('product_tmpl_id', '=', product.id),
                ('company_id', '=', current_company.id)
            ], limit=1)
            
            if company_category:
                company_category.write({'categ_id': product.categ_id.id})
            else:
                self.env['product.categ.by.company'].create({
                    'product_tmpl_id': product.id,
                    'company_id': current_company.id,
                    'categ_id': product.categ_id.id
                })
    
    @api.model
    def create(self, vals):
        """When creating a product, initialize the company-specific category"""
        res = super(ProductTemplate, self).create(vals)
        
        # Store the original category
        original_categ_id = vals.get('categ_id')
        
        # Create a company-specific category entry for the current company
        if original_categ_id:
            self.env['product.categ.by.company'].create({
                'product_tmpl_id': res.id,
                'company_id': self.env.company.id,
                'categ_id': original_categ_id
            })
            
        return res

