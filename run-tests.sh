#!/bin/sh
#
# This file is part of the shibboleth-authenticator module for Invenio.
# Copyright (C) 2017  Helmholtz-Zentrum Dresden-Rossendorf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

pydocstyle shibboleth_authenticator tests && \
isort -rc -c -df **/*.py && \
check-manifest --ignore ".travis-*" && \
sphinx-build -qnNW docs/source docs/build/html && \
python setup.py test && \
sphinx-build -qnNW -b doctest docs/source docs/build/doctest
