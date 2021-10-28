# -----------------------------------------------------------
# Copyright (C) 2021 Venceslas Roullier/Opendatasoft
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License.
# ---------------------------------------------------------------------

from . import qgis_ods_plugin

def classFactory(iface):
    return qgis_ods_plugin.QgisOdsPlugin(iface)
