class meta(type):
    def __getattr__(cls, item):
        t = TermCol()
        rv = t.__getattr__(item)
        del t
        return rv


class TermCol(metaclass=meta):
    __black = 90
    __red = 91
    __green = 92
    __yellow = 93
    __blue = 94
    __magenta = 95
    __cyan = 96
    __white = 97

    __color_mapping = {
        # long codes
        "BLACK": __black,
        "RED": __red,
        "GREEN": __green,
        "YELLOW": __yellow,
        "BLUE": __blue,
        "MAGENTA": __magenta,
        "CYAN": __cyan,
        "WHITE": __white,
        # short codes
        "BK": __black,
        "RD": __red,
        "GR": __green,
        "YL": __yellow,
        "BL": __blue,
        "MG": __magenta,
        "CY": __cyan,
        "WH": __white,
    }

    __bold = ";1"
    __faint = ";2"
    __italic = ";3"
    __underline = ";4"

    __start_cfg = "\x1b["
    __stop_cfg = "m"
    __reset = "\x1b[0m"

    __qualifier_mapping = {
        "B": __bold,
        "F": __faint,
        "UL": __underline,
        "IT": __italic,
    }

    def __custom(self, key):
        if key == "ARROW":
            return self.GR_B("—>")
        return None

    def __getattr__(self, item: str):
        if self.__custom(item) != None:
            return self.__custom(item)

        configs = item.upper().split("_")
        if configs[0] not in self.__color_mapping:
            color_code = ""
        else:
            color_code = self.__color_mapping.get(configs[0], "")

        qualifiers = configs[1:]

        if "BG" in qualifiers:
            qualifiers.remove("BG")
            if color_code != "":
                color_code += 10
        if "NB" in qualifiers:
            qualifiers.remove("NB")
            color_code -= 60

        qualifier_codes = [self.__qualifier_mapping.get(q, "") for q in qualifiers]

        return lambda s: (
            f"{self.__start_cfg}{color_code}{''.join(qualifier_codes)}{self.__stop_cfg}"
            + "{}"
            + self.__reset
        ).format(s)


if __name__ == "__main__":
    test_string = "hello world"
    import sys

    conf_str = sys.argv[1]
    print(getattr(TermCol, conf_str).format(test_string))
