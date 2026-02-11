from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partnership_status = fields.Selection([
        ('draft', 'Draft'),
        ('signed', 'Signed'),
        ('terminated', 'Terminated')
    ], string='Partnership Status', default='draft')

    partnership_type = fields.Selection([
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise')
    ], string='Partnership Type')

    partnership_pdf = fields.Binary(string='Partnership PDF')

    signature_transaction_count = fields.Integer(
        string='Signature Transaction Count',
        compute='_compute_signature_transaction_count',
        store=True
    )
    
    current_transaction_price = fields.Float(
        string='Current Transaction Price',
        compute='_compute_current_transaction_price',
        store=True,
        digits=(10, 4)
    )

    @api.depends('child_ids.sale_order_ids.state', 'child_ids.sale_order_ids.order_line.product_id.is_signature_pack')
    def _compute_signature_transaction_count(self):
        for partner in self:
            count = 0
            # Get all child contacts
            children = partner.child_ids
            if children:
                # Find confirmed sales orders for children
                domain = [
                    ('partner_id', 'in', children.ids),
                    ('state', '=', 'sale') # confirmed orders
                ]
                orders = self.env['sale.order'].search(domain)
                
                for order in orders:
                    for line in order.order_line:
                        if line.product_id.is_signature_pack:
                            # It implies sum of product quantities * signature_count per pack
                            # If signature_count is not set on product.product, we access it via product_id.product_tmpl_id or directly if fields are related.
                            # product.product inherits fields from template usually. Let's check safely.
                            sig_count = line.product_id.signature_count or 0
                            count += (line.product_uom_qty * sig_count)
            
            partner.signature_transaction_count = count

    @api.depends('signature_transaction_count')
    def _compute_current_transaction_price(self):
        # Prefetch tiers ordered by min_quantity descending
        tiers = self.env['partner.signature.tier'].search([], order='min_quantity desc')
        
        for partner in self:
            price = 0.0
            for tier in tiers:
                if partner.signature_transaction_count >= tier.min_quantity:
                    price = tier.transaction_price
                    break
            partner.current_transaction_price = price

    def action_view_child_sales(self):
        self.ensure_one()
        children = self.child_ids
        return {
            'name': 'Child Sales Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', 'in', children.ids)],
            'context': {'default_partner_id': self.id},
        }
