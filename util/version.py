# -*- coding: utf-8 -*-
"""
Version information for Sultan-Saver application.
"""

# Version follows Semantic Versioning (SemVer) - https://semver.org/
# Format: MAJOR.MINOR.PATCH
# MAJOR version for incompatible API changes
# MINOR version for new functionality in a backwards compatible manner
# PATCH version for backwards compatible bug fixes

MAJOR = 1
MINOR = 0
PATCH = 0
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
APP_NAME = "苏丹的存档"
AUTHOR = "Klarkxy"
GITHUB = "https://github.com/klarkxy/Sultan-Saver"


def about_text() -> str:
    return f"""
{APP_NAME} v{VERSION}
作者: {AUTHOR}
代码仓库: {GITHUB}
© {__import__('datetime').datetime.now().year} 版权所有。
"""
