from odoo import fields, models


class ProjectTask(models.Model):
    """ The Class ProjectTask for the model project_task which is to
    customise the access for the records. """
    _inherit = 'project.task'

    task_access_user_ids = fields.Many2many('res.users',
                                            string='Access Limited Users',
                                            help="The users who has access "
                                            "for this record")
    user_admin_check = fields.Boolean(string='sale_line_id_check',
                                      compute='_compute_user_admin_check',
                                      help="The Compute field to check if "
                                      "the user is an Internal user or not")

    # def _compute_user_admin_check(self):
    #     """The function computes a boolean field to check if the current
    #     user is the admin for the purpose of making the
    #     'task_access_user_ids' field editable only for 'user_admin'"""
    #     for rec in self:
    #         if rec.env.user.id == rec.env.ref('base.user_admin').id:
    #             rec.user_admin_check = True
    #         else:
    #             rec.user_admin_check = False


    def _compute_user_admin_check(self):
        """
        Check if the current user is:
        1. Odoo admin (base.user_admin), OR
        2. A Project Administrator (group_project_manager)
        """
        admin_user = self.env.ref("base.user_admin")
        project_admin_group = self.env.ref("project.group_project_manager")

        for rec in self:
            if (
                self.env.user == admin_user
                or project_admin_group in self.env.user.groups_id
            ):
                rec.user_admin_check = True
            else:
                rec.user_admin_check = False
