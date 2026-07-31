/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { FormController } from "@web/views/form/form_controller";
import { ListRenderer } from "@web/views/list/list_renderer";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
const { session } = require("@web/session");
var rpc = require("web.rpc");
const { onMounted } = owl;
// model_dic = JSON.parse(response);

var group_show_delete = true;
var group_show_export = true;
var group_show_duplicate = true;
var group_show_create = true;
var group_show_edit = true;
var group_show_archieve = true;

var model_dic = {};

rpc
  .query({
    model: "sh.access.model",
    method: "check_crud_operation",
    args: [{ user_id: session.uid }],
  })
  .then((response) => {
    model_dic = response;
  });

patch(FormController.prototype, "sh_multiaction_form_access", {
  /**
   * @override
   */
  setup() {
    // alert('Inehrited Successfully');
    this._super();
    var self = this;
    let count = 0;
    if (Object.keys(model_dic).length) {
      $.each(model_dic, function (index, value) {
        if (count == 0) {
          if (index == self.props.resModel) {
            count = count + 1;
            self.group_show_create = value["hide_create"];
            self.group_show_edit = value["hide_edit"];
            group_show_export = value["hide_export"];
            group_show_delete = value["hide_delete"];
            group_show_archieve = value["hide_archieve"];
            group_show_duplicate = value["hide_duplicate"];
          } else {
            self.group_show_create = true;
            self.group_show_edit = true;
          }
        }
      });
    } else {
      self.group_show_create = true;
      self.group_show_edit = true;
    }
  },

  getActionMenuItems() {
    const otherActionItems = [];
    if (this.archiveEnabled && group_show_archieve) {
      if (this.model.root.isActive) {
        otherActionItems.push({
          key: "archive",
          description: this.env._t("Archive"),
          callback: () => {
            const dialogProps = {
              body: this.env._t(
                "Are you sure that you want to archive this record?"
              ),
              confirmLabel: this.env._t("Archive"),
              confirm: () => this.model.root.archive(),
              cancel: () => {},
            };
            this.dialogService.add(ConfirmationDialog, dialogProps);
          },
        });
      } else {
        otherActionItems.push({
          key: "unarchive",
          description: this.env._t("Unarchive"),
          callback: () => this.model.root.unarchive(),
        });
      }
    }
    if (
      this.archInfo.activeActions.create &&
      this.archInfo.activeActions.duplicate &&
      group_show_duplicate
    ) {
      otherActionItems.push({
        key: "duplicate",
        description: this.env._t("Duplicate"),
        callback: () => this.duplicateRecord(),
      });
    }
    if (
      this.archInfo.activeActions.delete &&
      !this.model.root.isVirtual &&
      group_show_delete
    ) {
      otherActionItems.push({
        key: "delete",
        description: this.env._t("Delete"),
        callback: () => this.deleteRecord(),
        skipSave: true,
      });
    }
    return Object.assign({}, this.props.info.actionMenus, {
      other: otherActionItems,
    });
  },
});

patch(ListController.prototype, "sh_multiaction_list_access", {
  /**
   * @override
   */
  setup() {
    this._super();
    onMounted(this.onMounted);
    var self = this;
    let count = 0;
    if (Object.keys(model_dic).length) {
      $.each(model_dic, function (index, value) {
        if (count == 0) {
          if (index == self.props.resModel) {
            count = count + 1;
            self.group_show_create = value["hide_create"];
            self.group_show_edit = value["hide_edit"];
            group_show_export = value["hide_export"];
            group_show_delete = value["hide_delete"];
            group_show_archieve = value["hide_archieve"];
          } else {
            self.group_show_create = true;
          }
        }
      });
    } else {
      self.group_show_create = true;
    }
  },

  onMounted() {
    if (group_show_export == false) {
      var ExportButton = $(".o_list_export_xlsx");
      console.log("\n\n\n\n Custom File", ExportButton);
      ExportButton.addClass("d-none");
    }
  },

  getActionMenuItems() {
    const isM2MGrouped = this.model.root.isM2MGrouped;
    const otherActionItems = [];
    if (this.isExportEnable && group_show_export) {
      otherActionItems.push({
        key: "export",
        description: this.env._t("Export"),
        callback: () => this.onExportData(),
      });
    }
    if (this.archiveEnabled && group_show_archieve) {
      otherActionItems.push({
        key: "archive",
        description: this.env._t("Archive"),
        callback: () => {
          const dialogProps = {
            body: this.env._t(
              "Are you sure that you want to archive all the selected records?"
            ),
            confirmLabel: this.env._t("Archive"),
            confirm: () => {
              this.toggleArchiveState(true);
            },
            cancel: () => {},
          };
          this.dialogService.add(ConfirmationDialog, dialogProps);
        },
      });
      otherActionItems.push({
        key: "unarchive",
        description: this.env._t("Unarchive"),
        callback: () => this.toggleArchiveState(false),
      });
    }
    if (this.activeActions.delete && group_show_delete) {
      otherActionItems.push({
        key: "delete",
        description: this.env._t("Delete"),
        callback: () => this.onDeleteSelectedRecords(),
      });
    }
    return Object.assign({}, this.props.info.actionMenus, {
      other: otherActionItems,
    });
  },
});

patch(KanbanController.prototype, "sh_multiaction_kanban_access", {
  /**
   * @override
   */
  setup() {
    this._super();
    var self = this;
    var self = this;
    let count = 0;
    if (Object.keys(model_dic).length) {
      $.each(model_dic, function (index, value) {
        if (count == 0) {
          if (index == self.props.resModel) {
            count = count + 1;
            self.group_show_create = value["hide_create"];
          } else {
            self.group_show_create = true;
          }
        }
      });
    } else {
      self.group_show_create = true;
    }
  },
});

patch(ListRenderer.prototype, "sh_multiaction_export_button_access", {
  /**
   * @override
   */
  setup() {
    this._super();
    var self = this;
    let count = 0;
    if (Object.keys(model_dic).length) {
      $.each(model_dic, function (index, value) {
        if (count == 0) {
          if (index == self.props.resModel) {
            count = count + 1;
            self.group_show_create = value["hide_create"];
            self.group_show_edit = value["hide_edit"];
            group_show_export = value["hide_export"];
            group_show_delete = value["hide_delete"];
            group_show_archieve = value["hide_archieve"];
          } else {
            self.group_show_create = true;
          }
        }
      });
    } else {
      self.group_show_create = true;
    }
  },

  setDefaultColumnWidths() {
    if (group_show_export == false) {
      var ExportButton = $(".o_list_export_xlsx");
      console.log("\n\n\n\n Custom File 05", ExportButton);
      ExportButton.addClass("d-none");
    }
    this._super();
  },
});
