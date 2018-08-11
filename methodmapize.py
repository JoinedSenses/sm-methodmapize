#!/usr/bin/python
# Methodmapizer for SourcePawn 1.7+
# Replaces all native calls with their equivalent methodmap call.
# By Peace-Maker
# Version 1.0

import sys
import re
import os.path

if len(sys.argv) < 2:
	print('Give at least one file to methodmapize: file1.sp file2.sp ...')
	sys.exit(1)

def replaceDataType(dataType, code):
	pattern = r'(\w+) = new ('+dataType+')'
	for m in re.finditer(pattern, code):
		var = m.group(1)
		var2 = m.group(2)
		pattern = r'(static )*Handle ' + var+r'\b'
		replacement = r'\1'+var2+" "+var
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

		print('Methodmapizing {}'.format(sys.argv[i]))
		
		# AdminId
		code = re.sub(r'(?<!\w)BindAdminIdentity\s*\(\s*([^\,]+)\s*,\s*', r'\1.BindIdentity(', code)
		code = re.sub(r'(?<!\w)CanAdminTarget\s*\(\s*([^\,]+)\s*,\s*', r'\1.CanTarget(', code)
		code = re.sub(r'(?<!\w)GetAdminFlags\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetFlags(', code)
		code = re.sub(r'(?<!\w)GetAdminGroup\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetGroup(', code)
		code = re.sub(r'(?<!\w)GetAdminPassword\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetPassword(', code)
		code = re.sub(r'(?<!\w)GetAdminFlag\s*\(\s*([^\,]+)\s*,\s*', r'\1.HasFlag(', code)
		code = re.sub(r'(?<!\w)AdminInheritGroup\s*\(\s*([^\,]+)\s*,\s*', r'\1.InheritGroup(', code)
		code = re.sub(r'(?<!\w)SetAdminPassword\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetPassword(', code)
		code = re.sub(r'(?<!\w)GetAdminGroupCount\s*\(\s*([^\)]+)\s*\)', r'\1\.GroupCount', code)
		code = re.sub(r'(?<!\w)GetAdminImmunityLevel\s*\(\s*([^\)]+)\s*\)', r'\1\.ImmunityLevel', code)
		code = re.sub(r'(?<!\w)SetAdminImmunityLevel\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.ImmunityLevel = \2', code)

		# GroupId
		code = re.sub(r'(?<!\w)AddAdmGroupCmdOverride\s*\(\s*([^\,]+)\s*,\s*', r'\1.AddCommandOverride(', code)
		code = re.sub(r'(?<!\w)SetAdmGroupImmuneFrom\s*\(\s*([^\,]+)\s*,\s*', r'\1.AddGroupImmunity(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupCmdOverride\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetCommandOverride(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupAddFlags\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetFlags(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupImmunity\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetGroupImmunity(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupAddFlag\s*\(\s*([^\,]+)\s*,\s*', r'\1.HasFlag(', code)
		code = re.sub(r'(?<!\w)SetAdmGroupAddFlag\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetFlag(', code)
		code = re.sub(r'(?<!\w)GetAdmGroupImmuneCount\s*\(\s*([^\)]+)\s*\)', r'\1\.GroupImmunitiesCount', code)
		code = re.sub(r'(?<!\w)GetAdmGroupImmunityLevel\s*\(\s*([^\)]+)\s*\)', r'\1\.ImmunityLevel', code)
		code = re.sub(r'(?<!\w)SetAdmGroupImmunityLevel\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.ImmunityLevel = \2', code)

		# ArrayList
		code = re.sub(r'\w+ (\w+) = CreateArray', r'ArrayList \1 = new Arraylist', code)
		code = re.sub(r'(?<!\w)ClearArray\s*\(\s*([^\)]+)\s*\)', r'\1.Clear()', code)
		code = re.sub(r'(?<!\w)CloneArray\s*\(\s*([^\)]+)\s*\)', r'\1.Clone()', code)
		code = re.sub(r'(?<!\w)CreateArray\s*\(\s*([^\)]*)\s*\)', r'new ArrayList(\1)', code)
		code = re.sub(r'(?<!\w)FindStringInArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.FindString(', code)
		code = re.sub(r'(?<!\w)FindValueInArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.FindValue(', code)
		code = re.sub(r'(?<!\w)GetArrayArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetArray(', code)
		code = re.sub(r'(?<!\w)GetArrayCell\s*\(\s*([^\,]+)\s*,\s*', r'\1.Get(', code)
		code = re.sub(r'(?<!\w)GetArraySize\s*\(\s*([^\)]+)\s*\)', r'\1.Length', code)
		code = re.sub(r'(?<!\w)GetArrayString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)PushArrayArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.PushArray(', code)
		code = re.sub(r'(?<!\w)PushArrayCell\s*\(\s*([^\,]+)\s*,\s*', r'\1.Push(', code)
		code = re.sub(r'(?<!\w)PushArrayString\s*\(\s*([^\,]+)\s*,\s*', r'\1.PushString(', code)
		code = re.sub(r'(?<!\w)RemoveFromArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.Erase(', code)
		code = re.sub(r'(?<!\w)ResizeArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.Resize(', code)
		code = re.sub(r'(?<!\w)SetArrayArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetArray(', code)
		code = re.sub(r'(?<!\w)SetArrayCell\s*\(\s*([^\,]+)\s*,\s*', r'\1.Set(', code)
		code = re.sub(r'(?<!\w)SetArrayString\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)ShiftArrayUp\s*\(\s*([^\,]+)\s*,\s*', r'\1.ShiftUp(', code)
		code = re.sub(r'(?<!\w)SwapArrayItems\s*\(\s*([^\,]+)\s*,\s*', r'\1.SwapAt(', code)

		# ArrayStack
		code = re.sub(r'\w+ (\w+) = CreateArray', r'ArrayList \1 = new ArrayStack', code)
		code = re.sub(r'(?<!\w)CreateStack\s*\(\s*([^\)]*)\s*\)', r'new ArrayStack(\1)', code)
		code = re.sub(r'(?<!\w)IsStackEmpty\s*\(\s*([^\)]+)\s*\)', r'\1.Empty', code)
		code = re.sub(r'(?<!\w)PopStackArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.PopArray(', code)
		code = re.sub(r'(?<!\w)PopStackCell\s*\(\s*([^\,]+)\s*,\s*', r'\1.Pop(', code)
		code = re.sub(r'(?<!\w)PopStackString\s*\(\s*([^\,]+)\s*,\s*', r'\1.PopString(', code)
		code = re.sub(r'(?<!\w)PushStackArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.PushArray(', code)
		code = re.sub(r'(?<!\w)PushStackCell\s*\(\s*([^\,]+)\s*,\s*', r'\1.Push(', code)
		code = re.sub(r'(?<!\w)PushStackString\s*\(\s*([^\,]+)\s*,\s*', r'\1.PushString(', code)

		# StringMap
		code = re.sub(r'(?<!\w)CreateTrie\s*\(\s*\)', r'new StringMap()', code)
		code = re.sub(r'(?<!\w)GetTrieSize\s*\(\s*([^\)]+)\s*\)', r'\1.Size', code)
		code = re.sub(r'(?<!\w)ClearTrie\s*\(\s*([^\)]+)\s*\)', r'\1.Clear()', code)
		code = re.sub(r'(?<!\w)GetTrieString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)SetTrieString\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)GetTrieValue\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetValue(', code)
		code = re.sub(r'(?<!\w)SetTrieValue\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetValue(', code)
		code = re.sub(r'(?<!\w)GetTrieArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetArray(', code)
		code = re.sub(r'(?<!\w)SetTrieArray\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetArray(', code)
		code = re.sub(r'(?<!\w)RemoveFromTrie\s*\(\s*([^\,]+)\s*,\s*', r'\1.Remove(', code)

		# StringMapSnapshot
		code = re.sub(r'(?<!\w)CreateTrieSnapshot\s*\(\s*([^\)]+)\s*\)', r'\1.Snapshot()', code)
		code = re.sub(r'(?<!\w)TrieSnapshotKeyBufferSize\s*\(\s*([^\,]+)\s*,\s*', r'\1.KeyBufferSize(', code)
		code = re.sub(r'(?<!\w)GetTrieSnapshotKey\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetKey(', code)
		code = re.sub(r'(?<!\w)TrieSnapshotLength\s*\(\s*([^\)]+)\s*\)', r'\1.Length', code)

		# TODO
		# BfRead
		# BfWrite

		# ConVar
		code = re.sub(r'(?<!\w)GetConVarBool\s*\(\s*([^\)]+)\s*\)', r'\1.BoolValue', code)
		code = re.sub(r'(?<!\w)GetConVarBounds\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetBounds(', code)
		code = re.sub(r'(?<!\w)GetConVarDefault\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetDefault(', code)
		code = re.sub(r'(?<!\w)GetConVarFlags\s*\(\s*([^\)]+)\s*\)', r'\1.Flags', code)
		code = re.sub(r'(?<!\w)GetConVarFloat\s*\(\s*([^\)]+)\s*\)', r'\1.FloatValue', code)
		code = re.sub(r'(?<!\w)GetConVarInt\((FindConVar\(.+?\)|.+?)\)', r'\1.IntValue', code)
		code = re.sub(r'(?<!\w)GetConVarName\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetName(', code)
		code = re.sub(r'(?<!\w)GetConVarString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)HookConVarChange\s*\(\s*([^\,]+)\s*,\s*', r'\1.AddChangeHook(', code)
		code = re.sub(r'(?<!\w)ResetConVar\s*\(\s*([^\,]+)\s*,\s*', r'\1.RestoreDefault(', code)
		code = re.sub(r'(?<!\w)SendConVarValue\s*\(\s*([^\,]+)\s*,\s*', r'\1.ReplicateToClient(', code)

		# Only use the method if the original call has more than 2 parameters.
		code = re.sub(r'(?<!\w)SetConVarBool\s*\(\s*([^\,]+)\s*,\s*([^\,]+)\s*,', r'\1.SetBool(\2,', code)
		code = re.sub(r'(?<!\w)SetConVarBool\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.BoolValue = \2', code)

		code = re.sub(r'(?<!\w)SetConVarBounds\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetBounds(', code)
		code = re.sub(r'(?<!\w)SetConVarFlags\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.Flags = \2', code)

		code = re.sub(r'(?<!\w)SetConVarFloat\s*\(\s*([^\,]+)\s*,\s*([^\,]+)\s*,', r'\1.SetFloat(\2,', code)
		code = re.sub(r'(?<!\w)SetConVarFloat\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.FloatValue = \2', code)
		code = re.sub(r'(?<!\w)SetConVarInt\s*\(\s*([^\,]+)\s*,\s*([^\,]+)\s*,', r'\1.SetInt(\2,', code)
		code = re.sub(r'(?<!\w)SetConVarInt\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.IntValue = \2', code)
		code = re.sub(r'(?<!\w)SetConVarString\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)UnhookConVarChange\s*\(\s*([^\,]+)\s*,\s*', r'\1.RemoveChangeHook(', code)

		# DataPack
		code = re.sub(r'\w+ (\w+) = CreateDataPack', r'DataPack \1 = new DataPack', code)
		code = re.sub(r'(?<!\w)CreateDataPack\s*\(\s*\)', r'new DataPack()', code)
		code = re.sub(r'(?<!\w)WritePackCell\s*\(\s*([^\,]+)\s*,\s*', r'\1.WriteCell(', code)
		code = re.sub(r'(?<!\w)WritePackFloat\s*\(\s*([^\,]+)\s*,\s*', r'\1.WriteFloat(', code)
		code = re.sub(r'(?<!\w)WritePackString\s*\(\s*([^\,]+)\s*,\s*', r'\1.WriteString(', code)
		code = re.sub(r'(?<!\w)WritePackFunction\s*\(\s*([^\,]+)\s*,\s*', r'\1.WriteFunction(', code)
		code = re.sub(r'(?<!\w)ReadPackCell\s*\(\s*([^\)]+)\s*\)', r'\1.ReadCell()', code)
		code = re.sub(r'(?<!\w)ReadPackFloat\s*\(\s*([^\)]+)\s*\)', r'\1.ReadFloat()', code)
		code = re.sub(r'(?<!\w)ReadPackString\s*\(\s*([^\,]+)\s*,\s*', r'\1.ReadString(', code)
		code = re.sub(r'(?<!\w)ReadPackFunction\s*\(\s*([^\)]+)\s*\)', r'\1.ReadFunction()', code)
		code = re.sub(r'(?<!\w)ResetPack\s*\(\s*([^\,\)]+)\s*,?\s*([^\)]*)\s*\)', r'\1.Reset(\2)', code)
		code = re.sub(r'(?<!\w)GetPackPosition\s*\(\s*([^\)]+)\s*\)', r'\1.Position', code)
		code = re.sub(r'(?<!\w)SetPackPosition\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.Position = \2', code)
		code = re.sub(r'(?<!\w)IsStackEmptyckReadable\s*\(\s*([^\,]+)\s*,\s*', r'\1.IsReadable(', code)

		# DBDriver
		code = re.sub(r'(?<!\w)SQL_GetDriver\s*\(', r'DBDriver.Find(', code)
		code = re.sub(r'(?<!\w)SQL_GetDriverProduct\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetProduct(', code)
		code = re.sub(r'(?<!\w)SQL_GetDriverIdent\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetIdentifier(', code)

		# DBResultSet
		code = re.sub(r'(?<!\w)SQL_FetchMoreResults\s*\(\s*([^\)]+)\s*\)', r'\1.FetchMoreResults()', code)
		code = re.sub(r'(?<!\w)SQL_HasResultSet\s*\(\s*([^\)]+)\s*\)', r'\1.HasResults', code)
		code = re.sub(r'(?<!\w)SQL_GetRowCount\s*\(\s*([^\)]+)\s*\)', r'\1.RowCount', code)
		code = re.sub(r'(?<!\w)SQL_GetFieldCount\s*\(\s*([^\)]+)\s*\)', r'\1.FieldCount', code)
		code = re.sub(r'(?<!\w)SQL_GetAffectedRows\s*\(\s*([^\)]+)\s*\)', r'\1.AffectedRows', code)
		code = re.sub(r'(?<!\w)SQL_GetInsertId\s*\(\s*([^\)]+)\s*\)', r'\1.InsertId', code)
		code = re.sub(r'(?<!\w)SQL_FieldNumToName\s*\(\s*([^\,]+)\s*,\s*', r'\1.FieldNumToName(', code)
		code = re.sub(r'(?<!\w)SQL_FieldNameToNum\s*\(\s*([^\,]+)\s*,\s*', r'\1.FieldNameToNum(', code)
		code = re.sub(r'(?<!\w)SQL_FetchRow\s*\(\s*([^\)]+)\s*\)', r'\1.FetchRow()', code)
		code = re.sub(r'(?<!\w)SQL_MoreRows\s*\(\s*([^\)]+)\s*\)', r'\1.MoreRows', code)
		code = re.sub(r'(?<!\w)SQL_Rewind\s*\(\s*([^\)]+)\s*\)', r'\1.Rewind()', code)
		code = re.sub(r'(?<!\w)SQL_FetchString\s*\(\s*([^\,]+)\s*,\s*', r'\1.FetchString(', code)
		code = re.sub(r'(?<!\w)SQL_FetchFloats*\(\s*([^\,]+)\s*,\s*', r'\1.FetchFloat(', code)
		code = re.sub(r'(?<!\w)SQL_FetchInt*\(\s*([^\,]+)\s*,\s*', r'\1.FetchInt(', code)
		code = re.sub(r'(?<!\w)SQL_IsFieldNull*\(\s*([^\,]+)\s*,\s*', r'\1.IsFieldNull(', code)
		code = re.sub(r'(?<!\w)SQL_FetchSize*\(\s*([^\,]+)\s*,\s*', r'\1.FetchSize(', code)

		# Transaction
		code = re.sub(r'(?<!\w)SQL_CreateTransaction\s*\(\s*\)', r'new Transaction()', code)
		code = re.sub(r'(?<!\w)SQL_AddQuery\s*\(\s*([^\,]+)\s*,\s*', r'\1.AddQuery(', code)

		# DBStatement
		code = re.sub(r'(?<!\w)SQL_BindParamInt\s*\(\s*([^\,]+)\s*,\s*', r'\1.BindInt(', code)
		code = re.sub(r'(?<!\w)SQL_BindParamFloat\s*\(\s*([^\,]+)\s*,\s*', r'\1.BindFloat(', code)
		code = re.sub(r'(?<!\w)SQL_BindParamString\s*\(\s*([^\,]+)\s*,\s*', r'\1.BindString(', code)

		# Database
		code = re.sub(r'(?<!\w)SQL_TConnect\s*\(', r'Database.Connect(', code)
		# Only replace if the optional ident argument isn't used.
		code = re.sub(r'(?<!\w)SQL_ReadDriver\s*\(\s*([^\)\,]+)\s*\)', r'\1.Driver', code)
		code = re.sub(r'(?<!\w)SQL_SetCharset\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetCharset(', code)
		code = re.sub(r'(?<!\w)SQL_EscapeString\s*\(\s*([^\,]+)\s*,\s*', r'\1.Escape(', code)
		code = re.sub(r'(?<!\w)SQL_FormatQuery\s*\(\s*([^\,]+)\s*,\s*', r'\1.Format(', code)
		code = re.sub(r'(?<!\w)SQL_IsSameConnection\s*\(\s*([^\,]+)\s*,\s*', r'\1.IsSameConnection(', code)
		code = re.sub(r'(?<!\w)SQL_TQuery\s*\(\s*([^\,]+)\s*,\s*', r'\1.Query(', code)
		code = re.sub(r'(?<!\w)SQL_ExecuteTransaction\s*\(\s*([^\,]+)\s*,\s*', r'\1.Execute(', code)

		# Event
		code = re.sub(r'(?<!\w)FireEvent\s*\(\s*([^\,\)]+)\s*,?\s*([^\)]*)\s*\)', r'\1.Fire(\2)', code)
		code = re.sub(r'(?<!\w)CancelCreatedEvent\s*\(\s*([^\)]+)\s*\)', r'\1.Cancel()', code)
		code = re.sub(r'(?<!\w)GetEventBool\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetBool(', code)
		code = re.sub(r'(?<!\w)SetEventBool\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetBool(', code)
		code = re.sub(r'(?<!\w)GetEventInt\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetInt(', code)
		code = re.sub(r'(?<!\w)SetEventInt\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetInt(', code)
		code = re.sub(r'(?<!\w)GetEventFloat\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetFloat(', code)
		code = re.sub(r'(?<!\w)SetEventFloat\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetFloat(', code)
		code = re.sub(r'(?<!\w)GetEventString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)SetEventString\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)GetEventName\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetName(', code)
		code = re.sub(r'(?<!\w)SetEventBroadcast\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.BroadcastDisabled = \2', code)

		# DirectoryListing
		code = re.sub(r'(?<!\w)ReadDirEntry\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetNext(', code)

		# File
		code = re.sub(r'(?<!\w)IsEndOfFile\s*\(\s*([^\)]+)\s*\)', r'\1.EndOfFile()', code)
		code = re.sub(r'(?<!\w)ReadFile\s*\(\s*([^\,]+)\s*,\s*', r'\1.Read(', code)
		code = re.sub(r'(?<!\w)ReadFileLine\s*\(\s*([^\,]+)\s*,\s*', r'\1.ReadLine(', code)
		code = re.sub(r'(?<!\w)ReadFileString\s*\(\s*([^\,]+)\s*,\s*', r'\1.ReadString(', code)
		code = re.sub(r'(?<!\w)FileSeek\s*\(\s*([^\,]+)\s*,\s*', r'\1.Seek(', code)
		code = re.sub(r'(?<!\w)WriteFile\s*\(\s*([^\,]+)\s*,\s*', r'\1.Write(', code)
		code = re.sub(r'(?<!\w)WriteFileLine\s*\(\s*([^\,]+)\s*,\s*', r'\1.WriteLine(', code)
		code = re.sub(r'(?<!\w)WriteStringLine\s*\(\s*([^\,]+)\s*,\s*', r'\1.WriteString(', code)
		code = re.sub(r'(?<!\w)FilePosition\s*\(\s*([^\)]+)\s*\)', r'\1.Position', code)
		# TODO: ReadFileCell & ReadIntX

		# Handles
		code = re.sub(r'(?<!\w)CloseHandle\s*\(\s*([^\)]+)\s*\)', r'delete \1', code)

		# KeyValues
		code = re.sub(r'\w+ (\w+) = CreateKeyValues', r'KeyValues \1 = new KeyValues', code)
		code = re.sub(r'(?<!\w)CreateKeyValues\s*\(\s*([^\)]+)\s*\)', r'new KeyValues(\1)', code)
		code = re.sub(r'(?<!\w)KvSetString\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetString(', code)
		code = re.sub(r'(?<!\w)KvSetNum\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetNum(', code)
		code = re.sub(r'(?<!\w)KvSetUInt64\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetUInt64(', code)
		code = re.sub(r'(?<!\w)KvSetFloat\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetFloat(', code)
		code = re.sub(r'(?<!\w)KvSetColor\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetColor(', code)
		code = re.sub(r'(?<!\w)KvSetVector\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetVector(', code)
		code = re.sub(r'(?<!\w)KvGetString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetString(', code)
		code = re.sub(r'(?<!\w)KvGetNum\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetNum(', code)
		code = re.sub(r'(?<!\w)KvGetFloat\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetFloat(', code)
		code = re.sub(r'(?<!\w)KvGetColor\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetColor(', code)
		code = re.sub(r'(?<!\w)KvGetUInt64\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetUInt64(', code)
		code = re.sub(r'(?<!\w)KvGetVector\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetVector(', code)
		code = re.sub(r'(?<!\w)KvJumpToKey\s*\(\s*([^\,]+)\s*,\s*', r'\1.JumpToKey(', code)
		code = re.sub(r'(?<!\w)KvJumpToKeySymbol\s*\(\s*([^\,]+)\s*,\s*', r'\1.JumpToKeySymbol(', code)
		code = re.sub(r'(?<!\w)KvGotoFirstSubKey\s*\(\s*([^\,\)]+)\s*,?\s*([^\)]*)\s*\)', r'\1.GotoFirstSubKey(\2)', code)
		code = re.sub(r'(?<!\w)KvGotoNextKey\s*\(\s*([^\,\)]+)\s*,?\s*([^\)]*)\s*\)', r'\1.GotoNextKey(\2)', code)
		code = re.sub(r'(?<!\w)KvSavePosition\s*\(\s*([^\)]+)\s*\)', r'\1.SavePosition()', code)
		code = re.sub(r'(?<!\w)KvDeleteKey\s*\(\s*([^\,]+)\s*,\s*', r'\1.DeleteKey(', code)
		code = re.sub(r'(?<!\w)KvDeleteThis\s*\(\s*([^\)]+)\s*\)', r'\1.DeleteThis()', code)
		code = re.sub(r'(?<!\w)KvGoBack\s*\(\s*([^\)]+)\s*\)', r'\1.GoBack()', code)
		code = re.sub(r'(?<!\w)KvRewind\s*\(\s*([^\)]+)\s*\)', r'\1.Rewind()', code)
		code = re.sub(r'(?<!\w)KvGetSectionName\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetSectionName(', code)
		code = re.sub(r'(?<!\w)KvSetSectionName\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetSectionName(', code)
		code = re.sub(r'(?<!\w)KvGetDataType\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetDataType(', code)
		code = re.sub(r'(?<!\w)KeyValuesToFile\s*\(\s*([^\,]+)\s*,\s*', r'\1.ExportToFile(', code)
		code = re.sub(r'(?<!\w)FileToKeyValues\s*\(\s*([^\,]+)\s*,\s*', r'\1.ImportFromFile(', code)
		code = re.sub(r'(?<!\w)StringToKeyValues\s*\(\s*([^\,]+)\s*,\s*', r'\1.ImportFromString(', code)
		code = re.sub(r'(?<!\w)KvSetEscapeSequences\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetEscapeSequences(', code)
		code = re.sub(r'(?<!\w)KvNodesInStack\s*\(\s*([^\)]+)\s*\)', r'\1.NodesInStack()', code)
		code = re.sub(r'(?<!\w)KvCopySubkeys\s*\(\s*([^\,]+)\s*,\s*', r'\1.Import(', code)
		code = re.sub(r'(?<!\w)KvFindKeyById\s*\(\s*([^\,]+)\s*,\s*', r'\1.FindKeyById(', code)
		code = re.sub(r'(?<!\w)KvGetNameSymbol\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetNameSymbol(', code)
		code = re.sub(r'(?<!\w)KvGetSectionSymbol\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetSectionSymbol(', code)
		
		# Menu
		code = re.sub(r'\w+ (\w+) = CreateMenu', r'Menu \1 = new Menu', code)
		code = re.sub(r'(?<!\w)CreateMenu\s*\(\s*([^\)]+)\s*\)', r'new Menu(\1)', code)
		code = re.sub(r'(?<!\w)DisplayMenu\s*\(\s*([^\,]+)\s*,\s*', r'\1.Display(', code)
		code = re.sub(r'(?<!\w)DisplayMenuAtItem\s*\(\s*([^\,]+)\s*,\s*', r'\1.DisplayAt(', code)
		code = re.sub(r'(?<!\w)AddMenuItem\s*\(\s*([^\,]+)\s*,\s*', r'\1.AddItem(', code)
		code = re.sub(r'(?<!\w)InsertMenuItem\s*\(\s*([^\,]+)\s*,\s*', r'\1.InsertItem(', code)
		code = re.sub(r'(?<!\w)RemoveMenuItem\s*\(\s*([^\,]+)\s*,\s*', r'\1.RemoveItem(', code)
		code = re.sub(r'(?<!\w)RemoveAllMenuItems\s*\(\s*([^\)]+)\s*\)', r'\1.RemoveAllItems()', code)
		code = re.sub(r'(?<!\w)GetMenuItem\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetItem(', code)
		code = re.sub(r'(?<!\w)GetMenuSelectionPosition\s*\(\s*([^\)]+)\s*\)', r'\1.Selection', code)
		code = re.sub(r'(?<!\w)GetMenuItemCount\s*\(\s*([^\)]+)\s*\)', r'\1.ItemCount', code)
		code = re.sub(r'(?<!\w)SetMenuPagination\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.Pagination = \2', code)
		code = re.sub(r'(?<!\w)GetMenuPagination\s*\(\s*([^\)]+)\s*\)', r'\1.Pagination', code)
		code = re.sub(r'(?<!\w)GetMenuStyle\s*\(\s*([^\)]+)\s*\)', r'\1.Style', code)
		code = re.sub(r'(?<!\w)SetMenuTitle\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetTitle(', code)
		code = re.sub(r'(?<!\w)GetMenuTitle\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetTitle(', code)
		code = re.sub(r'(?<!\w)CreatePanelFromMenu\s*\(\s*([^\)]+)\s*\)', r'\1.ToPanel()', code)
		code = re.sub(r'(?<!\w)GetMenuExitButton\s*\(\s*([^\)]+)\s*\)', r'\1.ExitButton', code)
		code = re.sub(r'(?<!\w)SetMenuExitButton\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.ExitButton = \2', code)
		code = re.sub(r'(?<!\w)GetMenuExitBackButton\s*\(\s*([^\)]+)\s*\)', r'\1.ExitBackButton', code)
		code = re.sub(r'(?<!\w)SetMenuExitBackButton\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.ExitBackButton = \2', code)
		code = re.sub(r'(?<!\w)SetMenuNoVoteButton\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.NoVoteButton = \2', code)
		code = re.sub(r'(?<!\w)CancelMenu\s*\(\s*([^\)]+)\s*\)', r'\1.Cancel()', code)
		code = re.sub(r'(?<!\w)GetMenuOptionFlags\s*\(\s*([^\)]+)\s*\)', r'\1.OptionFlags', code)
		code = re.sub(r'(?<!\w)SetMenuOptionFlags\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OptionFlags = \2', code)
		code = re.sub(r'(?<!\w)VoteMenu\s*\(\s*([^\,]+)\s*,\s*', r'\1.DisplayVote(', code)
		code = re.sub(r'(?<!\w)VoteMenuToAll\s*\(\s*([^\,]+)\s*,\s*', r'\1.DisplayVoteToAll(', code)
		code = re.sub(r'(?<!\w)SetVoteResultCallback\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.VoteResultCallback = \2', code)

		# Panel
		code = re.sub(r'\w+ (\w+) = CreatePanel', r'Panel \1 = new Panel', code)
		code = re.sub(r'(?<!\w)CreatePanel\s*\(\s*([^\)]*)\s*\)', r'new Panel(\1)', code)
		code = re.sub(r'(?<!\w)GetPanelStyle\s*\(\s*([^\)]+)\s*\)', r'\1.Style', code)
		code = re.sub(r'(?<!\w)SetPanelTitle\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetTitle(', code)
		code = re.sub(r'(?<!\w)DrawPanelItem\s*\(\s*([^\,]+)\s*,\s*', r'\1.DrawItem(', code)
		code = re.sub(r'(?<!\w)DrawPanelText\s*\(\s*([^\,]+)\s*,\s*', r'\1.DrawText(', code)
		code = re.sub(r'(?<!\w)CanPanelDrawFlags\s*\(\s*([^\,]+)\s*,\s*', r'\1.CanDrawFlags(', code)
		code = re.sub(r'(?<!\w)SetPanelKeys\s*\(\s*([^\,]+)\s*,\s*', r'\1.SetKeys(', code)
		code = re.sub(r'(?<!\w)SendPanelToClient\s*\(\s*([^\,]+)\s*,\s*', r'\1.Send(', code)
		code = re.sub(r'(?<!\w)GetPanelTextRemaining\s*\(\s*([^\)]+)\s*\)', r'\1.TextRemaining', code)
		code = re.sub(r'(?<!\w)GetPanelCurrentKey\s*\(\s*([^\)]+)\s*\)', r'\1.CurrentKey', code)
		code = re.sub(r'(?<!\w)SetPanelCurrentKey\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.CurrentKey = \2', code)

		# TODO: Protobuf

		# Regex
		code = re.sub(r'\w+ (\w+) = CompileRegex', r'Regex \1 = new Regex', code)
		code = re.sub(r'(?<!\w)CompileRegex\s*\(\s*([^\)]*)\s*\)', r'new Regex(\1)', code)
		code = re.sub(r'(?<!\w)MatchRegex\s*\(\s*([^\,]+)\s*,\s*', r'\1.Match(', code)
		code = re.sub(r'(?<!\w)GetRegexSubString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetSubString(', code)

		# SMCParser
		code = re.sub(r'\w+ (\w+) = SMC_CreateParser', r'SMCParser \1 = new SMCParser', code)
		code = re.sub(r'(?<!\w)SMC_CreateParser\s*\(\s*\)', r'new SMCParser()', code)
		code = re.sub(r'(?<!\w)SMC_ParseFile\s*\(\s*([^\,]+)\s*,\s*', r'\1.ParseFile(', code)
		code = re.sub(r'(?<!\w)SMC_SetParseStart\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OnStart = \2', code)
		code = re.sub(r'(?<!\w)SMC_SetParseEnd\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OnEnd = \2', code)
		# TODO: Split up into 3 seperate lines?
		#code = re.sub(r'(?<!\w)SMC_SetReaders\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OnEnterSection = \2', code)
		#code = re.sub(r'(?<!\w)SetPanelCurrentKey\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OnLeaveSection = \2', code)
		#code = re.sub(r'(?<!\w)SetPanelCurrentKey\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OnKeyValue = \2', code)
		code = re.sub(r'(?<!\w)SMC_SetRawLine\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.OnRawLine = \2', code)
		code = re.sub(r'(?<!\w)SMC_GetErrorString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetErrorString(', code)

		# TopMenu
		code = re.sub(r'\w+ (\w+) = CreateTopMenu', r'TopMenu \1 = new TopMenu', code)
		code = re.sub(r'(?<!\w)CreateTopMenu\s*\(\s*([^\)]*)\s*\)', r'new TopMenu(\1)', code)
		code = re.sub(r'(?<!\w)LoadTopMenuConfig\s*\(\s*([^\,]+)\s*,\s*', r'\1.LoadConfig(', code)
		code = re.sub(r'(?<!\w)AddToTopMenu\s*\(\s*([^\,]+)\s*,\s*([^\,]+)\s*,\s*TopMenuObject_Category', r'\1.AddCategory(\2, ', code)
		code = re.sub(r'(?<!\w)AddToTopMenu\s*\(\s*([^\,]+)\s*,\s*([^\,]+)\s*,\s*TopMenuObject_Item', r'\1.AddItem(\2, ', code)
		code = re.sub(r'(?<!\w)GetTopMenuInfoString\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetInfoString(', code)
		code = re.sub(r'(?<!\w)GetTopMenuObjName\s*\(\s*([^\,]+)\s*,\s*', r'\1.GetObjName(', code)
		code = re.sub(r'(?<!\w)RemoveFromTopMenu\s*\(\s*([^\,]+)\s*,\s*', r'\1.Remove(', code)
		code = re.sub(r'(?<!\w)DisplayTopMenu\s*\(\s*([^\,]+)\s*,\s*', r'\1.Display(', code)
		code = re.sub(r'(?<!\w)DisplayTopMenuCategory\s*\(\s*([^\,]+)\s*,\s*', r'\1.DisplayCategory(', code)
		code = re.sub(r'(?<!\w)FindTopMenuCategory\s*\(\s*([^\,]+)\s*,\s*', r'\1.FindCategory(', code)
		code = re.sub(r'(?<!\w)SetTopMenuTitleCaching\s*\(\s*([^\,]+)\s*,\s*([^\)]+)\s*\)', r'\1.CacheTitles = \2', code)

		# _: int retagging
		code = re.sub(r'(?<!\w)(?<!\w)_:(.*?)(,\s*|[)]+)', r'view_as<int>(\1)\2', code)
		
		dataTypes = ["ArrayList", "ArrayStack", "StringMap", "DataPack", "Transaction", "KeyValues", "Menu", "Panel", "Regex", "SMCParser", "TopMenu"]
		for dataType in dataTypes:
			code = replaceDataType(dataType, code)

	with open(sys.argv[i] + '.m', 'w', encoding='utf-8') as f:
		f.write(code)
