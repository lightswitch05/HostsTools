import re
from typing import List, Set, Pattern

STRIP_COMMENTS_PATTERN = re.compile(r"^([^#]+)")
ALLOWED_DOMAIN_PATTERN = re.compile(r"^[^\*\?\[\]{}\|\\/&^%$\(\)#@!+=~`\s\.<>,\"']+$", re.IGNORECASE)
EXCLUDE_DOMAIN_PATTERN = re.compile(r"^[-]", re.IGNORECASE)


class HostsTools:
    @staticmethod
    def sort_domains(domains: List[str]) -> List[str]:
        sorted_list = []
        for domain in domains:
            d = HostsTools.normalize_domain(domain).split('.')
            d.reverse()
            sorted_list.append(d)
        sorted_list.sort()
        for index, domain_parts in enumerate(sorted_list):
            domain_parts.reverse()
            sorted_list[index] = '.'.join(domain_parts)
        return sorted_list

    @staticmethod
    def extract_domain(domain_entry: str) -> str:
        # First strip any comments
        match = STRIP_COMMENTS_PATTERN.match(domain_entry)
        if match and match.group(0):
            entry_parts = match.group(0).split()
            for index, part in enumerate(entry_parts):
                # normalize each part
                entry_parts[index] = HostsTools.normalize_domain(part)
            if len(entry_parts) == 2 and HostsTools.is_valid_domain(entry_parts[1]):
                # At least one character was found that was not after a comment.
                # Split it on whitespace, if the parts found is exactly 2
                # then we can assume its a valid host entry
                return entry_parts[1]
            elif len(entry_parts) == 1 and HostsTools.is_valid_domain(entry_parts[0]):
                # If there is only one part... still try to treat it as valid
                return entry_parts[0]
        return ''

    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        if not domain or len(domain) > 255:
            return False
        if domain[-1] == ".":
            domain = domain[:-1]  # strip exactly one dot from the right, if present
        return all(ALLOWED_DOMAIN_PATTERN.match(x) and not EXCLUDE_DOMAIN_PATTERN.match(x) for x in domain.split("."))

    @staticmethod
    def reduce_domains(domains: Set[str]) -> Set[str]:
        reduced_domains = set()
        for domain in domains:
            domain_parts = domain.split('.')
            domain_parts.reverse()
            minimum_domain = None
            for domain_part in domain_parts:
                if not minimum_domain:
                    minimum_domain = domain_part
                else:
                    minimum_domain = domain_part + '.' + minimum_domain
                if minimum_domain in domains:
                    reduced_domains.add(minimum_domain)
                    break
        print('Reduced query list from %s to %s' % (len(domains), len(reduced_domains)))
        return reduced_domains

    @staticmethod
    def load_domains_from_list(file_name: str) -> Set[str]:
        domains = set()
        with open(file_name) as file:
            lines = file.readlines()
        for line in lines:
            domain = HostsTools.extract_domain(line)
            if domain:
                domains.add(domain)
        return domains

    @staticmethod
    def filter_whitelist(domains: Set[str], whitelist: Set[Pattern] = {}) -> Set[str]:
        filtered = set(domains)
        for domain in domains:
            for pattern in whitelist:
                if domain in filtered and pattern.match(domain):
                    filtered.remove(domain)
                    print("whitelisted: %s" % domain)
            if len(domain) > 2 and len(domain) % 2 == 0:
                half = len(domain) // 2
                first = domain[:half]
                second = domain[half:]
                if first == second and domain in filtered:
                    filtered.remove(domain)
                    print("whitelisted: %s" % domain)
        return filtered

    @staticmethod
    def normalize_domain(domain: str) -> str:
        if domain:
            domain = domain.strip().lower()
        return domain
