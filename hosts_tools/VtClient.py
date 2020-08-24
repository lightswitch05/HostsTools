from . import Client
from . import HostsTools
from collections import namedtuple
from typing import Set
import time


class VtResponse(namedtuple('VtResponse', 'subdomains siblings')):
    pass


class VtClient:
    api_key: str
    last_request_epoch: int

    def __init__(self, api_key):
        self.api_key = api_key
        self.last_request_epoch = -1

    def find_domains(self, domain: str, verbose: bool = False) -> VtResponse:
        results = VtResponse(set(), set())
        results.subdomains.add(domain)
        if not self.api_key or self.api_key == 'SET_ME':
            print('Missing VirusTotal API key, skipping lookup!')
            return results

        self._sleep()
        response = Client.safe_api_call('https://www.virustotal.com/vtapi/v2/domain/report', params={
            'apikey': self.api_key,
            'domain': domain
        })
        if 'subdomains' in response and response['subdomains']:
            subdomains = self._parse_domains(response['subdomains'], verbose)
            results.subdomains.update(subdomains)
        if 'domain_siblings' in response and response['domain_siblings']:
            siblings = self._parse_domains(response['domain_siblings'], verbose)
            results.siblings.update(siblings)
        return results

    def _parse_domains(self, domains, verbose: bool) -> Set[str]:
        results = set()
        for domain in domains:
            found_domain = HostsTools.normalize_domain(domain)
            if HostsTools.is_valid_domain(found_domain):
                if verbose:
                    print('Found: %s' % found_domain)
                results.add(found_domain)
        return results

    def _sleep(self) -> None:
        # free API is capped at 4 requests per minute
        now = int(time.time())
        if self.last_request_epoch < 0:
            self.last_request_epoch = now
            return
        time_left = 14.1 - (now - self.last_request_epoch)
        if time_left > 0:
            time.sleep(time_left)
        self.last_request_epoch = int(time.time())
