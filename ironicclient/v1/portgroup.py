# -*- coding: utf-8 -*-
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc

CREATION_ATTRIBUTES = ['node_uuid', 'name', 'address', 'extra']


class Portgroup(base.Resource):
    def __repr__(self):
        return "<PortGroup %s>" % self._info


class PortgroupManager(base.Manager):
    resource_class = Portgroup
    _resource_name = 'portgroups'

    @staticmethod
    def _path(id=None):
        return '/v1/portgroups/%s' % id if id else '/v1/portgroups'

    def list(self, node=None, address=None, limit=None, marker=None,
             sort_key=None, sort_dir=None, detail=False, fields=None):
        """Retrieve a list of port groups.

        :param node: Optional, UUID or name of a node, to get
                       the port groups for that node
        :param address: Optional, MAC address of a port, to get
                       the port group which has this MAC address
        :param marker: Optional, the UUID of a port group, eg the last
                       port group from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of port groups to return.
            2) limit == 0, return the entire list of port groups.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about ports groups.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :returns: A list of portgroups.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker, limit, sort_key, sort_dir,
                                       fields)
        if address is not None:
            filters.append('address=%s' % address)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "portgroups")
        else:
            return self._list_pagination(self._path(path), "portgroups",
                                         limit=limit)

    def get(self, portgroup_id, fields=None):
        if fields is not None:
            portgroup_id = '%s?fields=' % portgroup_id
            portgroup_id += ','.join(fields)

        try:
            return self._list(self._path(portgroup_id))[0]
        except IndexError:
            return None

    def get_by_address(self, address, fields=None):
        path = '?address=%s' % address
        if fields is not None:
            path += '&fields=' + ','.join(fields)
        else:
            path = 'detail' + path

        portgroups = self._list(self._path(path), 'portgroups')
        # get all the details of the port group assuming that
        # filtering by address returns a collection of one portgroup
        # if successful.
        if len(portgroups) == 1:
            return portgroups[0]
        else:
            raise exc.NotFound()

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exc.InvalidAttribute()
        return self._create(self._path(), new)

    def delete(self, portgroup_id):
        return self._delete(self._path(portgroup_id))

    def update(self, portgroup_id, patch):
        return self._update(self._path(portgroup_id), patch)
