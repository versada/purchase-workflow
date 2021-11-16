# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestPOLineProcurementGroup(SavepointCase):
    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.pyromaniacs = cls.env["res.partner"].create(
            {"name": "Pyromaniacs Inc", "company_type": "company"}
        )
        cls.lighter = (
            cls.env["product.template"]
            .create(
                {
                    "name": "Lighter",
                    "type": "product",
                    "purchase_ok": True,
                    "seller_ids": [
                        (
                            0,
                            0,
                            {"name": cls.pyromaniacs.id, "min_qty": 1, "price": 1.0},
                        )
                    ],
                }
            )
            .product_variant_ids
        )

        cls.lighter.write({"route_ids": [(4, cls.mto_route.id)]})

        cls.proc_group1 = cls.env["procurement.group"].create(
            {"name": "PROC1", "move_type": "direct"}
        )
        cls.proc_group2 = cls.env["procurement.group"].create(
            {"name": "PROC2", "move_type": "direct"}
        )

        cls.move1 = (
            cls.env["stock.move"]
            .create(
                {
                    "name": "TEST-MOVE-1",
                    "location_id": cls.warehouse.lot_stock_id.id,
                    "location_dest_id": cls.location_customers.id,
                    "product_id": cls.lighter.id,
                    "product_uom": cls.uom_unit.id,
                    "product_uom_qty": 10,
                    "procure_method": "make_to_order",
                    "group_id": cls.proc_group1.id,
                }
            )
            ._action_confirm()
        )

        cls.move2 = (
            cls.env["stock.move"]
            .create(
                {
                    "name": "TEST-MOVE-2",
                    "location_id": cls.warehouse.lot_stock_id.id,
                    "location_dest_id": cls.location_customers.id,
                    "product_id": cls.lighter.id,
                    "product_uom": cls.uom_unit.id,
                    "product_uom_qty": 15,
                    "procure_method": "make_to_order",
                    "group_id": cls.proc_group2.id,
                }
            )
            ._action_confirm()
        )

        cls.move3 = (
            cls.env["stock.move"]
            .create(
                {
                    "name": "TEST-MOVE-3",
                    "location_id": cls.warehouse.lot_stock_id.id,
                    "location_dest_id": cls.location_customers.id,
                    "product_id": cls.lighter.id,
                    "product_uom": cls.uom_unit.id,
                    "product_uom_qty": 20,
                    "procure_method": "make_to_order",
                    "group_id": cls.proc_group2.id,
                }
            )
            ._action_confirm()
        )

    def test_po_line_proc_group(self):
        po = self.env["purchase.order"].search(
            [("partner_id", "=", self.pyromaniacs.id)]
        )
        self.assertEqual(len(po.order_line), 2)
        self.assertEqual(
            po.order_line.mapped("procurement_group_id.name"), ["PROC1", "PROC2"]
        )
        for line in po.order_line:
            if line.procurement_group_id == self.proc_group1:
                self.assertAlmostEqual(line.product_uom_qty, 10)
            if line.procurement_group_id == self.proc_group2:
                self.assertAlmostEqual(line.product_uom_qty, 35)

        po.button_confirm()

        move_lines = po.picking_ids.move_lines
        self.assertEqual(len(move_lines), 2)
        self.assertEqual(move_lines.mapped("group_id.name"), ["PROC1", "PROC2"])
        for move_line in move_lines:
            if move_line.procurement_group_id == self.proc_group1:
                self.assertAlmostEqual(move_line.product_uom_qty, 10)
            if move_line.procurement_group_id == self.proc_group2:
                self.assertAlmostEqual(move_line.product_uom_qty, 35)
