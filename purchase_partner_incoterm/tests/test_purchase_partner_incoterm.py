from odoo.tests.common import TransactionCase


class TestPurchasePartnerIncoterm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.partner_1 = cls.ResPartner.create(
            {
                "name": "Test Partner",
                "purchase_incoterm_id": cls.env.ref("account.incoterm_EXW").id,
                "purchase_incoterm_address_id": cls.ResPartner.create(
                    {
                        "name": "Incoterm Address",
                    }
                ).id,
            }
        )
        cls.purchase_order_1 = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner_1.id,
            }
        )

    def test_01_onchange_partner_id(self):
        # GIVEN / WHEN
        self.purchase_order_1.onchange_partner_id()
        # THEN
        self.assertEqual(
            self.purchase_order_1.incoterm_id, self.partner_1.purchase_incoterm_id
        )
        self.assertEqual(
            self.purchase_order_1.incoterm_address_id,
            self.partner_1.purchase_incoterm_address_id,
        )
