#!/usr/bin/python
# Methodmapizer for SourcePawn 1.7+
# Replaces all native calls with their equivalent methodmap call.
# By Peace-Maker, JoinedSenses
# Version 1.2


# NOTE: DO NOT BLINDLY RELY ON THIS SCRIPT. 
# ALWAYS DIFFCHECK CHANGES

import sys
import re
import os.path


if len(sys.argv) < 2:
	print('Give at least one file to methodmapize: file1.sp file2.sp ...')
	sys.exit(1)


REPLACEMEMTS = lambda : [
	# AdminId
	(r'\bBindAdminIdentity[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindIdentity('),
	(r'\bCanAdminTarget[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.CanTarget('),
	(r'\bGetAdminFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFlags('),
	(r'\bGetAdminGroup[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetGroup('),
	(r'\bGetAdminPassword[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetPassword('),
	(r'\bGetAdminFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.HasFlag('),
	(r'\bAdminInheritGroup[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.InheritGroup('),
	(r'\bSetAdminPassword[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetPassword('),
	(r'\bGetAdminGroupCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.GroupCount'),
	(r'\bGetAdminImmunityLevel[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.ImmunityLevel'),
	(r'\bSetAdminImmunityLevel[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ImmunityLevel = \2'),

	#GroupId
	(r'\bAddAdmGroupCmdOverride[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddCommandOverride('),
	(r'\bSetAdmGroupImmuneFrom[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddGroupImmunity('),
	(r'\bGetAdmGroupCmdOverride[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetCommandOverride('),
	(r'\bGetAdmGroupAddFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFlags('),
	(r'\bGetAdmGroupImmunity[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetGroupImmunity('),
	(r'\bGetAdmGroupAddFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.HasFlag('),
	(r'\bSetAdmGroupAddFlag[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFlag('),
	(r'\bGetAdmGroupImmuneCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.GroupImmunitiesCount'),
	(r'\bGetAdmGroupImmunityLevel[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1\.ImmunityLevel'),
	(r'\bSetAdmGroupImmunityLevel[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ImmunityLevel = \2'),

	# ArrayList
	(r'\bClearArray[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clear()'),
	(r'\bCloneArray[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clone()'),
	(r'\bCreateArray[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new ArrayList(\1)'),
	(r'\bFindStringInArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindString('),
	(r'\bFindValueInArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindValue('),
	(r'\bGetArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetArray('),
	(r'\bGetArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Get('),
	(r'\bGetArraySize[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Length'),
	(r'\bGetArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString('),
	(r'\bPushArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushArray('),
	(r'\bPushArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Push('),
	(r'\bPushArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushString('),
	(r'\bRemoveFromArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Erase('),
	(r'\bResizeArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Resize('),
	(r'\bSetArrayArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetArray('),
	(r'\bSetArrayCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Set('),
	(r'\bSetArrayString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString('),
	(r'\bShiftArrayUp[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ShiftUp('),
	(r'\bSwapArrayItems[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SwapAt('),

	# ArrayStack
	(r'\bCreateStack[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new ArrayStack(\1)'),
	(r'\bIsStackEmpty[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Empty'),
	(r'\bPopStackArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PopArray('),
	(r'\bPopStackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Pop('),
	(r'\bPopStackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PopString('),
	(r'\bPushStackArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushArray('),
	(r'\bPushStackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Push('),
	(r'\bPushStackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.PushString('),

	# StringMap
	(r'\bCreateTrie[ \t]*\([ \t]*\)', r'new StringMap()'),
	(r'\bGetTrieSize[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Size'),
	(r'\bClearTrie[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Clear()'),
	(r'\bGetTrieString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString('),
	(r'\bSetTrieString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString('),
	(r'\bGetTrieValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetValue('),
	(r'\bSetTrieValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetValue('),
	(r'\bGetTrieArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetArray('),
	(r'\bSetTrieArray[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetArray('),
	(r'\bRemoveFromTrie[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Remove('),

	# StringMapSnapshot
	(r'\bCreateTrieSnapshot[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Snapshot()'),
	(r'\bTrieSnapshotKeyBufferSize[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.KeyBufferSize('),
	(r'\bGetTrieSnapshotKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetKey('),
	(r'\bTrieSnapshotLength[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Length'),

	# BfRead/Write
	(r'\bBf((?:Read|Write)\w+)\((\w+)[, ]*', r'\2.\1('),

	# ConVar
	(r'\bGetConVarBool[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.BoolValue'),
	(r'\bGetConVarBounds[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetBounds('),
	(r'\bGetConVarDefault[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetDefault('),
	(r'\bGetConVarFlags[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Flags'),
	(r'\bGetConVarFloat[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FloatValue'),
	(r'\bGetConVarInt\((FindConVar\(.+?\)|.+?)\)', r'\1.IntValue'),
	(r'\bGetConVarName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetName('),
	(r'\bGetConVarString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString('),
	(r'\bHookConVarChange[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddChangeHook('),
	(r'\bResetConVar[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RestoreDefault('),
	(r'\bSendConVarValue[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReplicateToClient('),
	(r'\bSetConVarBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetBool(\2,'),
	(r'\bSetConVarBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.BoolValue = \2'),
	(r'\bSetConVarBounds[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetBounds('),
	(r'\bSetConVarFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Flags = \2'),
	(r'\bSetConVarFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetFloat(\2,'),
	(r'\bSetConVarFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.FloatValue = \2'),
	(r'\bSetConVarInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,', r'\1.SetInt(\2,'),
	(r'\bSetConVarInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.IntValue = \2'),
	(r'\bSetConVarString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString('),
	(r'\bUnhookConVarChange[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveChangeHook('),

	# Cookie
	(r'\bRegClientCookie[ \t]*\([ \t]*', r'new Cookie('),
	(r'\bFindClientCookie[ \t]*\(', r'Cookie.Find('),
	(r'\bSetClientCookie[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*([^\,]+)[ \t]*', r'\2.Set(\1'),
	(r'\bGetClientCookie[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*([^\,]+)[ \t]*', r'\2.Get(\1'),
	(r'\bSetAuthIdCookie[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*([^\,]+)[ \t]*', r'\2.SetByAuthId(\1'),
	(r'\bSetCookiePrefabMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetPrefabMenu('),
	(r'\bGetCookieAccess[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.AccessLevel'),

	# DataPack
	(r'\bCreateDataPack[ \t]*\([ \t]*\)', r'new DataPack()'),
	(r'\bWritePackCell[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteCell('),
	(r'\bWritePackFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteFloat('),
	(r'\bWritePackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteString('),
	(r'\bWritePackFunction[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteFunction('),
	(r'\bReadPackCell[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadCell()'),
	(r'\bReadPackFloat[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadFloat()'),
	(r'\bReadPackString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadString('),
	(r'\bReadPackFunction[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ReadFunction()'),
	(r'\bResetPack[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.Reset(\2)'),
	(r'\bGetPackPosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Position'),
	(r'\bSetPackPosition[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Position = \2'),
	(r'\bIsStackEmptyckReadable[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsReadable('),

	# DBDriver
	(r'\bSQL_GetDriver[ \t]*\(', r'DBDriver.Find('),
	(r'\bSQL_GetDriverProduct[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetProduct('),
	(r'\bSQL_GetDriverIdent[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetIdentifier('),

	# DBResultSet
	(r'\bSQL_FetchMoreResults[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FetchMoreResults()'),
	(r'\bSQL_HasResultSet[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.HasResults'),
	(r'\bSQL_GetRowCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.RowCount'),
	(r'\bSQL_GetFieldCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FieldCount'),
	(r'\bSQL_GetAffectedRows[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.AffectedRows'),
	(r'\bSQL_GetInsertId[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.InsertId'),
	(r'\bSQL_FieldNumToName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FieldNumToName('),
	(r'\bSQL_FieldNameToNum[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FieldNameToNum('),
	(r'\bSQL_FetchRow[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.FetchRow()'),
	(r'\bSQL_MoreRows[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.MoreRows'),
	(r'\bSQL_Rewind[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Rewind()'),
	(r'\bSQL_FetchString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchString('),
	(r'\bSQL_FetchFloats*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchFloat('),
	(r'\bSQL_FetchInt*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchInt('),
	(r'\bSQL_IsFieldNull*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsFieldNull('),
	(r'\bSQL_FetchSize*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FetchSize('),

	# Transaction
	(r'\bSQL_CreateTransaction[ \t]*\([ \t]*\)', r'new Transaction()'),
	(r'\bSQL_AddQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddQuery('),

	# Database
	(r'\bSQL_TConnect[ \t]*\(', r'Database.Connect('),
	(r'\bSQL_ReadDriver[ \t]*\([ \t]*([^\)\,]+)[ \t]*\)', r'\1.Driver'),
	(r'\bSQL_SetCharset[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetCharset('),
	(r'\bSQL_EscapeString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Escape('),
	(r'\bSQL_FormatQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Format('),
	(r'\bSQL_IsSameConnection[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.IsSameConnection('),
	(r'\bSQL_TQuery[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Query('),
	(r'\bSQL_ExecuteTransaction[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Execute('),

	# DBStatement
	(r'\bSQL_BindParamInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindInt('),
	(r'\bSQL_BindParamFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindFloat('),
	(r'\bSQL_BindParamString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.BindString('),

	# DirectoryListing
	(r'\b\w+[ \t]+(.*?)[ \t]*=[ \t]*(OpenDirectory)', r'DirectoryListing \1 = \2'),
	(r'\bReadDirEntry[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetNext('),

	# Event
	(r'\bFireEvent[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.Fire(\2)'),
	(r'\bCancelCreatedEvent[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Cancel()'),
	(r'\bGetEventBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetBool('),
	(r'\bSetEventBool[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetBool('),
	(r'\bGetEventInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetInt('),
	(r'\bSetEventInt[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetInt('),
	(r'\bGetEventFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFloat('),
	(r'\bSetEventFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFloat('),
	(r'\bGetEventString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString('),
	(r'\bSetEventString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString('),
	(r'\bGetEventName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetName('),
	(r'\bSetEventBroadcast[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.BroadcastDisabled = \2'),

	# File
	(r'\bIsEndOfFile[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.EndOfFile()'),
	(r'\bReadFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Read('),
	(r'\bReadFileLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadLine('),
	(r'\bReadFileString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ReadString('),
	(r'\bFileSeek[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Seek('),
	(r'\bWriteFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Write('),
	(r'\bWriteFileLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteLine('),
	(r'\bWriteStringLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.WriteString('),
	(r'\bFilePosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Position'),
	# TODO: ReadFileCell, ReadIntX

	# Forward
	(r'\bCreateGlobalForward[ \t]*\(', r'new GlobalForward('),
	(r'\bGetForwardFunctionCount[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.FunctionCount'),

	(r'\bCreateForward[ \t]*\(', r'new PrivateForward('),
	(r'\bAddToForward[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddFunction('),
	(r'\bRemoveFromForward[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveFunction('),
	(r'\bRemoveAllFromForward[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveAllFunctions('),

	# GameData
	(r'\bLoadGameConfigFile[ \t]*\(', r'new GameData'),
	(r'\bGameConfGetOffset[ \t]*\([ \t]*([^\,]+),[ \t]*', r'\1.GetOffset('),
	(r'\bGameConfGetKeyValue[ \t]*\([ \t]*([^\,]+),[ \t]*', r'\1.GetKeyValue('),
	(r'\bGameConfGetAddress[ \t]*\([ \t]*([^\,]+),[ \t]*', r'\1.GetAddress('),

	# Handle
	(r'\bCloseHandle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'delete \1'),

	# KeyValue
	(r'\bCreateKeyValues[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'new KeyValues(\1)'),
	(r'\bKvSetString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetString('),
	(r'\bKvSetNum[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetNum('),
	(r'\bKvSetUInt64[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetUInt64('),
	(r'\bKvSetFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetFloat('),
	(r'\bKvSetColor[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetColor('),
	(r'\bKvSetVector[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetVector('),
	(r'\bKvGetString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetString('),
	(r'\bKvGetNum[ \t]*\([ \t]*(.*?)[ \t]*,[ \t]*', r'\1.GetNum('),
	(r'\bKvGetFloat[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetFloat('),
	(r'\bKvGetColor[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetColor('),
	(r'\bKvGetUInt64[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetUInt64('),
	(r'\bKvGetVector[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetVector('),
	(r'\bKvJumpToKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.JumpToKey('),
	(r'\bKvJumpToKeySymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.JumpToKeySymbol('),
	(r'\bKvGotoFirstSubKey[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.GotoFirstSubKey(\2)'),
	(r'\bKvGotoNextKey[ \t]*\([ \t]*([^\,\)]+)[ \t]*,?[ \t]*([^\)]*)[ \t]*\)', r'\1.GotoNextKey(\2)'),
	(r'\bKvSavePosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.SavePosition()'),
	(r'\bKvDeleteKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DeleteKey('),
	(r'\bKvDeleteThis[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.DeleteThis()'),
	(r'\bKvGoBack[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.GoBack()'),
	(r'\bKvRewind[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Rewind()'),
	(r'\bKvGetSectionName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSectionName('),
	(r'\bKvSetSectionName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetSectionName('),
	(r'\bKvGetDataType[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetDataType('),
	(r'\bKeyValuesToFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ExportToFile('),
	(r'\bFileToKeyValues[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ImportFromFile('),
	(r'\bStringToKeyValues[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ImportFromString('),
	(r'\bKvSetEscapeSequences[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetEscapeSequences('),
	(r'\bKvNodesInStack[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.NodesInStack()'),
	(r'\bKvCopySubkeys[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Import('),
	(r'\bKvFindKeyById[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindKeyById('),
	(r'\bKvGetNameSymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetNameSymbol('),
	(r'\bKvGetSectionSymbol[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSectionSymbol('),

	# Menu
	(r'\bCreateMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'new Menu(\1)'),
	(r'\bDisplayMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Display('),
	(r'\bDisplayMenuAtItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayAt('),
	(r'\bAddMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.AddItem('),
	(r'\bInsertMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.InsertItem('),
	(r'\bRemoveMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.RemoveItem('),
	(r'\bRemoveAllMenuItems[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.RemoveAllItems()'),
	(r'\bGetMenuItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetItem('),
	(r'\bGetMenuSelectionPosition[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Selection'),
	(r'\bGetMenuItemCount[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ItemCount'),
	(r'\bSetMenuPagination[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.Pagination = \2'),
	(r'\bGetMenuPagination[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Pagination'),
	(r'\bGetMenuStyle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Style'),
	(r'\bSetMenuTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetTitle('),
	(r'\bGetMenuTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetTitle('),
	(r'\bCreatePanelFromMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ToPanel()'),
	(r'\bGetMenuExitButton[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ExitButton'),
	(r'\bSetMenuExitButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ExitButton = \2'),
	(r'\bGetMenuExitBackButton[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.ExitBackButton'),
	(r'\bSetMenuExitBackButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.ExitBackButton = \2'),
	(r'\bSetMenuNoVoteButton[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.NoVoteButton = \2'),
	(r'\bCancelMenu[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Cancel()'),
	(r'\bGetMenuOptionFlags[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.OptionFlags'),
	(r'\bSetMenuOptionFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OptionFlags = \2'),
	(r'\bVoteMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayVote('),
	(r'\bVoteMenuToAll[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayVoteToAll('),
	(r'\bSetVoteResultCallback[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.VoteResultCallback = \2'),

	# Panel
	(r'\bCreatePanel[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new Panel(\1)'),
	(r'\bGetPanelStyle[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.Style'),
	(r'\bSetPanelTitle[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetTitle('),
	(r'\bDrawPanelItem[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DrawItem('),
	(r'\bDrawPanelText[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DrawText('),
	(r'\bCanPanelDrawFlags[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.CanDrawFlags('),
	(r'\bSetPanelKeys[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.SetKeys('),
	(r'\bSendPanelToClient[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Send('),
	(r'\bGetPanelTextRemaining[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.TextRemaining'),
	(r'\bGetPanelCurrentKey[ \t]*\([ \t]*([^\)]+)[ \t]*\)', r'\1.CurrentKey'),
	(r'\bSetPanelCurrentKey[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.CurrentKey = \2'),

	# Profiler
	(r'\bCreateProfiler[ \t]*\([ \t]*\)', r'new Profiler()'),
	(r'\bStartProfiling[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.Start()'),
	(r'\bStopProfiling[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.Stop()'),
	(r'\bGetProfilerTime[ \t]*\([ \t]*(.*?)[ \t]*\)', r'\1.Time'),

	# Protobuf
	(r'\bPb((?:Add|Read|Set|Get|Remove)\w+)\((\w+)[, ]*', r'\2.\1('),

	# Regex
	(r'\bCompileRegex[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new Regex(\1)'),
	(r'\bMatchRegex[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Match('),
	(r'\bGetRegexSubString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetSubString('),

	# SMCParser
	(r'\bSMC_CreateParser[ \t]*\([ \t]*\)', r'new SMCParser()'),
	(r'\bSMC_ParseFile[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.ParseFile('),
	(r'\bSMC_SetParseStart[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnStart = \2'),
	(r'\bSMC_SetParseEnd[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnEnd = \2'),
	(r'([ \t]+)SMC_SetReaders\((\w+),[ \t]*(\w+),[ \t]*(\w+),[ \t]*(\w+).*', r'\1\2.OnEnterSection = \3;\n\1\2.OnKeyValue = \4;\n\1\2.OnLeaveSection = \5;'),
	(r'\bSMC_SetRawLine[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.OnRawLine = \2'),
	# Can't update SMC_GetErrorString with regex

	# TopMenu
	(r'\bCreateTopMenu[ \t]*\([ \t]*([^\)]*)[ \t]*\)', r'new TopMenu(\1)'),
	(r'\bLoadTopMenuConfig[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.LoadConfig('),
	(r'\bAddToTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,[ \t]*TopMenuObject_Category', r'\1.AddCategory(\2, '),
	(r'\bAddToTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\,]+)[ \t]*,[ \t]*TopMenuObject_Item', r'\1.AddItem(\2, '),
	(r'\bGetTopMenuInfoString[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetInfoString('),
	(r'\bGetTopMenuObjName[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.GetObjName('),
	(r'\bRemoveFromTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Remove('),
	(r'\bDisplayTopMenu[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.Display('),
	(r'\bDisplayTopMenuCategory[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.DisplayCategory('),
	(r'\bFindTopMenuCategory[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*', r'\1.FindCategory('),
	(r'\bSetTopMenuTitleCaching[ \t]*\([ \t]*([^\,]+)[ \t]*,[ \t]*([^\)]+)[ \t]*\)', r'\1.CacheTitles = \2'),
]


METHODMAPS_NO_NEW = lambda : [
	('ArrayList',        'CloneArray'),
	('ConVar',           'CreateConVar'),
	('ConVar',           'FindConVar'),
	('Cookie',           'FindClientCookie'),
	('DirectoryListing', 'OpenDirectory'),
	('Event',            'CreateEvent'),
	('File',             'OpenFile'),
	('Protobuf',         'PbAddMessage'),
]


METHODMAPS = lambda : [
	'ArrayList',
	'ArrayStack',
	'Cookie',
	'DataPack',
	'GameData',
	'GlobalForward',
	'KeyValues',
	'Menu',
	'Panel',
	'PrivateForward',
	'Profiler',
	'Regex',
	'SMCParser',
	'StringMap',
	'TopMenu',
	'Transaction'
]


# Updates Handles to their methodmap
def updateHandle(dataType, func, code):
	for m in re.finditer(r'(\w+)[ \t]*=[ \t]*' + func, code):
		var = m.group(1)
		pattern = r'Handle[ \t]+' + var + r'\b'
		replace = dataType + ' ' + var
		code = re.sub(pattern, replace, code)

	return code


# Updates Handles to their methodmap (searches for `= new`)
def updateMethodmap(dataType, code):
	for m in re.finditer(r'(\w+)[ \t]*=[ \t]*new[ \t]+(' + dataType + ')', code):
		var1 = m.group(1)
		var2 = m.group(2)

		pattern = r'(static[ \t]+)?Handle[ \t]+' + var1 + r'\b'
		replacement = r'\1' + var2 + ' ' + var1

		code = re.sub(pattern, replacement, code)
		
	return code


for i in range(1, len(sys.argv)):
	if not os.path.isfile(sys.argv[i]):
		print('File not found: {}'.format(sys.argv[i]))
		continue

	code = ''

	with open(sys.argv[i], 'r', encoding = 'utf-8') as f:
		print('Methodmapizing {}'.format(sys.argv[i]))

		code = f.read()

		# -- Handle: -> Handle 
		code = re.sub(r'(\bnew[ \t]+)?Handle:', 'Handle ', code)


		# -- Update handles from non 'new' functions
		for methodmap, func in METHODMAPS_NO_NEW():
			code = updateHandle(methodmap, func, code)


		# -- Main Replacements
		for search, replace in REPLACEMEMTS():
			code = re.sub(search, replace, code)


		# -- Socket
		m = re.search(r'\bSocketCreate\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*\)', code)
		if m: # SocketErrorCB
			code = re.sub(r'(\npublic )([ \t]*\b' + m.group(1) + r'\b[ \t]*)', r'\1void \2', code)

		m = re.search(r'\bSocketListen\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*\)', code)
		if m: # SocketIncomingCB
			code = re.sub(r'(\npublic )([ \t]*\b' + m.group(1) + r'\b[ \t]*)', r'\1void \2', code)

		m = re.search(r'\bSocketSetSendqueueEmptyCallback\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*\)', code)
		if m: # SocketSendqueueEmptyCB
			code = re.sub(r'(\npublic )([ \t]*\b' + m.group(1) + r'\b[ \t]*)', r'\1void \2', code)

		m = re.search(r'\bSocketConnect\([ \t]*.*?[ \t]*,[ \t]*(.*?)[ \t]*,[ \t]*(.*?)[ \t]*,[ \t]*(.*?)[ \t]*,', code)
		if m: # Connect, Receive, Disconnect
			for i in range(1, 3):
				code = re.sub(r'(^public[ \t])' + r'([ \t]*\b' + m.group(i) + r'\b[ \t]*)', r'\1void \2', code, 0, re.M)	


		# -- Remove deprecated FCVAR_PLUGIN
		code = re.sub(r'(?:\|FCVAR_PLUGIN|FCVAR_PLUGIN\|)', r'', code)
		code = re.sub('FCVAR_PLUGIN', '0', code)


		# -- Update invalid_handle to null
		code = re.sub('INVALID_HANDLE', 'null', code)


		# -- Updates Handle to datatypes generated by `= new` functions
		for methodmap in METHODMAPS():
			code = updateMethodmap(methodmap, code)



		# -- ConVar change callback
		for m in re.finditer(r'\.AddChangeHook\([ \t]*(.*?)[ \t]*\)', code):
			cvar = m.group(1)
			pattern = r'(\n[ \t]*public .*?' + cvar + r')\([ \t]*Handle'
			replace = r'\1' + r'(ConVar'
			code = re.sub(pattern, replace, code)

		# -- Event callback
		for m in re.finditer(r'\bHookEvent(?:Ex)*\(.*?,[ \t]*(.*?)[ \t]*(,|\))', code):
			event = m.group(1)
			pattern = r'(\n[ \t]*public .*?' + event + r')\([ \t]*Handle'
			replace = r'\1' + r'(Event'
			code = re.sub(pattern, replace, code)


	index = sys.argv[i].rfind('.')
	file = sys.argv[i][:index] + '.m' + sys.argv[i][index:]

	with open(file, 'w', encoding = 'utf-8') as f:
		f.write(code)
