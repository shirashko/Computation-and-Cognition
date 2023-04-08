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
    "11": b'QlpoOTFBWSZTWSAmmmwAAox//////97fp3x3/P040r///3909mbAZ+4AAMEAZFJMIEhQQAL9opWpqSg1NNEpnqI2jSn6eqT0h+kj1H6ofqmmRo09AEGg9QDIDRoDQBoaaABmkDNqT9JBoimFT/RNU/TaNTJk0kZPRqDTQPUMgANAAAAAAGg0AAZD0gNqIMmCaZGEyMTTTATAmAEwmmAJiZMAAjEYARkaGCNMjTJpgSKRT00ZRk0BGhkyB6QAAGgAAAaAaBoAyBoAAGjI8poWMySflUKCGOchAcxBfNNUwtC6it2U7FnUCs7NpIGGaxG7Cqu2lSUtrSyV6mdNh91EOot48FX4lNIIWol7OYMufd2USFmmkpoQt7eAEEEygEGkRNGY0IGD/eWoDTWTx4Nt8/I8REfHDgQGhOynkcdYYHDHK6LSXmGDaRgo67TfgDENVZVb5BlXxnqkCS7R2q+RcrFSlPw+bN2/iMYWVlMkLR6EQGMBAQHzHyEHvaaDJ6qFMkeAcMlKWXLj/a1qxm3d7Yra6MLm0qEVSmQTYFR3huD2EtFllQoy38ZnS6sU1asLDmpSpTRTRIr6mrWI1cE5PZskpKeepUC64ffDzxnfzMbNzcIvthPxQEvb1IbNCALvTrY3UVivvWQDfllloW0ixXVr04g208JLbQCJ3PkSTyLLdFmU1XwcCWFwwds2yzHbmsoHg0QZV4h3SIePOVer8qTGKIsV8Nw4znXA0yIkbTPrJF5eXGn0JMZTxjEQsO7us3jYBHHonGXtLHiv8AmNYyb+5JnCwm1SlRb7cydFhAOEHBq0xwyxJMepTTIxKUw8Hf0CoZ7HfBPt1BmBlpRN6X6C8AxGPsB+IUcDN2+dhrfRUqwnQFiyisi0qiTbpLqkHN30rWM5qawcB5ht9Jl6KpXllcaA7WrkJ7OU3CrcKJYA/Mw0jlhApB8iUkzQZgfUaKVQpE5qWRjbLnuie04UTI1oY5vJsEdtyxqaFXUYLsaW7iB7tyj0ne2M6cmcrLMGly9Wcmuxz1SwAaMWuU4Cu63cMrWlQ6ZxBdrTlWMDETohbqJa6tCMfIkjI2NUQrRStUsMMGh4g4Tx6VdQcIFbFsD96eJaxzr2Y47/X/2s1mTCGtmzcEO0XH1SxY2cK06u7la2D34tQqOZmSW1qt2mTLrYqMebFIm7KoVzy4chP919NOe45AoUIwzS9aaRAioGzWZET+fv78PMKK+JYiVkokOMIatLz67m8qpcuCXfC+cVOzaXJGuudTyqV7xj/tA8binKu2ZBZdeXuMlKxhUBhFMUL8uwUVUCA3VQb1QRqY3/F3JFOFCQICaabA==',
    "9": b'QlpoOTFBWSZTWeKAZHcAAP7////+3U5AIXx1zPEI0q/v/zYM5CAAYCAAAKAAEBBIIAgQQAH3Jx2ddxCptT1GjQABo0ADQAMgyAAAANAA1NCZTyaAmmk9JpoNNAAADQAAAAYm1A1T00mak9JPCmnpGQyAD1AAZDQND1AAAB6g01Ig9FMeqY0MkZDARphAAaAAMAjQMkuF1KbqhUpSYOaRQoAkgfZXWqIyVWZpMVcDXwJ566KKpz7243mdgWJYY5CCAJKKADOXSSSnQchxAo9zZWkEQp9EIkVxZaoio58cROH5sKRsMWAO4V8P3HDwp17K32jYExX4bxwqvKN4Jzk4IQwxymtbWYIq07HW4iM44QjAGnCg5TnpqOU9aVYa4EQsh9cRfQVGTAo3s0y5RsvLM6NkADGfbVpZAcIgYjy6gREqTbdoI4Z9UG2fAADXuN+3yUua8GiXvOw7xN9gUqYFrosPys/CP35789ldCqoer9UUsQoHRA6GgzChI3pOwg1vT5mKnBaK4+/0HWjY4tBaKRiw/wwoh8VqyV9IyCBTARrLAcDU00vwOg9oY7ZkLU4L+cgt9BECOlwHgcQUH4tjCHhF4qFVsQoCF2S/GyxMqw8bGmAwVH3oWUtEs4ylXzTVSBzhIQa9fTGk8VxAPOd+kWZI5J7YS/S8J2ruOtTr0VjYLQrZClI6dExTxCWYymxOZrzn9EqWtBBsMqMElIsRhTdMMmRCL9MQEbJRQLR0vVygEUiDwTEIRHFGHkx5Px3ysaRztRUQARsOAwpchqIBwCkUZg1YpSRlTuNbNWwjXnY7IoQ1qrZTkP8XckU4UJDigGR3',
    "8": b'QlpoOTFBWSZTWXyuFF8AAPT/////Xk5AIXx1zPEK0q/v/zYM5CAAYCAAAKAAEBBIIAAQQAH3F1dnXYapqHqPUaDQAaAAAAAAAAAB6gAamgKeiehNNMptBGhoGgAAADQAA0yHqBqmyU80mkTyjT0jRoGjJoMgDJoANANNDQA9QYpFPJiantU09NTTQPUMjEAAAAABoBk0aI6KaOBQZQkB9pE58JAiO82Vi4DJXYhnXTa8BWkPNNNVTU1rTvxVhFMUJCQDKgGhAm4okkkeFey9AjNv+9F0CgjdRJgowp6cVovnaSt/VhhdGFGT0Cxb+5BMK9nNgxnFZGIy4XfH9uvHwcsu3sEQFilytjOElOakIY6zUY2Bxy8ImB4OW5Ta/IeSNgepgiFkP4BSiLAGVCeDDez5mVRsqYZ1RsADnUISDVsccQc1sC4QiJDLu5oR4sTwbdqgAGwck7O5ZnsMGCPynf8FqWcjygtSkoKjX+EjB0896wm+dwNN2Qxwi+Opr4rxmCEjes6aDY9fmVU2M0Uh9/oOjGx6rC0JCYsTuOJGHgOmTMZIgfFUCXTOEWBjF+Doh2eoaI6etIv5mD/RKCloQPAig1qY0B0HgGEq662MTiHDUxRNnkXOo1qQD7pPqgbQ8I5RkrxGkqkDnCQg2HElBQXUA8p3qBZihilygl+iZYlfpXXW5WXnxrq1FO8wxK/MymiNGNjoqNyKmLfw5YCas7a7RSNB9qOklkUKir5YcRriK4tnSqYnCGog7pCEAihiCkxXPjvja8RzwmhgKgyHGCXIZKAeASEZgyy1SR05t5EpY8prr5jI54ffZOtBD/F3JFOFCQfK4UXw',
    "7": b'QlpoOTFBWSZTWeZvDfMAAO9////+XG5AIXx13PEI06/v/zYM5CAAYCAACIBAABBIIAAQQAH3ExNIap6BNUwj1PJGR6hkxMCABkGCHoEwjTNNEephqYgEDU1T/VPQU9J6JpggxBhGCAA0wRoepmg4Gg0yGmjQwgZDQwRoaZNGgGQYgADQaaiEwmp5J5MUGhobKaAaAAAABoGmT1Gi9mpTfYHZlgUEqBlUQSymxhQuc6xbsUsNNsaAJ23XI1cty3J8xRCoIw+wAgSMhAL5R0kkpxe/qFpJv/ErADZTAQiOPOlrLGc9e2ybv1QpGBWfQDpFF2mASCeei07YWdETKXfTy/cDSeK7mmzTCHEUZGhbF4PySuVZ4ClVQWKQ8GQ0KWrE8RAd68wRVAhjEHVF/A2t0A5XTFT5BbXkK30gPfbAw5bYJQIO9y1Oc6M3Z6qHxGrSGqUt/oQB6uLtz/adCgoYzN7T24pJGkAu1aEjuV+kh/3uU3UPGjgPggJN9pxoXQ9EjR7pzgwbZvHdWKueCSX+4zKIhr/geQ0qKXihZlqQE2Yy13IBUZYhwd+oLiOTUwjOw/xMXqTuKknW2IIRUB2yDoinY5JSqzQ6xhZO+VJZSbxXv/JeKeJzFZJgddEGWQ2YC24aTcqs6ZLM0MIiunKa9QxXcccwxslZK5NIUZmCLdOnwTb5cDx6S8mTZWrCUfKREVy/qFTAmrWJsbDHXcRMfMgtQiZG6kJTVLRNjCweIVErRS+Mi0ZfKoWXkOqZCsSskGLlo/vlthEjOKPQAlYIIDXahkBQAbzRAh4+2SbrW3axTuWx2cWtkfLCpkNmydIvH/F3JFOFCQ5m8N8w',
    "6": b'QlpoOTFBWSZTWcULpkkAAOR////+XG5AIXx3zPEI0r///zYM5CAAACAAAMAAABBMIAAQQAH3DuOVsNTQjFQ/UZPUamZRkZAyNANANNA9TQAD1NGm1BqaCJgaaTGkmh6mhpoAAAaAAAAPUaaERqZMnqSYmnoAmjJkzQmBGIZMBGJggaMmBKKDQBEPU9TQAHpqNAAAaAAAeoyNAM/j8CQ5gSZ4jWA/CcIXDGon6HXXEliLtQMefAms0UIcS3WtT3ZxhMRzIgJMogVKkKqqqnF7VDaT7/vhOHmlxohVPlREikjV/LKJITcFrfEtMgHQU+t6sTlmzTRDjtraLDTb6eP3eYne3raLvk+KpYUdM8uEeDOyKiVUiaGz6Ih0YRscMDDUL+u6QpApikDxIt0ZK9APJVCj9ccY/EDRLAuAtoGUJaYbBasCDKUonFSDNrIO14DJjIWIAo13jHvF3qBQ8j0k4GUVPkemC3GJeG6/jJM2Vg1Y09Z2gTAgIsMDoMZSjsy20JUIhJAcvtRIwa8837WKeJYoD+cLEVJTSvJWdb6Q9fatfRiFxRsO9iCmOtPZB8mmzzS25PC29YhH3kFwTpcQkGYg1ekyzoOsWlT0lEVZOX5fxibc9t1RqpgP2B5S3tV4WAJwLOBoy3qzNoJJzoOEIN61nTeOGUnfwiNUrJWouiDCoPuXoaprSo1i8V2Syg85GaRnEKhN2SOkVYa9WtPTqMMaPRo6kAzTLUBJpncIlqKm6IiNcQ0VJQppLjBMRFMQjEi5ApMlz38ZWiOIiKxJpLBwA6RYNEE5CmAIyJfHxQUN07kNCShHd61v4zvBZWQV0u4v8XckU4UJDFC6ZJA=',
    "10": b'QlpoOTFBWSZTWdi7dyMAATr/////XE5AIXx3zPEI0r/v/zYM5CAAYCAAAMAAABBMIAAQQAH3azna7dhpE0hk0aZTR5qGiB6n6p6IyZGQYQAGJoaMCPUGpqaYahMTU9ogmJoAAABoAAAAGjQGqn4in6k1MmNI9Rmk0AZMIGINAYm1MgDQ0Mj1BikJonqep5NGptEAAMTQYgyYgAABo0yNP2G8+F4FogbERJQ4pYlCGClK4312DrxHAA6d5dFEL9bUzXfNGIZInTxkMBALyIA+0XkkkeT39Q0YuP4Y0XUcCJFKZYMmoEsflsxsmZRyQHJgId44MnPpnB4Q1qERjQxBKM5eOLA4fB1tN4XxLLFHo19kXxMy6G88/sX5qYYGg2MIfcDoglSKtWidOsQogIXBAyUlRraFo9DQyYWFMMhGcQBma0qanuiBsahSGtadFNvR0DiGdGEnrSAA5C4V4nFDhNQGANyXfmKO2OCnBDE1iB5rcxt+r92tAzAcgRtLDnvS8xQjA7JlQogMPL3JA4NqLJl0yi0XBPH7OFJ95ZRIFJWmGdclVu/YhWNVs6BJYd3F/4fZZqRe6qGJS9NwZ6wiEaNgwohpYsD5NnWO2EqdWKoX0S701+q/ZdZYpFycD7hNUh/xibBSMdl9FDiDzwfCxaNKFjKOG3jsxiBek646/CENRriXIVMZn70lMoWzccG7IOTSxzmRoitlMbEk3Pko458cwmlpQ68IiMt2FGspSUDik1g+kXU1xbefVSUkYKqmpOQjEskoU/Lds0zHATz0CWpAJCmpBsmIZAOgG4aIEOApmtFyKr9MtB9jXXyp6rk2ebRDIMUFVQ/xdyRThQkNi7dyMA=='
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