/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import {
  ChatterContainer,
} from "@mail/components/chatter_container/chatter_container";
const { session } = require("@web/session");
var rpc = require("web.rpc");

var hideChatter = {};
rpc
  .query({
    model: "sh.hide.chatter",
    method: "checkhide_chatter",
    args: [{ 'user_id': session.uid }],
  })
  .then((response) => {
    // hideChatter = JSON.parse(response);
    hideChatter = response;
  });

patch(ChatterContainer.prototype, "sh_hide_chatter", {
  /**
   * @override
   */

  setup() {
    if (hideChatter) {
        var index = hideChatter.indexOf(
          this.props.threadModel
        );
        this.index_value = index;
    }
    this._super();
  },
});
