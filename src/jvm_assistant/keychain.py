"""macOS Keychain via Security.framework: secrets never enter shell arguments."""
from __future__ import annotations
import ctypes as C
import json
import sys
from .common import UserError

SERVICE = "jvm-work-assistant.v1"

def framework():
    if sys.platform != "darwin":
        raise UserError("This package currently supports macOS only")
    sec = C.CDLL("/System/Library/Frameworks/Security.framework/Security")
    sec.SecKeychainFindGenericPassword.argtypes = [C.c_void_p,C.c_uint32,C.c_char_p,C.c_uint32,C.c_char_p,C.POINTER(C.c_uint32),C.POINTER(C.c_void_p),C.POINTER(C.c_void_p)]
    sec.SecKeychainFindGenericPassword.restype = C.c_int32
    sec.SecKeychainItemFreeContent.argtypes = [C.c_void_p,C.c_void_p]
    sec.SecKeychainItemFreeContent.restype = C.c_int32
    sec.SecKeychainAddGenericPassword.argtypes = [C.c_void_p,C.c_uint32,C.c_char_p,C.c_uint32,C.c_char_p,C.c_uint32,C.c_void_p,C.POINTER(C.c_void_p)]
    sec.SecKeychainAddGenericPassword.restype = C.c_int32
    sec.SecKeychainItemModifyAttributesAndData.argtypes = [C.c_void_p,C.c_void_p,C.c_uint32,C.c_void_p]
    sec.SecKeychainItemModifyAttributesAndData.restype = C.c_int32
    sec.SecKeychainItemDelete.argtypes = [C.c_void_p]
    sec.SecKeychainItemDelete.restype = C.c_int32
    cf = C.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    cf.CFRelease.argtypes = [C.c_void_p]
    return sec, cf

def find(account: str):
    sec, cf = framework()
    a, s = account.encode(), SERVICE.encode()
    length, data, item = C.c_uint32(), C.c_void_p(), C.c_void_p()
    code = sec.SecKeychainFindGenericPassword(None,len(s),s,len(a),a,C.byref(length),C.byref(data),C.byref(item))
    if code == -25300:
        return sec, cf, None, None
    if code != 0:
        raise UserError("Keychain access denied or unavailable; unlock it and try again")
    try:
        raw = C.string_at(data, length.value)
    finally:
        sec.SecKeychainItemFreeContent(None,data)
    return sec, cf, raw, item

def get(account: str) -> dict | None:
    sec, cf, raw, item = find(account)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    finally:
        cf.CFRelease(item)

def set_secret(account: str, value: dict):
    payload = json.dumps(value).encode()
    sec, cf, _, item = find(account)
    buffer = C.create_string_buffer(payload)
    try:
        if item:
            status = sec.SecKeychainItemModifyAttributesAndData(item,None,len(payload),buffer)
        else:
            a, s = account.encode(), SERVICE.encode()
            status = sec.SecKeychainAddGenericPassword(None,len(s),s,len(a),a,len(payload),buffer,None)
        if status != 0:
            raise UserError("Could not save credentials to Keychain")
    finally:
        if item:
            cf.CFRelease(item)

def delete(account: str):
    sec, cf, _, item = find(account)
    if item:
        try:
            if sec.SecKeychainItemDelete(item) != 0:
                raise UserError("Could not remove Keychain item")
        finally:
            cf.CFRelease(item)
