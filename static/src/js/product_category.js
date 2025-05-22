/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";

patch(FormController.prototype, {
  async saveRecord() {
    const result = await this._super(...arguments);

    // Check if we're in a product form and the model is product.template
    if (
      this.model.root.resModel === "product.template" &&
      this.model.root.data.id
    ) {
      const productId = this.model.root.data.id;
      const categoryId = this.model.root.data.categ_id[0];

      // Call the controller to update the company-specific category
      const response = await this.env.services.rpc({
        route: "/product_categ_company/update_category",
        params: {
          product_id: productId,
          category_id: categoryId,
        },
      });

      if (response.success) {
        // Optionally show a notification
        this.env.services.notification.add(
          this.env._t("The category has been updated for the current company."),
          { type: "success" },
        );
      }
    }

    return result;
  },
});
