{
    'name': 'Partner Signature Management',
    'version': '18.0.1.0.0',
    'summary': 'Manage signature transactions and partner tiers',
    'category': 'Sales',
    'author': 'Antigravity',
    'depends': ['base', 'sale_management', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/signature_tier_data.xml',
        'views/partner_signature_tier_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
