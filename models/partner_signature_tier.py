from odoo import models, fields

class PartnerSignatureTier(models.Model):
    _name = 'partner.signature.tier'
    _description = 'Partner Signature Tier'
    _order = 'min_quantity asc'

    name = fields.Char(string='Tier Name', required=True)
    min_quantity = fields.Integer(string='Minimum Quantity', required=True, default=0)
    transaction_price = fields.Float(string='Transaction Price', required=True, digits=(10, 4))
