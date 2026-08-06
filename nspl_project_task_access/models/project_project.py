from odoo import fields, models


class ProjectProject(models.Model):
    """
    Custom access control: limit which users can access or edit a project.

    Modified by Sarthak Samgir:
    Added logic to give specific users access to view the project and its tasks
    based on the permissions assigned in 'project_access_user_ids'.
    """
    _inherit = "project.project"

    project_access_user_ids = fields.Many2many('res.users',
                                               string='Access Limited Users',
                                               help="The users who has "
                                               "access for this record")
    user_admin_check = fields.Boolean(string='sale_line_id_check',
                                      compute='_compute_user_admin_check',
                                      help="To check if the user is an Internal"
                                      " user or not")

    # def _compute_user_admin_check(self):
    #     """ Determines if the current user is an admin to allow the
    #     'task_access_user_ids' field to be editable only by 'user_admin'."""
    #     for rec in self:
    #         if rec.env.user.id == rec.env.ref('base.user_admin').id:
    #             rec.user_admin_check = True
    #         else:
    #             rec.user_admin_check = False


    def _compute_user_admin_check(self):
        """
        Determine if the current logged-in user is:
        1. Odoo Administrator (base.user_admin)
        2. Project Administrator (group_project_manager)

        Modified by Sarthak Samgir:
        Updated the logic so that users with Project Administrator rights
        are also allowed to add/update 'project_access_user_ids'.
        """
        # Cache these refs once per call rather than re-resolving inside
        # the loop below -- negligible on small recordsets but avoids
        # repeated XML-ID lookups on a bulk write.
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

