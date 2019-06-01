# encoding: utf-8
# fwgslib.py -- utils for Waf build system by FWGS
# Copyright (C) 2018 a1batross, Michel Mooij (michel.mooij
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
from waflib import Utils, Errors

def get_flags_by_compiler(flags, compiler):
	'''Returns a list of compile flags, depending on compiler

	:param flags: compiler flags
	:type flags: dict
	:param compiler: compiler string(COMPILER_CC, for example)
	:type compiler: string
	:returns: list of flags
	'''
	out = []
	if compiler in flags:
		out += flags[compiler]
	elif 'default' in flags:
		out += flags['default']
	return out

def get_flags_by_type(flags, type, compiler):
	'''Returns a list of compile flags, depending on compiler and build type

	:param flags: compiler flags
	:param type: build type
	:type type: string
	:param compiler: compiler string(COMPILER_CC, for example)
	:type compiler: string
	:returns: list of flags
	'''
	out = []
	if 'common' in flags:
		out += get_flags_by_compiler(flags['common'], compiler)
	if type in flags:
		out += get_flags_by_compiler(flags[type], compiler)
	return out

def get_deps(bld, target):
	'''Returns a list of (nested) targets on which this target depends.

	:param bld: a *waf* build instance from the top level *wscript*
	:type bld: waflib.Build.BuildContext
	:param target: task name for which the dependencies should be returned
	:type target: str
	:returns: a list of task names on which the given target depends
	'''
	try:
		tgen = bld.get_tgen_by_name(target)
	except Errors.WafError:
		return []
	else:
		uses = Utils.to_list(getattr(tgen, 'use', []))
		deps = uses[:]
		for use in uses:
			deps += get_deps(bld, use)
		return list(set(deps))


def get_tgens(bld, names):
	'''Returns a list of task generators based on the given list of task
	generator names.

	:param bld: a *waf* build instance from the top level *wscript*
	:type bld: waflib.Build.BuildContext
	:param names: list of task generator names
	:type names: list of str
	:returns: list of task generators
	'''
	tgens=[]
	for name in names:
		try:
			tgen = bld.get_tgen_by_name(name)
		except Errors.WafError:
			pass
		else:
			tgens.append(tgen)
	return list(set(tgens))


def get_targets(bld):
	'''Returns a list of user specified build targets or None if no specific
	build targets has been selected using the *--targets=* command line option.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	:returns: a list of user specified target names (using --targets=x,y,z) or None
	'''
	if bld.targets == '':
		return None
	targets = bld.targets.split(',')
	for target in targets:
		targets += get_deps(bld, target)
	return targets