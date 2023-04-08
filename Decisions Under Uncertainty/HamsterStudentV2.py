import base64
import bz2
import importlib.machinery
import platform
import sys

LOADING_ERROR_MESSAGE = f"""Error loading Hamster module.
Please contact the course TA with the following information: {sys.version}"""


class SourcelessMemoryLoader(importlib.machinery.SourcelessFileLoader):
    def __init__(self, data: bytes, *args, **kwargs):
        self._data = data
        super().__init__(*args, **kwargs)

    def get_data(self, path) -> bytes:
        return self._data


version_to_code = {
    "11": b'QlpoOTFBWSZTWeEZjF0AAT9/9///v0nGKXmVzn0dUK7/3z50dFD4AagBgGRySiBIEEABvHO5JiKehKeiaeh6iehHlDTQD1PUBoAaDQAaBoAA9Q9Q0ZptU9qg1T0mqaeCeontU9TxNTeqaPUaGgAAA0AAAAAADQMgGqZqMU1HpGgNPSAMmmjRhDQMhiAyGg0AB6CZAA2oNNSJP0p6R6jJoekHqAGgAxGQ0AAZAABpoMCAGhur+rGzrNNIaKhXv/yuQW5DZRA6YBDTSocBmFMuaa1t0cexerEQJcCwcLCI4hAhlBVIQEA+yHUBG5Nn7bKD1IYb7mAiTSA8OPqF+zaipduv1B9hoOaCGHFU1uufb4iEoLereUtroMslLhwQIgZGYIZ8037iapKZBEyY4fDTy3ErJJSq/p7GOLsLhSEkrFIvxDCMKo0EpDr47yK1urxZ/rc2zFQ4DZNun/vxlTiRLqTxTyKNyAmcQSQmLhdaM9H7jYE60WYi3C86Dm8QCAWDpHEnM1QXdGqVvomtPQpoBrKBuv7VSQf+ETILEmXl6MU4CBmRb1K1mhTKM2APcHlzOv1rL6ThxMDbioxGPj2o/hpb53DYcosApgdpylopEuo2mTngzyq6EK7J9I4yUNLmKB7EhXMzCqlWzElC2Zogz7ofD/w7IO4wjqNJdFso4ijfaESIDuBuaaqE0pX7QeOciU1mTktFQKBRMKnC8hxBIYZkecroL7diiR7TVgRJNYjRCcoSyDFYAXVE0c1qesCnISCAERxTd3EgMoyb6TP4G5WKq4AgJd5hpgi+Rxp0QGLi/XdymAX+LuSKcKEhwjMYug==',
    "8": b'QlpoOTFBWSZTWdGsXlMAAIf/9//+XUBEKXyVyHEPVK7v3zYMAAA4YCAAgAAwSCAAEDABOaxoiaCQ0ZMyk21TanpPUyaDIaNDIG1BgI2o2nooRU8mJpqZGQ0DTQAAAAAAAAMgaIk8kxDRplDQ0aYaTR6gyPUyMmg0xPRNkjJUb3JjXuSBQaQS2lJgbcUySg7chvvKbIAmjAERmZRyI8DITGMZkF/fUJrHQecLLklnrdLgHGgl/nw8JnUS20PmZGoY1NGwXTEUDnGCggScF7GQYQ+7L24U0g6BoMCzJTJgU6QmJ6UJiZAbIoVMsI7ECcPKtgYDiveRPWN9B8TrZyQZHGspitNIHppGQ1PIn3Nc+56HYRFmKq6jmjPWdEoIkhr0jyoIi9gl328Rh3QMD8CVJ/r93v0KCBYhZFYg2/0NjuOqZ7nPasmBimOE4VQ0np6qXBsRcCwitxznDY42YowJwrMWouJkCxID4t2GjOGCbwuqZ40I99gFiBEmQo4RlWSIBDQ1zNAqNx11Ngp0wA4gIHIlEdxAcQKGm9USQWuxouHIX/F3JFOFCQ0axeUw',
    "6": b'QlpoOTFBWSZTWXN7rbcAAHp/9//6XUBEKXyVyHENVK7/3zYMAAA4ACAAgAAwSCAAEDABOaxhFPUyTRoyMJp6jTQAAAANAAGgekDVNqnmpqeponiBk0jTRkaYaEaGjATJkaGaTDTURopsp6mNQ2kGTAIGAQGBMAATSOSrjOS0fPQYIzF9jz7HUZBHpU7ELj4AR4onsSUualWj/AgbiLxQO6fUa508sTx3OsjpEPBQJcaxSRigVtcVCShJSu6XnRtQkG2QWgFIj+JJCD7flxqOFbCYYcSowluUhP0tS6LgDwR4hjrSiFi77xWWwtrQ3GH/6QhucdHX+PyLxEXx4M/IXiLxMiOslDtB+WMInvRVkrk8sYBArzi0Ir6SCWq0/9nYCD7bOHcH2C7vP1f8yE8wg2JhBRewoPsrPyRXLMbIB2TqoS2XE5EEVhVMEWnZJgdnUICh1WUIiMpi+YiMQzp2DCgC4qNQiKkHDe64bUSF4nhNSKdehUELlFLAyInTiDhScuTbyltgLQIAofLX/19k81urfaQyMyv+pcxdyRThQkHN7rbc',
    "10": b'QlpoOTFBWSZTWcZdrb8AALl/9//+HVBAKXiVyHENVK7v3zYMAAA4YCAAgAAwSCAAEDABNpiEU9U9qKNlPKeNRp6ptMp6ExGEGAjBGBpPRqfooNTQyJoUeTRNG1AAND1PUPUAaADIA9INFIMgDQANGgAAZMgAABtQELbEtNUka7pB8HMvRypEpGzbO1XQ6NQCnEAN8iJVmNfGZBBjOZBPpbCF6Z8QmS2Bx+oqUwLpAeNsgIVScsKOpRmRMRN2fuL2aHEHkF/xfcGGwZ1EVbTpdBcEEdBo4G/3as4MWyqICRSsKRYzZWsJDowWGGnwOyNOoZUuBsu2WS/2Q7RB+XUH1vHUaq7rbijmnarCKcLDSt6Eu4BAvt9pYpFVFbV6T+h+DDK8kOYSOlt6XXJzh4oEHhQILuea49SPK3cKq8YEnSyp4Hf7G5mHWRpQU0BBDFMQRsrmoDUdL2QVCiiCaogVAcFiksZow/frNkRVJP5ZxK0X9a7gGhJebAQpXMlIkX4W4XTm9wDyDR5qy6uuY0RQT5oriiSpF8POv/F3JFOFCQxl2tvw',
    "9": b'QlpoOTFBWSZTWblfw9MAAJP/9//+XUBEKXyVyHENVK7v3zYMAAA4YCAAgAAwSCAAEDABOEaGqehNUzBTT2kbSnqeU09QNBiAaGNQDQNHqb0UGqmT1M1NPSMg0HqAAA00GgaAAABoGhAmIo00eUNNBoaA0GmmmmjQANqDahorxyqvuyqAmghJBiqItbMTRW3N27XbEgCgYA4jMyv0peMhUY6zIOx8IqtbJ+gcWpke7RLVGmhO+fDPFVZMltJzMje1u9DvPHgYJJEDzCv06kWgo+HzxutdZOKRYJ1sJTXgSoxT1qXaYIkVxsh8axgsXpBK3zpVcH9NOGWzpo7JYdxix90jv0FSe1kh8D0fNdkEpEzodgb4L6HgQRTLAlE7cgIJ3uPTqn5zkupbB9DTEjy/NSrLoekIRlIQcwVKM6hX9cwI2bxwxTHmpFS60FbsL5RTXViafcrQKn3DmjNDQtBra5mRrJobBORJO+cde6xknh0C4VwqQR58WUJJoxFAodFZI4Mj9ddTXfFTAKgCDQ1ZfobG0FFauW4STiSbHkN/i7kinChIXK/h6YA=',
    "7": b'QlpoOTFBWSZTWdCM1OoAAIJ/9//6XUBEKXyV2HENVK7v3zYMAAA4YCAAgAAwSCAAEDABONixFPQinqeU8htJPZU9T0T0mmagADIbQQyYnoxooNU0aGphGRkDQAAAAAAA0ANA00g1DVNHqPSABoDQDQNAAAaBtQ0YssDrrYHAWDQQtEHY8oxsJHDp1rfA+MkASggDdJKXfZeIoKyOkoGvbQrtaR8wyZt+dslM8ZaglvnvqFdK32WyShWELc/cbxeGZRMQ79NavUWfieqi5FswyWUA56LCYBU9HKUqBaJQqDlSBIxLKAxRbxgjndUVH660EZ5HW9CymogJolD30jKVn2eylj2VVuwskIrwbdX7eYzgCBpYbDBpl0gIMY+uam54lGdCg2hMc2jdS9W+ESRCAUiDUk5yNmPRZkNycZQUdXEsk8PA7U284L8VtARXI6jBO40UkBHryDE4URKgQKwWhafYQXQHXuwskc4Q2BkLlESY1HEZZsqgUcPYScCx/155NlEyYBiHj0T+tacBnCozUz4xjvRW5yr/i7kinChIaEZqdQA='
}

versions = platform.python_version().split('.')
assert versions[0] == '3', LOADING_ERROR_MESSAGE

minor_version = versions[1]

assert minor_version in version_to_code, LOADING_ERROR_MESSAGE

try:
    data = version_to_code[minor_version]
    data = base64.b64decode(data)
    data = bz2.decompress(data)
    loader = SourcelessMemoryLoader(data=data, path="Hamster", fullname="Hamster")
    Hamster = loader.load_module("Hamster")

    myHamster = Hamster.myHamster
except Exception as e:
    raise ImportError(LOADING_ERROR_MESSAGE) from e