from hosts_tools import HostsTools
import re


class TestHostsTools(object):

    TEST_FILE_NAME = './tests/test-list.txt'
    TEST_DOMAINS = {'a.com', 'b.a.com', 'b.com', 'a.b.com'}
    TEST_WHITELIST = {
        re.compile('^b\\.b\\.com$', re.IGNORECASE),
        re.compile('^z\\.com$', re.IGNORECASE)
    }

    def test_none_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain(None)
        assert not is_valid

    def test_empty_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("")
        assert not is_valid

    def test_wildcard_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("*.example.com")
        assert not is_valid

    def test_percent_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("%example.com")
        assert not is_valid

    def test_double_quote_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("\"example.com")
        assert not is_valid

    def test_single_quote_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("'example.com")
        assert not is_valid

    def test_left_paren_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("(example.com")
        assert not is_valid

    def test_right_paren_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain(")example.com")
        assert not is_valid

    def test_colon_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("v:443.example.com")
        assert not is_valid

    def test_simi_colon_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("v;443.example.com")
        assert not is_valid

    def test_unicode_is_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain(u"www.с\ud0b0.com")
        assert is_valid

    def test_too_long_is_not_a_valid_domain(self):
        domain = ("a" * 255) + ".com"
        is_valid = HostsTools.is_valid_domain(domain)
        assert not is_valid

    def test_long_is_a_valid_domain(self):
        domain = "a" * 251 + ".com"
        is_valid = HostsTools.is_valid_domain(domain)
        assert is_valid

    def test_naked_is_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("example.com")
        assert is_valid

    def test_www_is_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("www.example.com")
        assert is_valid

    def test_trailing_dot_is_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("www.example.com.")
        assert is_valid

    def test_leading_dash_is_not_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("-example.com")
        assert not is_valid

    def test_middle_dash_is_a_valid_domain(self):
        is_valid = HostsTools.is_valid_domain("my-example.com")
        assert is_valid

    def test_extract_basic(self):
        extracted = HostsTools.extract_domain("0.0.0.0 example.com")
        assert extracted == "example.com"

    def test_extract_different_ip(self):
        extracted = HostsTools.extract_domain("127.0.0.1 example.com")
        assert extracted == "example.com"

    def test_extract_no_ip(self):
        extracted = HostsTools.extract_domain("example.com")
        assert extracted == "example.com"

    def test_extract_trailing_comment(self):
        extracted = HostsTools.extract_domain("0.0.0.0 example.com # comment")
        assert extracted == "example.com"

    def test_extract_empty_line(self):
        extracted = HostsTools.extract_domain("")
        assert extracted == ""

    def test_extract_only_comment(self):
        extracted = HostsTools.extract_domain("# comment")
        assert extracted == ""

    def test_extract_commented_out_entry(self):
        extracted = HostsTools.extract_domain("# 0.0.0.0 example.com")
        assert extracted == ""

    def test_sort_root_domains(self):
        domains = ["y.a", "z.a", "x.a", "c.z", "b.z", "a.z"]
        sorted = HostsTools.sort_domains(domains)
        assert sorted == ["x.a", "y.a", "z.a", "a.z", "b.z", "c.z"]

    def test_sort_sub_domains(self):
        domains = ["b.y.a", "a.y.a", "y.a", "c.z", "b.a.z", "a.z"]
        sorted = HostsTools.sort_domains(domains)
        assert sorted == ["y.a", "a.y.a", "b.y.a", "a.z", "b.a.z", "c.z"]

    def test_reduce_domains(self):
        reduced = HostsTools.reduce_domains(self.TEST_DOMAINS)
        assert reduced
        assert not {'a.com', 'b.com'}.difference(reduced)

    def test_reduce_domains_empty(self):
        reduced = HostsTools.reduce_domains(set())
        assert not set().difference(reduced)

    def test_domain_is_whitelisted(self):
        domains = {
            'b.com',
            'b.b.com',
            'ad.example.com'
        }
        filtered = HostsTools.filter_whitelist(domains, self.TEST_WHITELIST)
        assert filtered == {'b.com', 'ad.example.com'}

    def test_duplicated_domain_is_whitelisted(self):
        domains = {
            'example.com',
            'ad.example.comad.example.com',
            'ad.example.com'
        }
        filtered = HostsTools.filter_whitelist(domains, set())
        assert filtered == {'example.com', 'ad.example.com'}

    def test_read_domains_list(self):
        domains = HostsTools.load_domains_from_list(self.TEST_FILE_NAME)
        assert domains
        assert len(domains) == 6

    def test_normalize_domain_simple(self):
        normalized = HostsTools.normalize_domain('   eXaMple.com   ')
        assert normalized == 'example.com'

    def test_normalize_domain_none(self):
        normalized = HostsTools.normalize_domain(None)
        assert normalized == normalized

    def test_normalize_domain_tab(self):
        normalized = HostsTools.normalize_domain(" \t example.com \t\t ")
        assert normalized == 'example.com'
