# -----------------------------------------------------------
# Copyright (C) 2021 Venceslas Roullier/Opendatasoft
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
# ---------------------------------------------------------------------

from . import qgis_ods_plugin


# noinspection PyPep8Naming
def classFactory(iface):
    return qgis_ods_plugin.QgisOdsPlugin(iface)
