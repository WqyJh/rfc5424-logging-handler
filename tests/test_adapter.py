import logging

import pytest
from mock import patch

from conftest import (
    address, message, sd1, sd2
)
from rfc5424logging import Rfc5424SysLogHandler, Rfc5424SysLogAdapter, NOTICE, NILVALUE


@pytest.mark.parametrize("handler_kwargs,adapter_kwargs,logger_kwargs,expected", [
    (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {},
        {'extra': {'structured_data': sd2, 'msgid': 'my_msgid'}},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname my_appname 1234'
        b' my_msgid [my_sd_id1@32473 my_key1="my_value1"][my_sd_id2@32473 my_key2="my_value2"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'enable_extra_levels': True},
        {'extra': {'structured_data': sd2, 'msgid': 'my_msgid'}},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname my_appname 1234'
        b' my_msgid [my_sd_id1@32473 my_key1="my_value1"][my_sd_id2@32473 my_key2="my_value2"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'extra': {'structured_data': sd2, 'msgid': 'my_msgid'}},
        {},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname my_appname 1234'
        b' my_msgid [my_sd_id1@32473 my_key1="my_value1"][my_sd_id2@32473 my_key2="my_value2"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'extra': {'structured_data': sd2, 'msgid': 'my_msgid'}, 'enable_extra_levels': True},
        {},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname my_appname 1234'
        b' my_msgid [my_sd_id1@32473 my_key1="my_value1"][my_sd_id2@32473 my_key2="my_value2"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'enable_extra_levels': True},
        {'structured_data': sd2, 'msgid': 'my_msgid'},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname my_appname 1234'
        b' my_msgid [my_sd_id1@32473 my_key1="my_value1"][my_sd_id2@32473 my_key2="my_value2"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'enable_extra_levels': True},
        {'procid': 'some_procid'},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname my_appname some_procid'
        b' - [my_sd_id1@32473 my_key1="my_value1"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'enable_extra_levels': True},
        {'appname': 'some_appname'},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 my-hostname some_appname 1234'
        b' - [my_sd_id1@32473 my_key1="my_value1"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address, 'structured_data': sd1, 'appname': 'my_appname', 'hostname': 'my-hostname', 'procid': "1234"},
        {'enable_extra_levels': True},
        {'hostname': 'some-hostname'},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 some-hostname my_appname 1234'
        b' - [my_sd_id1@32473 my_key1="my_value1"] '
        b'\xef\xbb\xbfThis is an interesting message'
    ), (
        {'address': address},
        {'enable_extra_levels': True},
        {'hostname': NILVALUE, 'appname': NILVALUE, 'procid': NILVALUE},
        b'<14>1 2000-01-01T17:11:11.111111+06:00 - - - - - '
        b'\xef\xbb\xbfThis is an interesting message'
    )
])
def test_adapter(logger, handler_kwargs, adapter_kwargs, logger_kwargs, expected):

    sh = Rfc5424SysLogHandler(**handler_kwargs)
    logger.addHandler(sh)
    adapter = Rfc5424SysLogAdapter(logger, **adapter_kwargs)
    with patch.object(sh.transport, 'socket') as syslog_socket:
        adapter.info(message, **logger_kwargs)
        syslog_socket.sendto.assert_called_once_with(expected, address)
        syslog_socket.sendto.reset_mock()

        adapter.log(logging.INFO, message, **logger_kwargs)
        syslog_socket.sendto.assert_called_once_with(expected, address)
        syslog_socket.sendto.reset_mock()
    logger.removeHandler(sh)


def test_log(logger_with_udp_handler):
    expected_msg = (b'<13>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    logger, syslog_socket = logger_with_udp_handler
    adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True)
    adapter.log(NOTICE, message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_log_not_enabled(adapter_with_udp_handler):
    expected_msg = (b'<12>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    adapter, syslog_socket = adapter_with_udp_handler
    adapter.log(NOTICE, message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_emergency(logger_with_udp_handler):
    expected_msg = (b'<8>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    logger, syslog_socket = logger_with_udp_handler
    adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True)
    adapter.emerg(message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_emergency_not_enabled(adapter_with_udp_handler):
    expected_msg = (b'<10>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    adapter, syslog_socket = adapter_with_udp_handler
    adapter.emergency(message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_alert(logger_with_udp_handler):
    expected_msg = (b'<9>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    logger, syslog_socket = logger_with_udp_handler
    adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True)
    adapter.alert(message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_alert_not_enabled(adapter_with_udp_handler):
    expected_msg = (b'<10>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    adapter, syslog_socket = adapter_with_udp_handler
    adapter.alert(message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_notice(logger_with_udp_handler):
    expected_msg = (b'<13>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    logger, syslog_socket = logger_with_udp_handler
    adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True)
    adapter.notice(message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_notice_not_enabled(adapter_with_udp_handler):
    expected_msg = (b'<12>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111'
                    b' - - \xef\xbb\xbfThis is an interesting message')
    adapter, syslog_socket = adapter_with_udp_handler
    adapter.notice(message)
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_empty_msg(logger_with_udp_handler):
    logger, syslog_socket = logger_with_udp_handler
    adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True)

    expected_msg = b'<15>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.debug()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<14>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.info()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<13>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.notice()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<12>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.warning()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<11>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.error()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<10>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.critical()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<9>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.alert()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)
    syslog_socket.sendto.reset_mock()

    expected_msg = b'<8>1 2000-01-01T17:11:11.111111+06:00 testhostname root 111 - -'
    adapter.emergency()
    syslog_socket.sendto.assert_called_once_with(expected_msg, address)


def test_extras(logger_with_udp_handler):
    logger, syslog_socket = logger_with_udp_handler
    adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True, extra={"a": 1, "c": 3})
    expected_return = ("aaaa", {'extra': dict(a=1, b=2, c="c")})
    # Make sure passed extra argument overrides that of the adapter instance
    assert adapter.process("aaaa", kwargs={'extra': {"b": 2, "c": "c"}}) == expected_return
    # Make sure adapter instance variables aren't overwritten
    assert {"a": 1, "c": 3} == adapter.extra
    # Test invalid extra argument
    with pytest.raises(TypeError):
        adapter = Rfc5424SysLogAdapter(logger, enable_extra_levels=True, extra="i_am_not_a_dict")
