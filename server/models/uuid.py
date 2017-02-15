import re


class UUID4:
    @staticmethod
    def validate(uuid):
        return re.match(
                "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}\
-[89ab][0-9a-f]{3}-[0-9a-f]{12}", uuid)
