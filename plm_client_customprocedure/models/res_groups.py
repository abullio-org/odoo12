# -*- encoding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, Open Source Management Solution    
#    Copyright (C) 2010-2011 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

'''
Created on Apr 19, 2017

@author: daniel
'''

import logging
import tempfile
import os
import base64
from odoo import models
from odoo import fields
from odoo import api
from odoo import _


class ResGroups(models.Model):
    _name = 'res.groups'
    _inherit = 'res.groups'

    custom_procedure = fields.Binary(string=_('Client CustomProcedure'))
    custom_procedure_fname = fields.Char(_("New File name"))
    custom_read_content = fields.Text('Modif Content', default='')

    custom_multicad = fields.Binary(string=_('Client Multicad'))
    custom_multicad_fname = fields.Char(_("New File name"))
    custom_multicad_content = fields.Text('Modif Content', default='')

    @api.multi
    def write(self, vals):
        erase = self.env.context.get('erase_multicad', True)
        erase_custom = self.env.context.get('erase_customprocedure', True)
        if erase and 'custom_multicad_content' in vals:
            self.open_custom_multicad_save(vals)
        if erase_custom and 'custom_read_content' in vals:
            self.open_custommodule_save(vals)
        return super(ResGroups, self).write(vals)

    @api.multi
    def open_custommodule_edit(self):
        for groupBrws in self:
            if groupBrws.custom_procedure:
                fileReadableContent = base64.decodestring(groupBrws.custom_procedure)
                if self.custom_read_content:
                    fileReadableContent = ''
                self.with_context({'erase_customprocedure': False}).custom_read_content = fileReadableContent
            
    @api.multi
    def open_custom_multicad_edit(self):
        for groupBrws in self:
            if groupBrws.custom_multicad:
                fileReadableContent = base64.decodestring(groupBrws.custom_multicad)
                if self.custom_multicad_content:
                    fileReadableContent = ''
                self.with_context({'erase_multicad': False}).custom_multicad_content = fileReadableContent

    @api.multi
    def open_custommodule_save(self, vals):
        for groupBrws in self:
            self.commonSave(vals, 
                            'custom_procedure', 
                            'custom_read_content',
                            groupBrws.custom_procedure_fname,
                            groupBrws.custom_procedure
                            )

    @api.model
    def open_custom_multicad_save(self, vals):
        for groupBrws in self:
            self.commonSave(vals, 
                            'custom_multicad', 
                            'custom_multicad_content',
                            groupBrws.custom_multicad_fname,
                            groupBrws.custom_multicad
                            )

    @api.model
    def commonSave(self, vals, binary_field, content_field, fname, custom_file):
        vals[binary_field] = base64.encodestring(vals.get(content_field, '').encode('utf-8'))
        tmpFolder = tempfile.gettempdir()
        if fname:
            customFilePath = os.path.join(tmpFolder, fname)
            with open(customFilePath, 'wb') as writeFile:
                writeFile.write(base64.decodestring(custom_file))
        vals[content_field] = ''
        
    @api.multi
    def getCustomProcedure(self):
        for groupBrws in self:
            logging.info('Request CustomProcedure file for user %r and group %r-%r and id %r' % (groupBrws.env.uid, groupBrws.category_id.name, groupBrws.name, groupBrws.id))
            if groupBrws.custom_procedure:
                return True, groupBrws.custom_procedure, groupBrws.custom_procedure_fname
        return False, '', groupBrws.custom_procedure_fname

    @api.multi
    def getCustomMulticad(self):
        for groupBrws in self:
            logging.info('Request Multicad file for user %r and group %r-%r and id %r' % (groupBrws.env.uid, groupBrws.category_id.name, groupBrws.name, groupBrws.id))
            if groupBrws.custom_multicad:
                return True, groupBrws.custom_multicad, groupBrws.custom_multicad_fname
        return False, '', groupBrws.custom_multicad_fname
