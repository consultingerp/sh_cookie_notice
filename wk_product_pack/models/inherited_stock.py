#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
	_inherit = 'product.template'
	
	def _compute_quantities_dict(self):
		res = super(ProductTemplate, self)._compute_quantities_dict()
		if len(self) > 1:
			pass
		else:
			ACT_VARIANTS = self.mapped('product_variant_ids')
			variants_available = self.mapped('product_variant_ids')._product_available()
			prod_available = {}
			for template in self:
				qty_available = 0
				virtual_available = 0
				incoming_qty = 0
				outgoing_qty = 0
				for p in template.product_variant_ids:
					qty_available += variants_available[p.id]["qty_available"]
					virtual_available += variants_available[p.id]["virtual_available"]
					incoming_qty += variants_available[p.id]["incoming_qty"]
					outgoing_qty += variants_available[p.id]["outgoing_qty"]
					################################### CODE ADDED BY JAHANGIR ####################################
					if template.is_pack and template.wk_product_pack:
						if len(template.product_variant_ids) > 1:
							variants_list = template.product_variant_ids.ids
						else:
							variants_list = [template.product_variant_ids.id]

						for pp in template.wk_product_pack:
							variants_list.append(pp.product_id.id)
						variants = self.env['product.product'].browse(variants_list)
						variants_available.update(variants._product_available())
						qty_avail = []
						vir_avail = []
						inco_qty = []
						outgo_qty = []
						for pp in template.wk_product_pack:
							if pp.product_id and pp.product_quantity > 0:
								qty_avail.append(variants_available[pp.product_id.id]["qty_available"]/pp.product_quantity)
								vir_avail.append(variants_available[pp.product_id.id]["virtual_available"]/pp.product_quantity)
								inco_qty.append(variants_available[pp.product_id.id]["incoming_qty"]/pp.product_quantity)
								outgo_qty.append(variants_available[pp.product_id.id]["outgoing_qty"]/pp.product_quantity)
						qty_available = min(qty_avail)
						virtual_available = min(vir_avail)
						incoming_qty = min(inco_qty)
						outgoing_qty = min(outgo_qty)
						template.product_variant_ids = ACT_VARIANTS
				################################### CODE CLOSED BY JAHANGIR ####################################
				prod_available[template.id] = {
					"qty_available": qty_available,
					"virtual_available": virtual_available,
					"incoming_qty": incoming_qty,
					"outgoing_qty": outgoing_qty,
				}
			return prod_available
		return res

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'
	
	def _get_delivered_qty(self):
		res = super(SaleOrderLine, self)._get_delivered_qty()
		if self.product_id.is_pack:
			return self.product_uom_qty
		return res