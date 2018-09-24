#!/usr/bin/python
# Methodmapizer for SourcePawn 1.7+
# Replaces all native calls with their equivalent methodmap call.
# Replaces old syntax declarations with new syntax
# By Peace-Maker, JoinedSenses
# Version 1.1


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
		replacement = r'File[ \t]+' + var
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
		code = re.sub(r'(^\w.*?)[ \t]*(?<!:)(\/\/.*?)({)', r'\2\n\1 \3', code, 0, re.M)
		code = re.sub(r'(^\w.*?)[ \t]*(?<!:)(\/\/.*?$)', r'\2\n\1', code, 0, re.M)
		code = re.sub(r'(^\t+)(\w.*;)[ \t]*(})', r'\1\2\n\1\3', code, 0, re.M)
		code = re.sub(r'(^\t+)(\w.*?(?:\:|\))[ \t]*\{) *(\w)', r'\1\2\n\1\t\3', code, 0, re.M)
		code = re.sub(r'(^\t+)(\w.*;)[ \t]*(?<!:)(\/\/[ \t]*$)', r'\1\2', code, 0, re.M)
		code = re.sub(r'(^\t+)(\w.*)([ \t]*)(?<!:)(\/\/.*$)', r'\1\4\n\1\2', code, 0, re.M)
		code = reLoop(r'(^\t+)(\w.*?;)[ \t]+([^)}\n]+$)', r'\1\2\n\1\3', code, re.M)
		# CODE NOW MORE PRETTY
		# *****************************************************************************

		print('Methodmapizing {}'.format(sys.argv[i]))

		# AdminId
		code = re.sub(r'(?<!\w)BindAdminIdentity[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindIdentity(', code)
		code = re.sub(r'(?<!\w)CanAdminTarget[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.CanTarget(', code)
		code = re.sub(r'(?<!\w)GetAdminFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFlags(', code)
		code = re.sub(r'(?<!\w)GetAdminGroup[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetGroup(', code)
		code = re.sub(r'(?<!\w)GetAdminPassword[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetPassword(', code)
		code = re.sub(r'(?<!\w)GetAdminFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.HasFlag(', code)
		code = re.sub(r'(?<!\w)AdminInheritGroup[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.InheritGroup(', code)
		code = re.sub(r'(?<!\w)SetAdminPassword[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetPassword(', code)
		code = re.sub(r'(?<!\w)GetAdminGroupCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.GroupCount', code)
		code = re.sub(r'(?<!\w)GetAdminImmunityLevel[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.ImmunityLevel', code)
		code = re.sub(r'(?<!\w)SetAdminImmunityLevel[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ImmunityLevel = \2', code)

		# GroupId
		code = re.sub(r'(?<!\w)AddAdmGroupCmdOverride[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddCommandOverride(', code)
		code = re.sub(r'(?<!\w)SetAdmGroupImmuneFrom[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddGroupImmunity(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupCmdOverride[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetCommandOverride(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupAddFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFlags(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupImmunity[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetGroupImmunity(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupAddFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.HasFlag(', code)
		code = re.sub(r'(?<!\w)SetAdmGroupAddFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFlag(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupImmuneCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.GroupImmunitiesCount', code)
		code = re.sub(r'(?<!\w)GetAdmGroupImmunityLevel[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.ImmunityLevel', code)
		code = re.sub(r'(?<!\w)SetAdmGroupImmunityLevel[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ImmunityLevel = \2', code)

		# ArrayList
		code = re.sub(r'(?<!\w)ClearArray[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clear()', code)
		code = re.sub(r'(?<!\w)CloneArray[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clone()', code)
		code = re.sub(r'(?<!\w)CreateArray[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new ArrayList(\1)', code)
		code = re.sub(r'(?<!\w)FindStringInArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindString(', code)
		code = re.sub(r'(?<!\w)FindValueInArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindValue(', code)
		code = re.sub(r'(?<!\w)GetArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetArray(', code)
		code = re.sub(r'(?<!\w)GetArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Get(', code)
		code = re.sub(r'(?<!\w)GetArraySize[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Length', code)
		code = re.sub(r'(?<!\w)GetArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)PushArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushArray(', code)
		code = re.sub(r'(?<!\w)PushArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Push(', code)
		code = re.sub(r'(?<!\w)PushArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushString(', code)
		code = re.sub(r'(?<!\w)RemoveFromArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Erase(', code)
		code = re.sub(r'(?<!\w)ResizeArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Resize(', code)
		code = re.sub(r'(?<!\w)SetArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetArray(', code)
		code = re.sub(r'(?<!\w)SetArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Set(', code)
		code = re.sub(r'(?<!\w)SetArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)ShiftArrayUp[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ShiftUp(', code)
		code = re.sub(r'(?<!\w)SwapArrayItems[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SwapAt(', code)

		# ArrayStack
		code = re.sub(r'(?<!\w)CreateStack[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new ArrayStack(\1)', code)
		code = re.sub(r'(?<!\w)IsStackEmpty[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Empty', code)
		code = re.sub(r'(?<!\w)PopStackArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PopArray(', code)
		code = re.sub(r'(?<!\w)PopStackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Pop(', code)
		code = re.sub(r'(?<!\w)PopStackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PopString(', code)
		code = re.sub(r'(?<!\w)PushStackArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushArray(', code)
		code = re.sub(r'(?<!\w)PushStackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Push(', code)
		code = re.sub(r'(?<!\w)PushStackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushString(', code)

		# StringMap
		code = re.sub(r'(?<!\w)CreateTrie[ \t]*\([ \t]*\)', r'new StringMap()', code)
		code = re.sub(r'(?<!\w)GetTrieSize[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Size', code)
		code = re.sub(r'(?<!\w)ClearTrie[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clear()', code)
		code = re.sub(r'(?<!\w)GetTrieString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)SetTrieString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)GetTrieValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetValue(', code)
		code = re.sub(r'(?<!\w)SetTrieValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetValue(', code)
		code = re.sub(r'(?<!\w)GetTrieArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetArray(', code)
		code = re.sub(r'(?<!\w)SetTrieArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetArray(', code)
		code = re.sub(r'(?<!\w)RemoveFromTrie[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Remove(', code)

		# StringMapSnapshot
		code = re.sub(r'(?<!\w)CreateTrieSnapshot[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Snapshot()', code)
		code = re.sub(r'(?<!\w)TrieSnapshotKeyBufferSize[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.KeyBufferSize(', code)
		code = re.sub(r'(?<!\w)GetTrieSnapshotKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetKey(', code)
		code = re.sub(r'(?<!\w)TrieSnapshotLength[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Length', code)

		# TODO
		# BfRead
		# BfWrite

		# ConVar
		code = re.sub(r'(?<!\w)GetConVarBool[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.BoolValue', code)
		code = re.sub(r'(?<!\w)GetConVarBounds[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetBounds(', code)
		code = re.sub(r'(?<!\w)GetConVarDefault[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetDefault(', code)
		code = re.sub(r'(?<!\w)GetConVarFlags[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Flags', code)
		code = re.sub(r'(?<!\w)GetConVarFloat[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FloatValue', code)
		code = re.sub(r'(?<!\w)GetConVarInt\((FindConVar\(.+?\)|.+?)\)', r'\1.IntValue', code)
		code = re.sub(r'(?<!\w)GetConVarName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetName(', code)
		code = re.sub(r'(?<!\w)GetConVarString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)HookConVarChange[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddChangeHook(', code)
		code = re.sub(r'(?<!\w)ResetConVar[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RestoreDefault(', code)
		code = re.sub(r'(?<!\w)SendConVarValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReplicateToClient(', code)

		# Only use the method if the original call has more than 2 parameters.
		code = re.sub(r'(?<!\w)SetConVarBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetBool(\2,', code)
		code = re.sub(r'(?<!\w)SetConVarBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.BoolValue = \2', code)

		code = re.sub(r'(?<!\w)SetConVarBounds[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetBounds(', code)
		code = re.sub(r'(?<!\w)SetConVarFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Flags = \2', code)

		code = re.sub(r'(?<!\w)SetConVarFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetFloat(\2,', code)
		code = re.sub(r'(?<!\w)SetConVarFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.FloatValue = \2', code)
		code = re.sub(r'(?<!\w)SetConVarInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetInt(\2,', code)
		code = re.sub(r'(?<!\w)SetConVarInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.IntValue = \2', code)
		code = re.sub(r'(?<!\w)SetConVarString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)UnhookConVarChange[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveChangeHook(', code)

		# DataPack
		code = re.sub(r'(?<!\w)CreateDataPack[ \t]*\([ \t]*\)', r'new DataPack()', code)
		code = re.sub(r'(?<!\w)WritePackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteCell(', code)
		code = re.sub(r'(?<!\w)WritePackFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteFloat(', code)
		code = re.sub(r'(?<!\w)WritePackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteString(', code)
		code = re.sub(r'(?<!\w)WritePackFunction[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteFunction(', code)
		code = re.sub(r'(?<!\w)ReadPackCell[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadCell()', code)
		code = re.sub(r'(?<!\w)ReadPackFloat[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadFloat()', code)
		code = re.sub(r'(?<!\w)ReadPackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadString(', code)
		code = re.sub(r'(?<!\w)ReadPackFunction[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadFunction()', code)
		code = re.sub(r'(?<!\w)ResetPack[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.Reset(\2)', code)
		code = re.sub(r'(?<!\w)GetPackPosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Position', code)
		code = re.sub(r'(?<!\w)SetPackPosition[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Position = \2', code)
		code = re.sub(r'(?<!\w)IsStackEmptyckReadable[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsReadable(', code)

		# DBDriver
		code = re.sub(r'(?<!\w)SQL_GetDriver[ \t]*\(', r'DBDriver.Find(', code)
		code = re.sub(r'(?<!\w)SQL_GetDriverProduct[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetProduct(', code)
		code = re.sub(r'(?<!\w)SQL_GetDriverIdent[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetIdentifier(', code)

		# DBResultSet
		code = re.sub(r'(?<!\w)SQL_FetchMoreResults[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FetchMoreResults()', code)
		code = re.sub(r'(?<!\w)SQL_HasResultSet[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.HasResults', code)
		code = re.sub(r'(?<!\w)SQL_GetRowCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.RowCount', code)
		code = re.sub(r'(?<!\w)SQL_GetFieldCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FieldCount', code)
		code = re.sub(r'(?<!\w)SQL_GetAffectedRows[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.AffectedRows', code)
		code = re.sub(r'(?<!\w)SQL_GetInsertId[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.InsertId', code)
		code = re.sub(r'(?<!\w)SQL_FieldNumToName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FieldNumToName(', code)
		code = re.sub(r'(?<!\w)SQL_FieldNameToNum[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FieldNameToNum(', code)
		code = re.sub(r'(?<!\w)SQL_FetchRow[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FetchRow()', code)
		code = re.sub(r'(?<!\w)SQL_MoreRows[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.MoreRows', code)
		code = re.sub(r'(?<!\w)SQL_Rewind[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Rewind()', code)
		code = re.sub(r'(?<!\w)SQL_FetchString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchString(', code)
		code = re.sub(r'(?<!\w)SQL_FetchFloats*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchFloat(', code)
		code = re.sub(r'(?<!\w)SQL_FetchInt*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchInt(', code)
		code = re.sub(r'(?<!\w)SQL_IsFieldNull*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsFieldNull(', code)
		code = re.sub(r'(?<!\w)SQL_FetchSize*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchSize(', code)

		# Transaction
		code = re.sub(r'(?<!\w)SQL_CreateTransaction[ \t]*\([ \t]*\)', r'new Transaction()', code)
		code = re.sub(r'(?<!\w)SQL_AddQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddQuery(', code)

		# DBStatement
		code = re.sub(r'(?<!\w)SQL_BindParamInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindInt(', code)
		code = re.sub(r'(?<!\w)SQL_BindParamFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindFloat(', code)
		code = re.sub(r'(?<!\w)SQL_BindParamString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindString(', code)

		# Database
		code = re.sub(r'(?<!\w)SQL_TConnect[ \t]*\(', r'Database.Connect(', code)
		# Only replace if the optional ident argument isn't used.
		code = re.sub(r'(?<!\w)SQL_ReadDriver[ \t]*\([ \t]*([^\)\,]+)[ \t]*\)', r'\1.Driver', code)
		code = re.sub(r'(?<!\w)SQL_SetCharset[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetCharset(', code)
		code = re.sub(r'(?<!\w)SQL_EscapeString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Escape(', code)
		code = re.sub(r'(?<!\w)SQL_FormatQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Format(', code)
		code = re.sub(r'(?<!\w)SQL_IsSameConnection[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsSameConnection(', code)
		code = re.sub(r'(?<!\w)SQL_TQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Query(', code)
		code = re.sub(r'(?<!\w)SQL_ExecuteTransaction[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Execute(', code)

		# Event
		code = re.sub(r'(?<!\w)FireEvent[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.Fire(\2)', code)
		code = re.sub(r'(?<!\w)CancelCreatedEvent[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Cancel()', code)
		code = re.sub(r'(?<!\w)GetEventBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetBool(', code)
		code = re.sub(r'(?<!\w)SetEventBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetBool(', code)
		code = re.sub(r'(?<!\w)GetEventInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetInt(', code)
		code = re.sub(r'(?<!\w)SetEventInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetInt(', code)
		code = re.sub(r'(?<!\w)GetEventFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFloat(', code)
		code = re.sub(r'(?<!\w)SetEventFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFloat(', code)
		code = re.sub(r'(?<!\w)GetEventString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)SetEventString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)GetEventName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetName(', code)
		code = re.sub(r'(?<!\w)SetEventBroadcast[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.BroadcastDisabled = \2', code)

		# DirectoryListing
		code = re.sub(r'(?<!\w)\w+[ \t]+(.*?)[ \t]*=[ \t]*(OpenDirectory)', r'DirectoryListing \1 = \2', code)
		code = re.sub(r'(?<!\w)ReadDirEntry[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetNext(', code)

		# File
		code = re.sub(r'(?<!\w)IsEndOfFile[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.EndOfFile()', code)
		code = re.sub(r'(?<!\w)ReadFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Read(', code)
		code = re.sub(r'(?<!\w)ReadFileLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadLine(', code)
		code = re.sub(r'(?<!\w)ReadFileString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadString(', code)
		code = re.sub(r'(?<!\w)FileSeek[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Seek(', code)
		code = re.sub(r'(?<!\w)WriteFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Write(', code)
		code = re.sub(r'(?<!\w)WriteFileLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteLine(', code)
		code = re.sub(r'(?<!\w)WriteStringLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteString(', code)
		code = re.sub(r'(?<!\w)FilePosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Position', code)
		# TODO: ReadFileCell & ReadIntX

		# Handles
		code = re.sub(r'(?<!\w)CloseHandle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'delete \1', code)

		# KeyValues
		code = re.sub(r'(?<!\w)CreateKeyValues[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'new KeyValues(\1)', code)
		code = re.sub(r'(?<!\w)KvSetString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)KvSetNum[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetNum(', code)
		code = re.sub(r'(?<!\w)KvSetUInt64[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetUInt64(', code)
		code = re.sub(r'(?<!\w)KvSetFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFloat(', code)
		code = re.sub(r'(?<!\w)KvSetColor[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetColor(', code)
		code = re.sub(r'(?<!\w)KvSetVector[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetVector(', code)
		code = re.sub(r'(?<!\w)KvGetString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)KvGetNum[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*', r'\1.GetNum(', code)
		code = re.sub(r'(?<!\w)KvGetFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFloat(', code)
		code = re.sub(r'(?<!\w)KvGetColor[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetColor(', code)
		code = re.sub(r'(?<!\w)KvGetUInt64[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetUInt64(', code)
		code = re.sub(r'(?<!\w)KvGetVector[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetVector(', code)
		code = re.sub(r'(?<!\w)KvJumpToKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.JumpToKey(', code)
		code = re.sub(r'(?<!\w)KvJumpToKeySymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.JumpToKeySymbol(', code)
		code = re.sub(r'(?<!\w)KvGotoFirstSubKey[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.GotoFirstSubKey(\2)', code)
		code = re.sub(r'(?<!\w)KvGotoNextKey[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.GotoNextKey(\2)', code)
		code = re.sub(r'(?<!\w)KvSavePosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.SavePosition()', code)
		code = re.sub(r'(?<!\w)KvDeleteKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DeleteKey(', code)
		code = re.sub(r'(?<!\w)KvDeleteThis[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.DeleteThis()', code)
		code = re.sub(r'(?<!\w)KvGoBack[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.GoBack()', code)
		code = re.sub(r'(?<!\w)KvRewind[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Rewind()', code)
		code = re.sub(r'(?<!\w)KvGetSectionName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSectionName(', code)
		code = re.sub(r'(?<!\w)KvSetSectionName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetSectionName(', code)
		code = re.sub(r'(?<!\w)KvGetDataType[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetDataType(', code)
		code = re.sub(r'(?<!\w)KeyValuesToFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ExportToFile(', code)
		code = re.sub(r'(?<!\w)FileToKeyValues[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ImportFromFile(', code)
		code = re.sub(r'(?<!\w)StringToKeyValues[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ImportFromString(', code)
		code = re.sub(r'(?<!\w)KvSetEscapeSequences[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetEscapeSequences(', code)
		code = re.sub(r'(?<!\w)KvNodesInStack[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.NodesInStack()', code)
		code = re.sub(r'(?<!\w)KvCopySubkeys[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Import(', code)
		code = re.sub(r'(?<!\w)KvFindKeyById[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindKeyById(', code)
		code = re.sub(r'(?<!\w)KvGetNameSymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetNameSymbol(', code)
		code = re.sub(r'(?<!\w)KvGetSectionSymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSectionSymbol(', code)
		
		# Menu
		code = re.sub(r'(?<!\w)CreateMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'new Menu(\1)', code)
		code = re.sub(r'(?<!\w)DisplayMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Display(', code)
		code = re.sub(r'(?<!\w)DisplayMenuAtItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayAt(', code)
		code = re.sub(r'(?<!\w)AddMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddItem(', code)
		code = re.sub(r'(?<!\w)InsertMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.InsertItem(', code)
		code = re.sub(r'(?<!\w)RemoveMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveItem(', code)
		code = re.sub(r'(?<!\w)RemoveAllMenuItems[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.RemoveAllItems()', code)
		code = re.sub(r'(?<!\w)GetMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetItem(', code)
		code = re.sub(r'(?<!\w)GetMenuSelectionPosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Selection', code)
		code = re.sub(r'(?<!\w)GetMenuItemCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ItemCount', code)
		code = re.sub(r'(?<!\w)SetMenuPagination[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Pagination = \2', code)
		code = re.sub(r'(?<!\w)GetMenuPagination[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Pagination', code)
		code = re.sub(r'(?<!\w)GetMenuStyle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Style', code)
		code = re.sub(r'(?<!\w)SetMenuTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetTitle(', code)
		code = re.sub(r'(?<!\w)GetMenuTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetTitle(', code)
		code = re.sub(r'(?<!\w)CreatePanelFromMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ToPanel()', code)
		code = re.sub(r'(?<!\w)GetMenuExitButton[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ExitButton', code)
		code = re.sub(r'(?<!\w)SetMenuExitButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ExitButton = \2', code)
		code = re.sub(r'(?<!\w)GetMenuExitBackButton[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ExitBackButton', code)
		code = re.sub(r'(?<!\w)SetMenuExitBackButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ExitBackButton = \2', code)
		code = re.sub(r'(?<!\w)SetMenuNoVoteButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.NoVoteButton = \2', code)
		code = re.sub(r'(?<!\w)CancelMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Cancel()', code)
		code = re.sub(r'(?<!\w)GetMenuOptionFlags[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.OptionFlags', code)
		code = re.sub(r'(?<!\w)SetMenuOptionFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OptionFlags = \2', code)
		code = re.sub(r'(?<!\w)VoteMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayVote(', code)
		code = re.sub(r'(?<!\w)VoteMenuToAll[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayVoteToAll(', code)
		code = re.sub(r'(?<!\w)SetVoteResultCallback[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.VoteResultCallback = \2', code)

		# Panel
		code = re.sub(r'(?<!\w)CreatePanel[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new Panel(\1)', code)
		code = re.sub(r'(?<!\w)GetPanelStyle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Style', code)
		code = re.sub(r'(?<!\w)SetPanelTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetTitle(', code)
		code = re.sub(r'(?<!\w)DrawPanelItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DrawItem(', code)
		code = re.sub(r'(?<!\w)DrawPanelText[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DrawText(', code)
		code = re.sub(r'(?<!\w)CanPanelDrawFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.CanDrawFlags(', code)
		code = re.sub(r'(?<!\w)SetPanelKeys[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetKeys(', code)
		code = re.sub(r'(?<!\w)SendPanelToClient[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Send(', code)
		code = re.sub(r'(?<!\w)GetPanelTextRemaining[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.TextRemaining', code)
		code = re.sub(r'(?<!\w)GetPanelCurrentKey[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.CurrentKey', code)
		code = re.sub(r'(?<!\w)SetPanelCurrentKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.CurrentKey = \2', code)

		# TODO: Protobuf

		# Regex
		code = re.sub(r'(?<!\w)CompileRegex[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new Regex(\1)', code)
		code = re.sub(r'(?<!\w)MatchRegex[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Match(', code)
		code = re.sub(r'(?<!\w)GetRegexSubString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSubString(', code)

		# SMCParser
		code = re.sub(r'(?<!\w)SMC_CreateParser[ \t]*\([ \t]*\)', r'new SMCParser()', code)
		code = re.sub(r'(?<!\w)SMC_ParseFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ParseFile(', code)
		code = re.sub(r'(?<!\w)SMC_SetParseStart[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnStart = \2', code)
		code = re.sub(r'(?<!\w)SMC_SetParseEnd[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnEnd = \2', code)
		code = re.sub(r'([ \t]+)SMC_SetReaders\((\w+),[ \t]*(\w+),[ \t]*(\w+),[ \t]*(\w+).*', r'\1\2.OnEnterSection = \3;\n\1\2.OnKeyValue = \4;\n\1\2.OnLeaveSection = \5;', code)
		code = re.sub(r'(?<!\w)SMC_SetRawLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnRawLine = \2', code)
		code = re.sub(r'(?<!\w)SMC_GetErrorString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetErrorString(', code)

		# TopMenu
		code = re.sub(r'(?<!\w)CreateTopMenu[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new TopMenu(\1)', code)
		code = re.sub(r'(?<!\w)LoadTopMenuConfig[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.LoadConfig(', code)
		code = re.sub(r'(?<!\w)AddToTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,[ \t]*TopMenuObject_Category', r'\1.AddCategory(\2, ', code)
		code = re.sub(r'(?<!\w)AddToTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,[ \t]*TopMenuObject_Item', r'\1.AddItem(\2, ', code)
		code = re.sub(r'(?<!\w)GetTopMenuInfoString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetInfoString(', code)
		code = re.sub(r'(?<!\w)GetTopMenuObjName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetObjName(', code)
		code = re.sub(r'(?<!\w)RemoveFromTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Remove(', code)
		code = re.sub(r'(?<!\w)DisplayTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Display(', code)
		code = re.sub(r'(?<!\w)DisplayTopMenuCategory[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayCategory(', code)
		code = re.sub(r'(?<!\w)FindTopMenuCategory[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindCategory(', code)
		code = re.sub(r'(?<!\w)SetTopMenuTitleCaching[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.CacheTitles = \2', code)



		# --------------------------------------------------------------------------------------------------------------------------------
		# GENERAL SYNTAX UPDATES
		print('Updating syntax on {}'.format(sys.argv[i]))

		# _: int retagging
		code = re.sub(r'(?<!\w)_:(.*?)(,[ \t]*|[)]+|;)', r'view_as<int>(\1)\2', code)

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
		# socket(even though this directly SM, I've included it)
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

		code = re.sub(r'iClient', r'client', code)

		# Check to remove unrequired var type in BuildPath (idk, i saw a plugin do this, so i added it)
		code = re.sub(r'(BuildPath\()[ \t]*PathType:*', r'\1', code)

		# String:whatever[] -> char[] whatever
		code = re.sub(r'String:*(\w+)(\[\])', r'char\2 \1', code)

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
		code = reLoop(r'^([ \t]*)(new\b(?!.*=[ \t]*\w+[ \t]*\()[^(\n]+)(.*?\),|,[ \t]*)(.*?)(;|,[ \t]*)', r'\1\2;\n\1\4;\1', code, re.M)
		code = re.sub(r'^([ \t]*)new[ \t]+(\w+[ \t:]+\w)', r'\1\2', code, 0, re.M)
		# ************************************************************************************

		code = re.sub(r'(?<!\w)GetClientAuthString\([ \t]*(.*?,)', r'GetClientAuthId(\1 AuthId_Steam2,', code)

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

		dataTypes = ["ArrayList", "ArrayStack", "StringMap", "DataPack", "Transaction", "KeyValues", "Menu", "Panel", "Regex", "SMCParser", "TopMenu"]
		for dataType in dataTypes:
			code = replaceDataType(dataType, code)

		# Handle var -> ArrayList var
		for m in re.finditer(r'(\w+)[ \t]*=[ \t]*GetNativeCell', code):
			var = m.group(1)
			pattern = r'Handle[ \t]+'+var+r'\b'
			replace = r'ArrayList '+var
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
