# -*- coding: utf-8 -*-
{
    'name': 'Multi-Company Product Categories',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Make product categories company-specific',
    'description': """
This module allows product categories to be company-specific instead of global.
Each company can have its own product category hierarchy.
    """,
    'author': 'Grandis',
    'website': 'https://grnd.is',
    'depends': ['product', 'stock'],
    'data': [
        'security/security_rules.xml',
        'views/product_category_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

