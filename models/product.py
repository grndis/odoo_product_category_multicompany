# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCategoryCompany(models.Model):
    _name = 'product.category.company'
    _description = 'Product Category per Company'
    
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
    category_id = fields.Many2one(
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
    
    company_category_ids = fields.One2many(
        'product.category.company',
        'product_tmpl_id',
        string='Categories per Company'
    )
    
    # Override standard category field
    standard_categ_id = fields.Many2one(
        related='categ_id', 
        string='Standard Category',
        readonly=True
    )
    
    company_specific_categ_id = fields.Many2one(
        'product.category',
        string='Company-Specific Category',
        compute='_compute_company_category',
        inverse='_set_company_category',
        store=False,
        help='Category specific to the current company'
    )
    
    @api.depends('company_category_ids', 'company_category_ids.category_id')
    def _compute_company_category(self):
        for product in self:
            current_company = self.env.company
            company_category = product.company_category_ids.filtered(
                lambda cc: cc.company_id == current_company
            )
            
            if company_category:
                product.company_specific_categ_id = company_category[0].category_id
            else:
                product.company_specific_categ_id = product.categ_id
    
    def _set_company_category(self):
        for product in self:
            if not product.company_specific_categ_id:
                continue
                
            current_company = self.env.company
            company_category = product.company_category_ids.filtered(
                lambda cc: cc.company_id == current_company
            )
            
            if company_category:
                company_category[0].category_id = product.company_specific_categ_id
            else:
                self.env['product.category.company'].create({
                    'product_tmpl_id': product.id,
                    'company_id': current_company.id,
                    'category_id': product.company_specific_categ_id.id,
                })
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        # Initialize company-specific category with the default category
        if 'categ_id' in vals and vals['categ_id']:
            self.env['product.category.company'].create({
                'product_tmpl_id': res.id,
                'company_id': self.env.company.id,
                'category_id': vals['categ_id'],
            })
        return res
    
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        # If standard category changes and no company-specific category exists,
        # create one for the current company
        if 'categ_id' in vals:
            for product in self:
                current_company = self.env.company
                company_category = product.company_category_ids.filtered(
                    lambda cc: cc.company_id == current_company
                )
                
                if not company_category:
                    self.env['product.category.company'].create({
                        'product_tmpl_id': product.id,
                        'company_id': current_company.id,
                        'category_id': vals['categ_id'],
                    })
        return res

