#!/usr/bin/python
# Methodmapizer for SourcePawn 1.7+
# Replaces all native calls with their equivalent methodmap call.
# Replaces old syntax declarations with new syntax
# By Peace-Maker, JoinedSenses
# Version 1.2Full


# NOTE: DO NOT RELY ON THIS SCRIPT. IT IS EXPERIMENTAL AND
# STILL IN DEVELOPMENT. ALWAYS DIFFCHECK CHANGES


import sys
import re
import os.path

if len(sys.argv) < 2:
	print('Give at least one file to methodmapize: file1.sp file2.sp ...')
	sys.exit(1)

# Updates Handles to their new class
def replaceDataType(dataType, code):
	pattern = r'(\w+)[ \t]*=[ \t]*new[ \t]+(' + dataType + ')'
	for m in re.finditer(pattern, code):
		var = m.group(1)
		var2 = m.group(2)
		pattern = r'(static[ \t]+)*Handle[ \t]+' + var + r'\b'
		replacement = r'\1'+var2+" "+var
		code = re.sub(pattern, replacement, code)
	return code

# Loops regex until it fails to find a result
def reLoop(pattern, repl, code, flags=0):
	m = re.search(pattern, code, flags)
	while m:
		code = re.sub(pattern, repl, code, 0, flags)
		m = re.search(pattern, code, flags)
	return code

# Updates convar handles to ConVar class
def replConVar(code):
	pattern = r'(\w+) *= *CreateConVar'
	for m in re.finditer(pattern, code):
		var = m.group(1)
		pattern = r'Handle[ \t]+'+var+r'\b'
		replacement = r'ConVar ' + var
		code = re.sub(pattern, replacement, code)
	return code

# Updates file handles to File class
def replFileType(code):
	pattern = r'(\w+)[ \t]*= *OpenFile'
	for m in re.finditer(pattern, code):
		var = m.group(1)
		pattern = r'Handle[ \t]+'+var+r'\b'
		replacement = r'File ' + var
		code = re.sub(pattern, replacement, code)
	return code

# Run through all passed files
for i in range(1, len(sys.argv)):
	if not os.path.isfile(sys.argv[i]):
		print('File not found: {}'.format(sys.argv[i]))
		continue

	code = ''
	with open(sys.argv[i], 'r', encoding='utf-8') as f:
		code = f.read()

		# Formatting stuff. OPTIONAL: DISABLE IF YOU LIKE UGLY THINGS
		# *****************************************************************************
		print('\nFormatting {}'.format(sys.argv[i]))

		# This brings curly braces up to the line above it if it's alone on a line (reason: preference/readability)
		# function(whatever)
		# {
		# -------------->
		# function(whatever) {
		code = re.sub(r'[ \t]*\n[ \t]*\{', r' {', code)

		# These remove spaces inside of brackets & parenthesis (reason: ugly)
		# [ WHATEVER + 1 ] -> [WHATEVER + 1]
		code = re.sub(r'[ \t]+\]', r']', code)
		code = re.sub(r'\[[ \t]+', r'[', code)
		code = re.sub(r'[ \t]+\)', r')', code)
		code = re.sub(r'\([ \t]+', r'(', code)
		code = re.sub(r'[ \t]+\n', r'\n', code)

		# Adds spaces between <>= and characters (reason: preference)
		# i<=MaxClients
		# -------------->
		# i <= MaxClients
		code = re.sub(r'(?<=[^<])(\b\w+)([=<>]+)[ \t]*(\w+\b)(?=[^>]+[ \t\(\[\;])(?=(?:[^"]*"[^"]*")*[^"]*$)', r'\1 \2 \3', code)
		code = re.sub(r'(?<=[^<])(\b\w+)[ \t]*([=<>]+)(\w+\b)(?=[^>]+[ \t\(\[\;])(?=(?:[^"]*"[^"]*")*[^"]*$)', r'\1 \2 \3', code)

		# Adds a space between comma and character
		code = re.sub(r',(\w)', r', \1', code)

		# This adds a space between if/else/while/for and left parenthesis (reason: preference)
		# if(whatever)
		# -------------->
		# if (whatever)
		code = re.sub(r'(if|else|while|for)\(', r'\1 (', code)

		# This splits up single line functions without curly braces (reason: ugly/readability)
		# if (whatever) doThing;
		# -------------->
		# if (whatever)
		#	doThing;
		code = re.sub(r'^(\t+)(\w.*?\))( |\t)*(\w)(?=(?:[^\"\n]*\"[^\"\n]*\")*[^\"\n]*$)', r'\1\2\n\1\t\4', code, 0, re.M)
		code = re.sub(r'^(\t+)(else)([ \t]+)(?!if)(\w)', r'\1\2\n\1\t\4', code, 0, re.M)

		# This adds curly braces around unbraced single method functions (reason: preference)
		# if (whatever)
		#	doThing;
		# -------------->
		# if (whatever) {
		#	doThing;
		# }
		code = re.sub(r'(^\t+)((?:\w.*?\)|else)[ \t]*)(\n\1\t.*?\;)', r'\1\2 {\3\n\1}', code, 0, re.M)

		# This moves else down a line if next to a right curly brace (reason: preference/readability)
		# } else
		# -------------->
		# }
		# else
		code = re.sub(r'(\t+)\}[ \t]*(else)', r'\1}\n\1\2', code)

		# This adds curly braces around unbraced else functions (reason: preference)
		# else
		#	whatever;
		# -------------->
		# else {
		#	whatever;
		# }
		code = re.sub(r'(\t+)(else[ \t]*)(\n\1\t.*?\;)', r'\1\2 {\3\n\1}', code)

		# These lines turn single line functions into multi-lined and also split multiple functions(reason: ugly)
		# This also brings commands from the side of functions to the top (reason: ease of future regex searches)
		#
		# if (whatever) { do thing; } // Comment
		# -------------->
		# // Comment
		# if (whatever) {
		#	do thing;
		# }
		# * * * * * * * * * * * * *
		# doThing1(whatever); doThing2(whatever);
		# -------------->
		# doThing1(whatever);
		# doThing2(whatever);
		code = re.sub(r'(^\w.*?)[ \t]*(?<!:)(\/\/.*?)({)$', r'\2\n\1 \3', code, 0, re.M)
		code = re.sub(r'(^\w.*?)[ \t]*(?<!:)(\/\/.*?$)', r'\2\n\1', code, 0, re.M)
		code = re.sub(r'(^[ \t]+)(\w.*;)[ \t]*(})', r'\1\2\n\1\3', code, 0, re.M)
		code = re.sub(r'(^[ \t]\t+)(\w.*?(?:\:|\))[ \t]*\{) *(\w)', r'\1\2\n\1\t\3', code, 0, re.M)
		code = re.sub(r'(^[ \t]+)(\w.*;)[ \t]*(?<!:)(\/\/[ \t]*$)', r'\1\2', code, 0, re.M)
		code = re.sub(r'(^[ \t]+)(\w.*?)[ \t]*(?<!:)(\/\/.*?)([ \t]*\{?)$', r'\1\3\n\1\2 \4', code, 0, re.M)
		code = reLoop(r'(^[ \t]+)(\w.*?;)[ \t]+([^)}\n]+$)', r'\1\2\n\1\3', code, re.M)
		# CODE NOW MORE PRETTY
		# *****************************************************************************

		print('Methodmapizing {}'.format(sys.argv[i]))

		# AdminId
		code = re.sub(r'\bBindAdminIdentity[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindIdentity(', code)
		code = re.sub(r'\bCanAdminTarget[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.CanTarget(', code)
		code = re.sub(r'\bGetAdminFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFlags(', code)
		code = re.sub(r'\bGetAdminGroup[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetGroup(', code)
		code = re.sub(r'\bGetAdminPassword[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetPassword(', code)
		code = re.sub(r'\bGetAdminFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.HasFlag(', code)
		code = re.sub(r'\bAdminInheritGroup[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.InheritGroup(', code)
		code = re.sub(r'\bSetAdminPassword[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetPassword(', code)
		code = re.sub(r'\bGetAdminGroupCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.GroupCount', code)
		code = re.sub(r'\bGetAdminImmunityLevel[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.ImmunityLevel', code)
		code = re.sub(r'\bSetAdminImmunityLevel[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ImmunityLevel = \2', code)

		# GroupId
		code = re.sub(r'\bAddAdmGroupCmdOverride[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddCommandOverride(', code)
		code = re.sub(r'\bSetAdmGroupImmuneFrom[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddGroupImmunity(', code)
		code = re.sub(r'\bGetAdmGroupCmdOverride[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetCommandOverride(', code)
		code = re.sub(r'\bGetAdmGroupAddFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFlags(', code)
		code = re.sub(r'\bGetAdmGroupImmunity[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetGroupImmunity(', code)
		code = re.sub(r'\bGetAdmGroupAddFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.HasFlag(', code)
		code = re.sub(r'\bSetAdmGroupAddFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFlag(', code)
		code = re.sub(r'\bGetAdmGroupImmuneCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.GroupImmunitiesCount', code)
		code = re.sub(r'\bGetAdmGroupImmunityLevel[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.ImmunityLevel', code)
		code = re.sub(r'\bSetAdmGroupImmunityLevel[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ImmunityLevel = \2', code)

		# ArrayList
		code = re.sub(r'\bClearArray[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clear()', code)
		code = re.sub(r'\bCloneArray[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clone()', code)
		code = re.sub(r'\bCreateArray[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new ArrayList(\1)', code)
		code = re.sub(r'\bFindStringInArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindString(', code)
		code = re.sub(r'\bFindValueInArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindValue(', code)
		code = re.sub(r'\bGetArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetArray(', code)
		code = re.sub(r'\bGetArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Get(', code)
		code = re.sub(r'\bGetArraySize[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Length', code)
		code = re.sub(r'\bGetArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'\bPushArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushArray(', code)
		code = re.sub(r'\bPushArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Push(', code)
		code = re.sub(r'\bPushArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushString(', code)
		code = re.sub(r'\bRemoveFromArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Erase(', code)
		code = re.sub(r'\bResizeArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Resize(', code)
		code = re.sub(r'\bSetArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetArray(', code)
		code = re.sub(r'\bSetArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Set(', code)
		code = re.sub(r'\bSetArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'\bShiftArrayUp[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ShiftUp(', code)
		code = re.sub(r'\bSwapArrayItems[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SwapAt(', code)

		# ArrayStack
		code = re.sub(r'\bCreateStack[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new ArrayStack(\1)', code)
		code = re.sub(r'\bIsStackEmpty[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Empty', code)
		code = re.sub(r'\bPopStackArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PopArray(', code)
		code = re.sub(r'\bPopStackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Pop(', code)
		code = re.sub(r'\bPopStackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PopString(', code)
		code = re.sub(r'\bPushStackArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushArray(', code)
		code = re.sub(r'\bPushStackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Push(', code)
		code = re.sub(r'\bPushStackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushString(', code)

		# StringMap
		code = re.sub(r'\bCreateTrie[ \t]*\([ \t]*\)', r'new StringMap()', code)
		code = re.sub(r'\bGetTrieSize[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Size', code)
		code = re.sub(r'\bClearTrie[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clear()', code)
		code = re.sub(r'\bGetTrieString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'\bSetTrieString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'\bGetTrieValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetValue(', code)
		code = re.sub(r'\bSetTrieValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetValue(', code)
		code = re.sub(r'\bGetTrieArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetArray(', code)
		code = re.sub(r'\bSetTrieArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetArray(', code)
		code = re.sub(r'\bRemoveFromTrie[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Remove(', code)

		# StringMapSnapshot
		code = re.sub(r'\bCreateTrieSnapshot[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Snapshot()', code)
		code = re.sub(r'\bTrieSnapshotKeyBufferSize[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.KeyBufferSize(', code)
		code = re.sub(r'\bGetTrieSnapshotKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetKey(', code)
		code = re.sub(r'\bTrieSnapshotLength[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Length', code)

		# BfRead/BfWrite
		code = re.sub(r'\bBf((?:Read|Write)\w+)\((\w+)[, ]*', r'\2.\1(', code)

		# ConVar
		code = re.sub(r'\bGetConVarBool[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.BoolValue', code)
		code = re.sub(r'\bGetConVarBounds[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetBounds(', code)
		code = re.sub(r'\bGetConVarDefault[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetDefault(', code)
		code = re.sub(r'\bGetConVarFlags[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Flags', code)
		code = re.sub(r'\bGetConVarFloat[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FloatValue', code)
		code = re.sub(r'\bGetConVarInt\((FindConVar\(.+?\)|.+?)\)', r'\1.IntValue', code)
		code = re.sub(r'\bGetConVarName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetName(', code)
		code = re.sub(r'\bGetConVarString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'\bHookConVarChange[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddChangeHook(', code)
		code = re.sub(r'\bResetConVar[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RestoreDefault(', code)
		code = re.sub(r'\bSendConVarValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReplicateToClient(', code)

		# Only use the method if the original call has more than 2 parameters.
		code = re.sub(r'\bSetConVarBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetBool(\2,', code)
		code = re.sub(r'\bSetConVarBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.BoolValue = \2', code)

		code = re.sub(r'\bSetConVarBounds[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetBounds(', code)
		code = re.sub(r'\bSetConVarFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Flags = \2', code)

		code = re.sub(r'\bSetConVarFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetFloat(\2,', code)
		code = re.sub(r'\bSetConVarFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.FloatValue = \2', code)
		code = re.sub(r'\bSetConVarInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetInt(\2,', code)
		code = re.sub(r'\bSetConVarInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.IntValue = \2', code)
		code = re.sub(r'\bSetConVarString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'\bUnhookConVarChange[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveChangeHook(', code)

		# Cookie
		code = re.sub(r'\bRegClientCookie[ \t]*\([ \t]*\)', r'new Cookie(', code)
		code = re.sub(r'\bFindClientCookie[ \t]*\(', r'Cookie.Find(', code)
		code = re.sub(r'\bSetClientCookie[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*([^\,]+)[ \t]*', r'\2.Set(\1', code)
		code = re.sub(r'\bGetClientCookie[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*([^\,]+)[ \t]*', r'\2.Get(\1', code)
		code = re.sub(r'\bSetAuthIdCookie[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*([^\,]+)[ \t]*', r'\2.SetByAuthId(\1', code)
		code = re.sub(r'\bSetCookiePrefabMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetPrefabMenu(', code)
		code = re.sub(r'\bGetCookieAccess[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.AccessLevel', code)

		# DataPack
		code = re.sub(r'\bCreateDataPack[ \t]*\([ \t]*\)', r'new DataPack()', code)
		code = re.sub(r'\bWritePackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteCell(', code)
		code = re.sub(r'\bWritePackFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteFloat(', code)
		code = re.sub(r'\bWritePackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteString(', code)
		code = re.sub(r'\bWritePackFunction[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteFunction(', code)
		code = re.sub(r'\bReadPackCell[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadCell()', code)
		code = re.sub(r'\bReadPackFloat[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadFloat()', code)
		code = re.sub(r'\bReadPackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadString(', code)
		code = re.sub(r'\bReadPackFunction[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadFunction()', code)
		code = re.sub(r'\bResetPack[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.Reset(\2)', code)
		code = re.sub(r'\bGetPackPosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Position', code)
		code = re.sub(r'\bSetPackPosition[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Position = \2', code)
		code = re.sub(r'\bIsStackEmptyckReadable[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsReadable(', code)

		# DBDriver
		code = re.sub(r'\bSQL_GetDriver[ \t]*\(', r'DBDriver.Find(', code)
		code = re.sub(r'\bSQL_GetDriverProduct[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetProduct(', code)
		code = re.sub(r'\bSQL_GetDriverIdent[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetIdentifier(', code)

		# DBResultSet
		code = re.sub(r'\bSQL_FetchMoreResults[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FetchMoreResults()', code)
		code = re.sub(r'\bSQL_HasResultSet[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.HasResults', code)
		code = re.sub(r'\bSQL_GetRowCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.RowCount', code)
		code = re.sub(r'\bSQL_GetFieldCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FieldCount', code)
		code = re.sub(r'\bSQL_GetAffectedRows[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.AffectedRows', code)
		code = re.sub(r'\bSQL_GetInsertId[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.InsertId', code)
		code = re.sub(r'\bSQL_FieldNumToName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FieldNumToName(', code)
		code = re.sub(r'\bSQL_FieldNameToNum[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FieldNameToNum(', code)
		code = re.sub(r'\bSQL_FetchRow[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FetchRow()', code)
		code = re.sub(r'\bSQL_MoreRows[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.MoreRows', code)
		code = re.sub(r'\bSQL_Rewind[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Rewind()', code)
		code = re.sub(r'\bSQL_FetchString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchString(', code)
		code = re.sub(r'\bSQL_FetchFloats*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchFloat(', code)
		code = re.sub(r'\bSQL_FetchInt*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchInt(', code)
		code = re.sub(r'\bSQL_IsFieldNull*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsFieldNull(', code)
		code = re.sub(r'\bSQL_FetchSize*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchSize(', code)

		# Transaction
		code = re.sub(r'\bSQL_CreateTransaction[ \t]*\([ \t]*\)', r'new Transaction()', code)
		code = re.sub(r'\bSQL_AddQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddQuery(', code)

		# DBStatement
		code = re.sub(r'\bSQL_BindParamInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindInt(', code)
		code = re.sub(r'\bSQL_BindParamFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindFloat(', code)
		code = re.sub(r'\bSQL_BindParamString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindString(', code)

		# Database
		code = re.sub(r'\bSQL_TConnect[ \t]*\(', r'Database.Connect(', code)
		# Only replace if the optional ident argument isn't used.
		code = re.sub(r'\bSQL_ReadDriver[ \t]*\([ \t]*([^\)\,]+)[ \t]*\)', r'\1.Driver', code)
		code = re.sub(r'\bSQL_SetCharset[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetCharset(', code)
		code = re.sub(r'\bSQL_EscapeString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Escape(', code)
		code = re.sub(r'\bSQL_FormatQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Format(', code)
		code = re.sub(r'\bSQL_IsSameConnection[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsSameConnection(', code)
		code = re.sub(r'\bSQL_TQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Query(', code)
		code = re.sub(r'\bSQL_ExecuteTransaction[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Execute(', code)

		# Event
		code = re.sub(r'\bFireEvent[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.Fire(\2)', code)
		code = re.sub(r'\bCancelCreatedEvent[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Cancel()', code)
		code = re.sub(r'\bGetEventBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetBool(', code)
		code = re.sub(r'\bSetEventBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetBool(', code)
		code = re.sub(r'\bGetEventInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetInt(', code)
		code = re.sub(r'\bSetEventInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetInt(', code)
		code = re.sub(r'\bGetEventFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFloat(', code)
		code = re.sub(r'\bSetEventFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFloat(', code)
		code = re.sub(r'\bGetEventString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'\bSetEventString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'\bGetEventName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetName(', code)
		code = re.sub(r'\bSetEventBroadcast[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.BroadcastDisabled = \2', code)

		# DirectoryListing
		code = re.sub(r'\bReadDirEntry[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetNext(', code)

		# File
		code = re.sub(r'\bIsEndOfFile[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.EndOfFile()', code)
		code = re.sub(r'\bReadFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Read(', code)
		code = re.sub(r'\bReadFileLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadLine(', code)
		code = re.sub(r'\bReadFileString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadString(', code)
		code = re.sub(r'\bFileSeek[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Seek(', code)
		code = re.sub(r'\bWriteFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Write(', code)
		code = re.sub(r'\bWriteFileLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteLine(', code)
		code = re.sub(r'\bWriteStringLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteString(', code)
		code = re.sub(r'\bFilePosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Position', code)
		# TODO: ReadFileCell & ReadIntX

		# Forwards
		code = re.sub(r'\bCreateGlobalForward[ \t]*\(', r'new GlobalForward(', code)
		code = re.sub(r'\bGetForwardFunctionCount[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.FunctionCount', code)

		code = re.sub(r'\bCreateForward[ \t]*\(', r'new PrivateForward(', code)
		code = re.sub(r'\bAddToForward[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddFunction(', code)
		code = re.sub(r'\bRemoveFromForward[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveFunction(', code)
		code = re.sub(r'\bRemoveAllFromForward[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveAllFunctions(', code)

		# Handles
		code = re.sub(r'\bCloseHandle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'delete \1', code)

		# KeyValues
		code = re.sub(r'\bCreateKeyValues[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'new KeyValues(\1)', code)
		code = re.sub(r'\bKvSetString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'\bKvSetNum[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetNum(', code)
		code = re.sub(r'\bKvSetUInt64[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetUInt64(', code)
		code = re.sub(r'\bKvSetFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFloat(', code)
		code = re.sub(r'\bKvSetColor[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetColor(', code)
		code = re.sub(r'\bKvSetVector[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetVector(', code)
		code = re.sub(r'\bKvGetString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'\bKvGetNum[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*', r'\1.GetNum(', code)
		code = re.sub(r'\bKvGetFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFloat(', code)
		code = re.sub(r'\bKvGetColor[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetColor(', code)
		code = re.sub(r'\bKvGetUInt64[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetUInt64(', code)
		code = re.sub(r'\bKvGetVector[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetVector(', code)
		code = re.sub(r'\bKvJumpToKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.JumpToKey(', code)
		code = re.sub(r'\bKvJumpToKeySymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.JumpToKeySymbol(', code)
		code = re.sub(r'\bKvGotoFirstSubKey[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.GotoFirstSubKey(\2)', code)
		code = re.sub(r'\bKvGotoNextKey[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.GotoNextKey(\2)', code)
		code = re.sub(r'\bKvSavePosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.SavePosition()', code)
		code = re.sub(r'\bKvDeleteKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DeleteKey(', code)
		code = re.sub(r'\bKvDeleteThis[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.DeleteThis()', code)
		code = re.sub(r'\bKvGoBack[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.GoBack()', code)
		code = re.sub(r'\bKvRewind[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Rewind()', code)
		code = re.sub(r'\bKvGetSectionName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSectionName(', code)
		code = re.sub(r'\bKvSetSectionName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetSectionName(', code)
		code = re.sub(r'\bKvGetDataType[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetDataType(', code)
		code = re.sub(r'\bKeyValuesToFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ExportToFile(', code)
		code = re.sub(r'\bFileToKeyValues[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ImportFromFile(', code)
		code = re.sub(r'\bStringToKeyValues[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ImportFromString(', code)
		code = re.sub(r'\bKvSetEscapeSequences[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetEscapeSequences(', code)
		code = re.sub(r'\bKvNodesInStack[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.NodesInStack()', code)
		code = re.sub(r'\bKvCopySubkeys[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Import(', code)
		code = re.sub(r'\bKvFindKeyById[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindKeyById(', code)
		code = re.sub(r'\bKvGetNameSymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetNameSymbol(', code)
		code = re.sub(r'\bKvGetSectionSymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSectionSymbol(', code)
		
		# Menu
		code = re.sub(r'\bCreateMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'new Menu(\1)', code)
		code = re.sub(r'\bDisplayMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Display(', code)
		code = re.sub(r'\bDisplayMenuAtItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayAt(', code)
		code = re.sub(r'\bAddMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddItem(', code)
		code = re.sub(r'\bInsertMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.InsertItem(', code)
		code = re.sub(r'\bRemoveMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveItem(', code)
		code = re.sub(r'\bRemoveAllMenuItems[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.RemoveAllItems()', code)
		code = re.sub(r'\bGetMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetItem(', code)
		code = re.sub(r'\bGetMenuSelectionPosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Selection', code)
		code = re.sub(r'\bGetMenuItemCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ItemCount', code)
		code = re.sub(r'\bSetMenuPagination[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Pagination = \2', code)
		code = re.sub(r'\bGetMenuPagination[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Pagination', code)
		code = re.sub(r'\bGetMenuStyle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Style', code)
		code = re.sub(r'\bSetMenuTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetTitle(', code)
		code = re.sub(r'\bGetMenuTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetTitle(', code)
		code = re.sub(r'\bCreatePanelFromMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ToPanel()', code)
		code = re.sub(r'\bGetMenuExitButton[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ExitButton', code)
		code = re.sub(r'\bSetMenuExitButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ExitButton = \2', code)
		code = re.sub(r'\bGetMenuExitBackButton[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ExitBackButton', code)
		code = re.sub(r'\bSetMenuExitBackButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ExitBackButton = \2', code)
		code = re.sub(r'\bSetMenuNoVoteButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.NoVoteButton = \2', code)
		code = re.sub(r'\bCancelMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Cancel()', code)
		code = re.sub(r'\bGetMenuOptionFlags[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.OptionFlags', code)
		code = re.sub(r'\bSetMenuOptionFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OptionFlags = \2', code)
		code = re.sub(r'\bVoteMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayVote(', code)
		code = re.sub(r'\bVoteMenuToAll[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayVoteToAll(', code)
		code = re.sub(r'\bSetVoteResultCallback[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.VoteResultCallback = \2', code)

		# Panel
		code = re.sub(r'\bCreatePanel[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new Panel(\1)', code)
		code = re.sub(r'\bGetPanelStyle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Style', code)
		code = re.sub(r'\bSetPanelTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetTitle(', code)
		code = re.sub(r'\bDrawPanelItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DrawItem(', code)
		code = re.sub(r'\bDrawPanelText[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DrawText(', code)
		code = re.sub(r'\bCanPanelDrawFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.CanDrawFlags(', code)
		code = re.sub(r'\bSetPanelKeys[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetKeys(', code)
		code = re.sub(r'\bSendPanelToClient[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Send(', code)
		code = re.sub(r'\bGetPanelTextRemaining[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.TextRemaining', code)
		code = re.sub(r'\bGetPanelCurrentKey[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.CurrentKey', code)
		code = re.sub(r'\bSetPanelCurrentKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.CurrentKey = \2', code)

		# Protobuf
		code = re.sub(r'\bPb((?:Add|Read|Set|Get|Remove)\w+)\((\w+)[, ]*', r'\2.\1(', code)

		# Regex
		code = re.sub(r'\bCompileRegex[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new Regex(\1)', code)
		code = re.sub(r'\bMatchRegex[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Match(', code)
		code = re.sub(r'\bGetRegexSubString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSubString(', code)

		# SMCParser
		code = re.sub(r'\bSMC_CreateParser[ \t]*\([ \t]*\)', r'new SMCParser()', code)
		code = re.sub(r'\bSMC_ParseFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ParseFile(', code)
		code = re.sub(r'\bSMC_SetParseStart[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnStart = \2', code)
		code = re.sub(r'\bSMC_SetParseEnd[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnEnd = \2', code)
		code = re.sub(r'([ \t]+)SMC_SetReaders\((\w+),[ \t]*(\w+),[ \t]*(\w+),[ \t]*(\w+).*', r'\1\2.OnEnterSection = \3;\n\1\2.OnKeyValue = \4;\n\1\2.OnLeaveSection = \5;', code)
		code = re.sub(r'\bSMC_SetRawLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnRawLine = \2', code)
		code = re.sub(r'\bSMC_GetErrorString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetErrorString(', code)

		# TopMenu
		code = re.sub(r'\bCreateTopMenu[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new TopMenu(\1)', code)
		code = re.sub(r'\bLoadTopMenuConfig[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.LoadConfig(', code)
		code = re.sub(r'\bAddToTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,[ \t]*TopMenuObject_Category', r'\1.AddCategory(\2, ', code)
		code = re.sub(r'\bAddToTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,[ \t]*TopMenuObject_Item', r'\1.AddItem(\2', code)
		code = re.sub(r'\bGetTopMenuInfoString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetInfoString(', code)
		code = re.sub(r'\bGetTopMenuObjName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetObjName(', code)
		code = re.sub(r'\bRemoveFromTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Remove(', code)
		code = re.sub(r'\bDisplayTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Display(', code)
		code = re.sub(r'\bDisplayTopMenuCategory[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayCategory(', code)
		code = re.sub(r'\bFindTopMenuCategory[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindCategory(', code)
		code = re.sub(r'\bSetTopMenuTitleCaching[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.CacheTitles = \2', code)



		# --------------------------------------------------------------------------------------------------------------------------------
		# GENERAL SYNTAX UPDATES
		print('Updating syntax on {}'.format(sys.argv[i]))

		# type:whatever -> view_as<type>(whatever)
		code = reLoop(r'(=[ \t]*)(\w+):(.*?)(,|;)(?=(?:[^{]*{[^}]*})*[^}]*$)(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)(?=(?:[^\(]*\([^\)]*\))*[^\)]*$)', r'\1view_as<\2>(\3)\4', code, re.M)

		# update function type to void
		code = re.sub(r'(\npublic )((?:OnMapTimeLeftChanged|TF2_OnConditionAdded|TF2_OnWaitingForPlayersEnd|TF2_OnWaitingForPlayersStart|TF2_OnConditionRemoved|OnEntityCreated|OnEntityDestroyed|OnMapVoteStarted|OnNominationRemoved|OnClientSayCommand_Post|BaseComm_OnClientGag|OnClientCookiesCached|BaseComm_OnClientMute|OnAdminMenuCreated|OnAdminMenuReady|OnRebuildAdminCache|OnClientAuthorized|OnClientPostAdminCheck|OnClientPostAdminFilter|OnClientPutInServer|OnClientSettingsChanged|OnClientDisconnect_Post|OnClientConnected|OnClientDisconnect|OnAllPluginsLoaded|OnAutoConfigsBuffered|OnClientFloodResult|OnConfigsExecuted|OnGameFrame|OnLibraryAdded|OnLibraryRemoved|OnMapEnd|OnMapStart|OnPluginEnd|OnPluginPauseChange|OnPluginStart|OnServerCfg)[ \t]*\()', r'\1void \2', code)

		# public native -> public int native
		for m in re.finditer(r'\bCreateNative\(.*?,[ \t]*(.*?)[ \t]*\)', code):
			native = m.group(1)
			pattern = r'\npublic '+native+r'\('
			replace = r'\npublic int '+native+r'('
			code = re.sub(pattern, replace, code)

		# public convarChange -> public void convarChange
		for m in re.finditer(r'\.AddChangeHook\([ \t]*(.*?)[ \t]*\)', code):
			convarChange = m.group(1)
			pattern = r'\npublic '+convarChange+r'\( *\w+'
			replace = r'\npublic void '+convarChange+r'(ConVar'
			code = re.sub(pattern, replace, code)

		# public eventHook -> public void eventHook
		for m in re.finditer(r'\bHookEvent(?:Ex)*\(.*?,[ \t]*(.*?)[ \t]*(,|\))', code):
			event = m.group(1)
			pattern = r'\npublic '+event+r'\([ \t]*\w+'
			replace = r'\npublic void '+event+r'(Event'
			code = re.sub(pattern, replace, code)
			pattern = r'Action(:| +)'+event+r'[ \t]*\(Handle(:| +)'
			replace = r'Action '+event+r'(Event '
			code = re.sub(pattern, replace, code)

		# ***************************************
		# socket(even though this isn't included in SM, I've added it)
		m = re.search(r'\bSocketCreate\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*\)', code)
		if m:
			SocketErrorCB = m.group(1)
			code = re.sub(r'(\npublic )'+r'([ \t]*\b'+SocketErrorCB+r'\b[ \t]*)', r'\1void \2', code)

		m = re.search(r'\bSocketListen\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*\)', code)
		if m:
			SocketIncomingCB = m.group(1)
			code = re.sub(r'(\npublic )'+r'([ \t]*\b'+SocketIncomingCB+r'\b[ \t]*)', r'\1void \2', code)

		m = re.search(r'\bSocketSetSendqueueEmptyCallback\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*\)', code)
		if m:
			SocketSendqueueEmptyCB = m.group(1)
			code = re.sub(r'(\npublic )'+r'([ \t]*\b'+SocketSendqueueEmptyCB+r'\b[ \t]*)', r'\1void \2', code)

		m = re.search(r'\bSocketConnect\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*,[ \t]*(.*?)[ \t]*,[ \t]*(.*?)[ \t]*,', code)
		if m:
			SocketConnectCB = m.group(1)
			SocketReceiveCB = m.group(2)
			SocketDisconnectCB = m.group(3)
			code = re.sub(r'(^public[ \t])'+r'([ \t]*\b'+SocketConnectCB+r'\b[ \t]*)', r'\1void \2', code, 0, re.M)
			code = re.sub(r'(^public[ \t])'+r'([ \t]*\b'+SocketReceiveCB+r'\b[ \t]*)', r'\1void \2', code, 0, re.M)
			code = re.sub(r'(^public[ \t])'+r'([ \t]*\b'+SocketDisconnectCB+r'\b[ \t]*)', r'\1void \2', code, 0, re.M)
		# ****************************************

		# Remove deprecated FCVAR_PLUGIN
		code = re.sub(r'(?:\|FCVAR_PLUGIN|FCVAR_PLUGIN\|)', r'', code)
		code = re.sub(r'FCVAR_PLUGIN', r'0', code)

		# Update invalid_handle to null
		code = re.sub(r'INVALID_HANDLE', r'null', code)

		code = re.sub(r'\biClient', r'client', code)

		# Check to remove unrequired var type in BuildPath (idk, i saw a plugin do this, so i added it)
		code = re.sub(r'(BuildPath\()[ \t]*PathType:*', r'\1', code)

		# String:whatever[] -> char[] whatever
		code = re.sub(r'(?<!new )String:*(\w+)((?:\[\])+)', r'char\2 \1', code)

		# ***********************************************************************************
		# ## Var Declarations ##
		# decl String:whatever[1], Float:whatever, whatever;
		# -------------->
		# char whatever[1];
		# float whatever;
		# int whatever;
		code = reLoop(r'^([ \t]*)(decl[ \t]+.+), (\w+(?:\[[ \t]*\w+[ \t]*\])?[ \t]*)(?:,[ \t]*|=[ \t]*\-?(?:\d+|\w+)[ \t]*(?:\)|,[ \t]*)|;)(?=(?:[^{]*{[^}]*})*[^}]*$)(?=(?:[^"]*"[^"]*")*[^"]*$)(?=[^)]*$)', r'\1\2;\n\1int \3;\n\1', code, re.M)
		code = re.sub(r'(decl\b +)(\w+(?:\[.+?\][ =]*\d*)*)(;|[ \t]*,[ \t]*)', r'\1 int \2\3', code)
		code = reLoop(r'^([ \t]*)(decl\b[^(\n]+)(.*?\),|,[ \t]*)(.*?)(;|,[ \t]*)', r'\1\2;\n\1\4;', code, re.M)
		code = re.sub(r'decl\b +', r'', code)
		# 
		# Same thing, but for new String:whatever[1], Float:whatever, whatever;
		code = reLoop(r'^([ \t]*)(new[ \t]+.+),[ \t]+(\w+(?:\[[ \t]*\w+[ \t]*\])?[ \t]*)(?:,|=[ \t]*\-?(?:\d+|\w+)[ \t]*(?:\)|,)|;)(?=(?:[^{]*{[^}]*})*[^}]*$)(?=(?:[^"]*"[^"]*")*[^"]*$)(?=[^)]*$)', r'\1\2;\n\1int \3;\n\1', code, re.M)
		code = re.sub(r'(?<!=)(?<! )(new\b +)(\w+(?:\[.+?\][ =]*\d*)*)(;|[ \t]*,[ \t]*)', r'\1 int \2\3', code)
		code = reLoop(r'^([ \t]*)(new\b(?!.*=[ \t]*\w+[ \t]*\()[^\(\n\{]+)([^\(]+\),|,[ \t]*)(.*?)(;|,[ \t]*)', r'\1\2;\n\1\4;\1', code, re.M)
		code = re.sub(r'^([ \t]*)new[ \t]+(\w+[ \t:]+\w)', r'\1\2', code, 0, re.M)
		# ************************************************************************************

		# _: int retagging
		code = re.sub(r'\b_:(.*?)((?:\]|,)[ \t]*|[)]+|;)', r'view_as<int>(\1)\2', code)

		code = re.sub(r'\bGetClientAuthString\([ \t]*(.*?,)', r'GetClientAuthId(\1 AuthId_Steam2,', code)

		# new String:var -> char var
		code = re.sub(r'(?:new[ \t]+)*String:', r'char ', code)

		# new dataType:whatever -> dataType whatever
		code = re.sub(r'new[ \t]+(\w+):', r'\1 ', code)

		# Handle: -> Handle 
		code = re.sub(r'Handle:',r'Handle ', code)

		# Float -> float
		code = re.sub(r'\bFloat\b(:|[ \t]+)', r'float ', code)

		# new var -> int var
		code = re.sub(r'(\n\t*)new[ \t]+(\w+([ \t]*\=|\;))', r'\1int \2', code)

		# for (new = -> for (int =
		code = re.sub(r'(for[ \t]*\()[ \t]*new', r'\1int', code)

		# dataType:whatever -> dataType whatever
		code = re.sub(r'(^.*?\w):(\w.*\()', r'\1 \2', code, 0, re.M)

		# new var -> int var
		code = re.sub(r'(?<!= )(?<!=)new[ \t]+(\w+(?:\[.+?\])*(?:\,|\;|[ \t]*=[ \t]*-*\d+))', r'int \1', code)

		# const var -> const int var
		code = re.sub(r'(,*[ \t]*const) ([\w\d_]+\,)', r'\1 int \2', code)

		# dataType:whatever -> dataType whatever (NOTE TO SELF: reference this for finding things not inside of quotes!)
		code = reLoop(r'(\([ \t]*|,[ \t]*)([a-zA-Z]+):(\w[^\"\n,]+(,|\)))', r'\1\2 \3', code)
		code = re.sub(r'(^public[ \t]+\w+):(.*?\=)', r'\1 \2', code, 0, re.M)

		# removes colons from bool and any
		code = re.sub (r'^(\t*bool):', r'\1 ', code, 0, re.M)
		code = re.sub (r'(any):(\.)', r'\1 \2', code)

		# DataType vars
		# Handle var -> ConVar var
		code = replConVar(code)
		# Handle var -> File var
		code = replFileType(code)

		dataTypes = [
			  "ArrayList"
			, "ArrayStack"
			, "Cookie"
			, "DataPack"
			, "GlobalForward"
			, "KeyValues"
			, "Menu"
			, "Panel"
			, "PrivateForward"
			, "Regex"
			, "SMCParser"
			, "StringMap"
			, "TopMenu"
			, "Transaction"
		]
		for dataType in dataTypes:
			code = replaceDataType(dataType, code)

		# Handle var -> ArrayList var
		for m in re.finditer(r'(\w+)[ \t]*=[ \t]*GetNativeCell', code):
			var = m.group(1)
			pattern = r'Handle[ \t]+'+var+r'\b'
			replace = r'ArrayList '+var
			code = re.sub(pattern, replace, code)

		# Handle var -> ConVar var
		for m in re.finditer(r'([\w_]+)[ \t]*=[ \t]*FindConVar\(', code):
			var = m.group(1)
			pattern = r'Handle[ \t]+'+var+r'\b'
			replace = r'ConVar '+var
			code = re.sub(pattern, replace, code)

		for m in re.finditer(r'([\w_]+)[ \t]*=[ \t]*OpenDirectory\(', code):
			var = m.group(1)
			pattern = r'Handle[ \t]+'+var+r'\b'
			replace = r'DirectoryListing '+var
			code = re.sub(pattern, replace, code)

		# Redundancy check on converting handles to ArrayList class
		re.sub(r'Handle[ \t]+(\w+[ \t]*=[ \t]*GetNativeCell)', r'ArrayList \1', code)

		# public Menu_Handler -> public int Menu_Handler
		for m in re.finditer(r'=[ \t]*new Menu\((.*?)(?:,|\))', code):
			var = m.group(1)
			pattern = r'^(public)[ \t]+'+var+r'[ \t]*\([ \t]*\w+[ \t]+'
			replace = r'\1 int '+var+r'(Menu '
			code = re.sub(pattern, replace, code, 0, re.M)

		# This one finds int vars in function declaration and adds `int` in front it the var
		code = reLoop(r'^(\w.+?\(.*)(?<=,|\()[ \t]*(&?[\w]+(?:\[\d+\])?[ \t]*(?:,|\)|=[ \t]*\-?(\d+|\w+)[ \t]*(?:\)|,)))(?=(?:[^{]*{[^}]*})*[^}]*$)(?=(?:[^"]*"[^"]*")*[^"]*$)', r'\1 int \2', code, re.M)

		# Redundancy check on removing colons from variables
		code = re.sub(r'^(\t*\w+)\:', r'\1 ', code, 0, re.M)

		# Format again. Remove extra spaces.
		code = re.sub(r'[ \t]*\n[ \t]*\{', r' {', code)
		code = re.sub(r'[ \t]+\]', r']', code)
		code = re.sub(r'\[[ \t]+', r'[', code)
		code = re.sub(r'[ \t]+\)', r')', code)
		code = re.sub(r'\([ \t]+', r'(', code)
		code = re.sub(r'[ \t]+\n', r'\n', code)


	with open(sys.argv[i], 'w', encoding='utf-8') as f:
		f.write(code)