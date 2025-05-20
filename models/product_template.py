# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Store the original category
    original_categ_id = fields.Many2one(
        'product.category', 
        string='Original Category',
        default=lambda self: self.categ_id,
    )
    
    # Company-specific category fields - use Text field instead of Serialized
    company_specific_categ_json = fields.Text(
        string='Company Categories JSON',
        help='JSON field to store company-specific categories'
    )
    
    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if 'categ_id' in vals:
            res.original_categ_id = vals['categ_id']
            # Initialize the company categories dict
            company_id = self.env.company.id
            res.company_specific_categ_json = json.dumps({str(company_id): vals['categ_id']})
        return res
    
    def write(self, vals):
        # If category is being changed, store it for the current company
        if 'categ_id' in vals:
            for record in self:
                company_id = str(self.env.company.id)
                company_categories = {}
                if record.company_specific_categ_json:
                    try:
                        company_categories = json.loads(record.company_specific_categ_json)
                    except:
                        company_categories = {}
                
                company_categories[company_id] = vals['categ_id']
                vals['company_specific_categ_json'] = json.dumps(company_categories)
        
        return super(ProductTemplate, self).write(vals)
    
    def get_company_category(self, company_id=None):
        """Get the category for a specific company"""
        self.ensure_one()
        if not company_id:
            company_id = self.env.company.id
        
        company_id_str = str(company_id)
        
        if not self.company_specific_categ_json:
            return self.categ_id.id
        
        try:
            company_categories = json.loads(self.company_specific_categ_json)
            if company_id_str in company_categories:
                return company_categories[company_id_str]
        except:
            pass
        
        return self.categ_id.id
    
    def _compute_display_category(self):
        """Compute the display category for the current company"""
        for record in self:
            categ_id = record.get_company_category()
            category = self.env['product.category'].browse(categ_id)
            record.display_categ_name = category.name if category else ""
    
    display_categ_name = fields.Char(
        compute='_compute_display_category', 
        string='Company Category'
    )
    
    # Override the default categ_id field to make it computed
    @api.depends('company_specific_categ_json')
    def _compute_category(self):
        for record in self:
            categ_id = record.get_company_category()
            record.categ_id = categ_id
    
    def _inverse_category(self):
        for record in self:
            company_id = str(self.env.company.id)
            company_categories = {}
            
            if record.company_specific_categ_json:
                try:
                    company_categories = json

