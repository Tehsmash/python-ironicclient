# Copyright 2015 SAP Ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import mock

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common import utils as commonutils
from ironicclient.tests.unit import utils
import ironicclient.v1.portgroup_shell as pg_shell


class PortgroupShellTest(utils.BaseTestCase):

    def test_portgroup_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            portgroup = object()
            pg_shell._print_portgroup_show(portgroup)
        exp = ['address', 'created_at', 'extra', 'node_uuid', 'updated_at',
               'uuid', 'name']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_portgroup_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = 'portgroup_uuid'
        args.address = False
        args.fields = None

        pg_shell.do_portgroup_show(client_mock, args)
        client_mock.portgroup.get.assert_called_once_with('portgroup_uuid',
                                                          fields=None)
        # assert get_by_address() wasn't called
        self.assertFalse(client_mock.portgroup.get_by_address.called)

    def test_do_portgroup_show_space_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = '   '
        args.address = False
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_show,
                          client_mock, args)

    def test_do_portgroup_show_empty_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = ''
        args.address = False
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_show,
                          client_mock, args)

    def test_do_portgroup_show_by_address(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = 'portgroup_address'
        args.address = True
        args.fields = None

        pg_shell.do_portgroup_show(client_mock, args)
        client_mock.portgroup.get_by_address.assert_called_once_with(
            'portgroup_address', fields=None)
        # assert get() wasn't called
        self.assertFalse(client_mock.portgroup.get.called)

    def test_do_portgroup_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = 'portgroup_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        pg_shell.do_portgroup_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.portgroup.update.assert_called_once_with('portgroup_uuid',
                                                             patch)

    def _get_client_mock_args(self, address=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None):
        args = mock.MagicMock(spec=True)
        args.address = address
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail
        args.fields = fields

        return args

    def test_do_portgroup_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(detail=False)

    def test_do_portgroup_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(detail=True)

    def test_do_portgroup_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=False)

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(sort_key='uuid',
                                                           detail=False)

    def test_do_portgroup_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid',
                                          detail=False)

        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list.called)

    def test_do_portgroup_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=True)

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(sort_key='uuid',
                                                           detail=True)

    def test_do_portgroup_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list.called)

    def test_do_portgroup_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        pg_shell.do_portgroup_create(client_mock, args)
        client_mock.portgroup.create.assert_called_once_with()

    def test_do_portgroup_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = ['portgroup_uuid']
        pg_shell.do_portgroup_delete(client_mock, args)
        client_mock.portgroup.delete.assert_called_once_with('portgroup_uuid')
