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

    # Override the standard write method to handle the case when categ_id is changed directly
    def write(self, vals):
        result = super(ProductTemplate, self).write(vals)

        # If the standard category field was changed, update the company-specific category
        if "categ_id" in vals:
            for record in self:
                company_id = self.env.company.id
                company_category = self.env["product.categ.by.company"].search(
                    [
                        ("product_tmpl_id", "=", record.id),
                        ("company_id", "=", company_id),
                    ],
                    limit=1,
                )

                if company_category:
                    company_category.write({"categ_id": vals["categ_id"]})
                else:
                    self.env["product.categ.by.company"].create(
                        {
                            "product_tmpl_id": record.id,
                            "company_id": company_id,
                            "categ_id": vals["categ_id"],
                        }
                    )

        return result

    @api.model_create_multi
    def create(self, vals_list):
        # First create the products with the standard fields
        records = super(ProductTemplate, self).create(vals_list)

        # Then create the company-specific categories
        for record in records:
            # Get the category from the record (not from vals_list to avoid issues)
            category_id = record.categ_id.id
            if category_id:
                # Check if a company-specific category already exists
                company_id = self.env.company.id
                existing = self.env["product.categ.by.company"].search(
                    [
                        ("product_tmpl_id", "=", record.id),
                        ("company_id", "=", company_id),
                    ],
                    limit=1,
                )

                # Only create if it doesn't exist yet
                if not existing:
                    self.env["product.categ.by.company"].create(
                        {
                            "product_tmpl_id": record.id,
                            "company_id": company_id,
                            "categ_id": category_id,
                        }
                    )

        return records
