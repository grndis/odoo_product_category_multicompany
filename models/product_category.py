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
    
    # We'll keep the original categ_id field but add methods to handle company-specific behavior
    
    @api.model
    def create(self, vals):
        """When creating a product, initialize the company-specific category"""
        res = super(ProductTemplate, self).create(vals)
        
        # Create a company-specific category entry for the current company
        if 'categ_id' in vals and vals['categ_id']:
            self.env['product.categ.by.company'].create({
                'product_tmpl_id': res.id,
                'company_id': self.env.company.id,
                'categ_id': vals['categ_id'],
            })
            
        return res
    
    def write(self, vals):
        """When updating a product, handle company-specific category"""
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
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """Override search to handle company-specific categories"""
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and len(arg) == 3 and arg[0] == 'categ_id':
                operator = arg[1]
                value = arg[2]
                
                # Get products with matching company-specific category
                company_id = self.env.company.id
                category_records = self.env['product.categ.by.company'].search([
                    ('company_id', '=', company_id),
                    ('categ_id', operator, value)
                ])
                product_ids = category_records.mapped('product_tmpl_id').ids
                
                if product_ids:
                    new_args.append(('id', 'in', product_ids))
                else:
                    # If no company-specific categories match, use the original condition
                    new_args.append(arg)
            else:
                new_args.append(arg)
        
        return super(ProductTemplate, self)._search(
            new_args, offset=offset, limit=limit, order=order, 
            count=count, access_rights_uid=access_rights_uid
        )
    
    # Add a method to get the company-specific category
    def get_company_category(self):
        """Get the category for the current company"""
        self.ensure_one()
        company_id = self.env.company.id
        company_category = self.env['product.categ.by.company'].search([
            ('product_tmpl_id', '=', self.id),
            ('company_id', '=', company_id)
        ], limit=1)
        
        if company_category:
            return company_category.categ_id
        return self.categ_id
    
    # Add a method to update the company-specific category
    def update_company_category(self, category_id):
        """Update the category for the current company"""
        self.ensure_one()
        company_id = self.env.company.id
        company_category = self.env['product.categ.by.company'].search([
            ('product_tmpl_id', '=', self.id),
            ('company_id', '=', company_id)
        ], limit=1)
        
        if company_category:
            company_category.write({'categ_id': category_id})
        else:
            self.env['product.categ.by.company'].create({
                'product_tmpl_id': self.id,
                'company_id': company_id,
                'categ_id': category_id
            })

