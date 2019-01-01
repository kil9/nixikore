#!/usr/bin/env python3

from config import hairpin
from hairpin.views import home  # noqa: F401


if __name__ == '__main__':
    hairpin.logger.info(u'*** hairpin 서버가 시작되었습니다. ***')
    try:
        hairpin.run(host='0.0.0.0', port=21000, debug=True)
    finally:
        hairpin.logger.info(u'*** hairpin 서버가 종료되었습니다. ***')
