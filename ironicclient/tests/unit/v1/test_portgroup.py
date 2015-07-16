# Copyright 2015 SAP Ltd.
# All Rights Reserved.
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

import copy

import testtools
from testtools.matchers import HasLength

from ironicclient.tests.unit import utils
import ironicclient.v1.portgroup

PORTGROUP = {'id': 987,
             'uuid': '11111111-2222-3333-4444-555555555555',
             'name': 'Port name',
             'node_uuid': 12,
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}

PORTGROUP2 = {'id': 988,
              'uuid': '55555555-4444-3333-2222-111111111111',
              'name': 'Port2 name',
              'node_uuid': 103,
              'address': 'AA:AA:AA:BB:BB:BB',
              'extra': {}}

CREATE_PORTGROUP = copy.deepcopy(PORTGROUP)
del CREATE_PORTGROUP['id']
del CREATE_PORTGROUP['uuid']

UPDATED_PORTGROUP = copy.deepcopy(PORTGROUP)
NEW_ADDR = 'AA:AA:AA:AA:AA:AA'
UPDATED_PORTGROUP['address'] = NEW_ADDR

fake_responses = {
    '/v1/portgroups':
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
        'POST': (
            {},
            CREATE_PORTGROUP,
        ),
    },
    '/v1/portgroups/detail':
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/portgroups/%s' % PORTGROUP['uuid']:
    {
        'GET': (
            {},
            PORTGROUP,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_PORTGROUP,
        ),
    },
    '/v1/portgroups/detail?address=%s' % PORTGROUP['address']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/portgroups/?address=%s' % PORTGROUP['address']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    }
}

fake_responses_pagination = {
    '/v1/portgroups':
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP],
             "next": "http://127.0.0.1:6385/v1/portgroups/?limit=1"}
        ),
    },
    '/v1/portgroups/?limit=1':
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP2]}
        ),
    },
    '/v1/portgroups/?marker=%s' % PORTGROUP['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/portgroups/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP2, PORTGROUP]}
        ),
    },
    '/v1/portgroups/?sort_dir=desc':
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP2, PORTGROUP]}
        ),
    },
}


class PortgroupManagerTest(testtools.TestCase):

    def setUp(self):
        super(PortgroupManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.portgroup.PortgroupManager(self.api)

    def test_portgroups_list(self):
        portgroups = self.mgr.list()
        expect = [
            ('GET', '/v1/portgroups', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(portgroups))

    def test_portgroups_list_by_address(self):
        portgroups = self.mgr.list(address=PORTGROUP['address'])
        expect = [
            ('GET', '/v1/portgroups/?address=%s' % PORTGROUP['address'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(portgroups))

    def test_portgroups_list_by_address_detail(self):
        portgroups = self.mgr.list(address=PORTGROUP['address'], detail=True)
        expect = [
            ('GET', '/v1/portgroups/detail?address=%s' % PORTGROUP['address'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(portgroups))

    def test_portgroups_list_detail(self):
        portgroups = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/portgroups/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(portgroups))

    def test_portgroups_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.portgroup.PortgroupManager(self.api)
        portgroups = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/portgroups/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(portgroups, HasLength(1))

    def test_portgroups_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.portgroup.PortgroupManager(self.api)
        portgroups = self.mgr.list(marker=PORTGROUP['uuid'])
        expect = [
            ('GET', '/v1/portgroups/?marker=%s' % PORTGROUP['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(portgroups, HasLength(1))

    def test_portgroups_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.portgroup.PortgroupManager(self.api)
        portgroups = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/portgroups', {}, None),
            ('GET', '/v1/portgroups/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(portgroups, HasLength(2))

    def test_portgroups_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.portgroup.PortgroupManager(self.api)
        portgroups = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/portgroups/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(portgroups))

    def test_portgroups_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.portgroup.PortgroupManager(self.api)
        ports = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/portgroups/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(ports))

    def test_portgroups_show(self):
        portgroup = self.mgr.get(PORTGROUP['uuid'])
        expect = [
            ('GET', '/v1/portgroups/%s' % PORTGROUP['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(PORTGROUP['uuid'], portgroup.uuid)
        self.assertEqual(PORTGROUP['name'], portgroup.name)
        self.assertEqual(PORTGROUP['node_uuid'], portgroup.node_uuid)
        self.assertEqual(PORTGROUP['address'], portgroup.address)

    def test_portgroups_show_by_address(self):
        portgroup = self.mgr.get_by_address(PORTGROUP['address'])
        expect = [
            ('GET', '/v1/portgroups/detail?address=%s' % PORTGROUP['address'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(PORTGROUP['uuid'], portgroup.uuid)
        self.assertEqual(PORTGROUP['name'], portgroup.name)
        self.assertEqual(PORTGROUP['node_uuid'], portgroup.node_uuid)
        self.assertEqual(PORTGROUP['address'], portgroup.address)

    def test_create(self):
        portgroup = self.mgr.create(**CREATE_PORTGROUP)
        expect = [
            ('POST', '/v1/portgroups', {}, CREATE_PORTGROUP),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(portgroup)

    def test_delete(self):
        portgroup = self.mgr.delete(portgroup_id=PORTGROUP['uuid'])
        expect = [
            ('DELETE', '/v1/portgroups/%s' % PORTGROUP['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(portgroup)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_ADDR,
                 'path': '/address'}

        portgroup = self.mgr.update(portgroup_id=PORTGROUP['uuid'],
                                    patch=patch)
        expect = [
            ('PATCH', '/v1/portgroups/%s' % PORTGROUP['uuid'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_ADDR, portgroup.address)
