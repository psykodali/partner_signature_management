from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_signature_pack = fields.Boolean(string='Is Signature Pack')
    signature_count = fields.Integer(string='Signature Count', help='Number of signatures included in this pack')
