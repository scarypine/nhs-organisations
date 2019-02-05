import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Organisation, Region

_REGIONS_URL = 'https://improvement.nhs.uk/regions.json/'
_URL = 'https://improvement.nhs.uk/organisations.json'


class Command(BaseCommand):
    help = (
        "Update local Organisations to reflect the data from {}. "
        "Organisations may change or close over time, but should never be "
        "deleted once created."
        .format(_URL)
    )

    @transaction.atomic
    def handle(self, **kwargs):
        print('----------------------------------------------------------')
        print('Refreshing region data')
        print('----------------------------------------------------------')
        self.refresh_region_data(**kwargs)

        print('----------------------------------------------------------')
        print('Refreshing organisation data')
        print('----------------------------------------------------------')
        self.refresh_organisation_data(**kwargs)

    def refresh_region_data(self, **kwargs):
        self.regions_by_id = {}
        self.regions_by_code = {}

        print('Fetching region data...')
        try:
            response = requests.get(_REGIONS_URL)
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print("regions.json is not live yet, so skipping for now\n\n")
                for obj in Region.objects.all():
                    self.regions_by_id[obj.id] = obj
                    self.regions_by_code[obj.code] = obj
                return
            raise e

        region_list = response.json()
        print('Updating region data...')
        for r in region_list:
            obj, created = Region.objects.update_or_create(
                id=r['id'],
                defaults=dict(
                    code=r['code'],
                    name=r['name'],
                    is_active=r['is_active']
                ),
            )
            self.regions_by_id[str(obj.id)] = obj
            self.regions_by_code[obj.code] = obj
            if created:
                print("Added new region: %r" % obj)
            else:
                print("Updated existing region: %r" % obj)

        print('Setting region predecessor values...')
        for r in region_list:
            obj = self.regions_by_id[r['id']]
            predecessor_regions = [
                self.regions_by_id[pid] for pid in r['predecessor_ids']
                if pid in self.regions_by_id
            ]
            print('Setting predecessors for %r to:\n%r' % (obj, predecessor_regions))
            obj.predecessors.set(predecessor_regions)

        print('Done!\n\n')

    def refresh_organisation_data(self, **kwargs):
        print('Fetching organisation data...')
        response = requests.get(_URL)
        response.raise_for_status()

        existing_orgs = Organisation.objects.as_dict(keyed_by='code')
        successor_orgs_to_set = {}
        orgs_to_create = []

        print('Updating organisation data...')
        for org_code, org_details in response.json().items():
            org_details = self.prepare_organisation_data(org_details)
            print('----------------------------------------------------------')
            print("%s (%s)" % (org_details['name'], org_code))

            successor_code = org_details.pop('successor_org_code')
            if successor_code is not None:
                successor_orgs_to_set[org_code] = successor_code

            if org_code in existing_orgs:
                print("Updating local copy")
                obj = existing_orgs[org_code]
                for key, val in org_details.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                print("Creating a local copy")
                org_details['code'] = org_code
                orgs_to_create.append(Organisation(**org_details))
        if orgs_to_create:
            print('----------------------------------------------------------')
            print("Saving %s new organisations..." % len(orgs_to_create))
            Organisation.objects.bulk_create(orgs_to_create)
        if successor_orgs_to_set:
            print('----------------------------------------------------------')
            print("Setting successor organisations for merged orgs...")
            successor_org_codes = successor_orgs_to_set.values()
            succeeded_org_codes = successor_orgs_to_set.keys()
            successor_orgs_dict = Organisation.objects.filter(code__in=successor_org_codes).as_dict(keyed_by='code')
            for org in Organisation.objects.filter(code__in=succeeded_org_codes):
                successor_code = successor_orgs_to_set[org.code]
                successor_org = successor_orgs_dict.get(successor_code)
                if successor_org:
                    org.successor_id = successor_org.id
                    org.save()
        print('----------------------------------------------------------')
        print('Done!\n\n')

    def prepare_organisation_data(self, org_details):
        try:
            successor_org_code = org_details['successor_organisation']['code']
        except (KeyError, TypeError):
            successor_org_code = None

        region_details = org_details.pop('region', None)
        if region_details:
            try:
                region_new = self.regions_by_id.get(region_details['id'])
            except KeyError:
                region_new = self.regions_by_code.get(region_details['code'])
            region = ''
        else:
            region_new = None
            region = ''

        return {
            'name': org_details['name'],
            'organisation_type': org_details['organisation_type']['code'],
            'region': region,
            'region_new': region_new,
            'closure_date': org_details['closure_date'],
            'created_at': org_details['created_at'],
            'last_updated_at': org_details['last_updated_at'],
            'successor_org_code': successor_org_code,
        }
