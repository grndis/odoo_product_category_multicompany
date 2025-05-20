# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Store the original category
    original_categ_id = fields.Many2one(
        'product.category', 
        string='Original Category',
        default=lambda self: self.categ_id,
    )
    
    # Company-specific category fields
    company_specific_categ_ids = fields.Serialized(
        string='Company Categories',
        help='JSON field to store company-specific categories'
    )
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if 'categ_id' in vals:
            res.original_categ_id = vals['categ_id']
            # Initialize the company categories dict
            company_id = self.env.company.id
            res.company_specific_categ_ids = {str(company_id): vals['categ_id']}
        return res
    
    def write(self, vals):
        # If category is being changed, store it for the current company
        if 'categ_id' in vals:
            for record in self:
                company_id = str(self.env.company.id)
                company_categories = record.company_specific_categ_ids or {}
                company_categories[company_id] = vals['categ_id']
                vals['company_specific_categ_ids'] = company_categories
        return super(ProductTemplate, self).write(vals)
    
    @api.model
    def _search_company_specific_category(self, operator, value):
        # Enable searching by category across companies
        if operator == '=':
            return [('categ_id', operator, value)]
        return []
    
    def _compute_display_category(self):
        # This method could be used to show the company-specific category in views
        for record in self:
            company_id = str(self.env.company.id)
            company_categories = record.company_specific_categ_ids or {}
            if company_id in company_categories:
                record.display_categ_name = self.env['product.category'].browse(company_categories[company_id]).name
            else:
                record.display_categ_name = record.categ_id.name
    
    display_categ_name = fields.Char(compute='_compute_display_category', string='Category Name')

