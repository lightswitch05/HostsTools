from . import Client
from . import HostsTools
from typing import Set


def find_subdomains(domain: str, verbose: bool = False) -> Set[str]:
    found_domains = {domain}  # include query as a found domain
    url = 'https://crt.sh/?q=%.{d}&output=json'.format(d=domain)
    response = Client.safe_api_call(url)
    for key, value in enumerate(response):
        if 'name_value' in value:
            found_domain = value['name_value'].lower().strip()
            if verbose:
                print('Found: %s' % found_domain)
            if found_domain.startswith('*.'):
                found_domain = found_domain[2:]
            if HostsTools.is_valid_domain(found_domain):
                found_domains.add(found_domain)
    return found_domains
