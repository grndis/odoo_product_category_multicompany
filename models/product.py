# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductCategByCompany(models.Model):
    _name = "product.categ.by.company"
    _description = "Product Category by Company"

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, ondelete="cascade", index=True
    )
    categ_id = fields.Many2one(
        "product.category",
        string="Category",
        required=True,
        ondelete="restrict",
        index=True,
    )

    _sql_constraints = [
        (
            "product_company_unique",
            "unique(product_tmpl_id, company_id)",
            "A product can only have one category per company!",
        )
    ]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    company_categ_ids = fields.One2many(
        "product.categ.by.company", "product_tmpl_id", string="Categories per Company"
    )

    # Add a computed field to show the current company's category
    company_specific_categ_id = fields.Many2one(
        "product.category",
        string="Company Category",
        compute="_compute_company_specific_categ",
        inverse="_inverse_company_specific_categ",
        store=False,
    )

    @api.depends(
        "company_categ_ids",
        "company_categ_ids.categ_id",
        "company_categ_ids.company_id",
    )
    def _compute_company_specific_categ(self):
        for record in self:
            current_company = self.env.company
            company_category = self.env["product.categ.by.company"].search(
                [
                    ("product_tmpl_id", "=", record.id),
                    ("company_id", "=", current_company.id),
                ],
                limit=1,
            )

            if company_category:
                record.company_specific_categ_id = company_category.categ_id
            else:
                record.company_specific_categ_id = record.categ_id

    def _inverse_company_specific_categ(self):
        for record in self:
            if not record.company_specific_categ_id:
                continue

            current_company = self.env.company
            company_category = self.env["product.categ.by.company"].search(
                [
                    ("product_tmpl_id", "=", record.id),
                    ("company_id", "=", current_company.id),
                ],
                limit=1,
            )

            if company_category:
                company_category.categ_id = record.company_specific_categ_id
            else:
                self.env["product.categ.by.company"].create(
                    {
                        "product_tmpl_id": record.id,
                        "company_id": current_company.id,
                        "categ_id": record.company_specific_categ_id.id,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductTemplate, self).create(vals_list)

        # Initialize company-specific categories for each new product
        for record, vals in zip(records, vals_list):
            if "categ_id" in vals and vals["categ_id"]:
                self.env["product.categ.by.company"].create(
                    {
                        "product_tmpl_id": record.id,
                        "company_id": self.env.company.id,
                        "categ_id": vals["categ_id"],
                    }
                )

        return records
