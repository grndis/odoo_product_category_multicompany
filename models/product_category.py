# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        default=lambda self: self.env.company
    )
    
    # Optional: If you want to allow categories to be used in multiple companies
    company_ids = fields.Many2many(
        'res.company', 
        string='Allowed Companies',
        default=lambda self: self.env.company.ids
    )
    
    @api.constrains('parent_id', 'company_id')
    def _check_category_company(self):
        for category in self:
            if category.parent_id and category.company_id and category.parent_id.company_id and category.company_id != category.parent_id.company_id:
                raise ValidationError(_("The parent category must belong to the same company!"))

