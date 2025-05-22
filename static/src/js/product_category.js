odoo.define("product_categ_company.product_category", function (require) {
  "use strict";

  var FormController = require("web.FormController");
  var core = require("web.core");
  var _t = core._t;

  FormController.include({
    saveRecord: function () {
      var self = this;
      var result = this._super.apply(this, arguments);

      // Check if we're in a product form and the category field has changed
      if (
        this.modelName === "product.template" &&
        this.renderer.state.data.categ_id
      ) {
        var productId = this.renderer.state.data.id;
        var categoryId = this.renderer.state.data.categ_id.data.id;

        // Call the controller to update the company-specific category
        this._rpc({
          route: "/product_categ_company/update_category",
          params: {
            product_id: productId,
            category_id: categoryId,
          },
        }).then(function (result) {
          if (result.success) {
            // Optionally show a notification
            self.displayNotification({
              title: _t("Category Updated"),
              message: _t(
                "The category has been updated for the current company.",
              ),
              type: "success",
            });
          }
        });
      }

      return result;
    },
  });
});
