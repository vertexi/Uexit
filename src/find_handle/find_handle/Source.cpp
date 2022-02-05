#include <stdio.h>
#include <windows.h>
#include "Source.h"
#include <locale.h>
#include <tchar.h>
#include <string.h>
#include <psapi.h>
#include <strsafe.h>

// #define DEBUG

#ifdef DEBUG
#define DEBUG_PRINT(...) do{ fprintf( stdout, __VA_ARGS__ ); } while( false )
#else
#define DEBUG_PRINT(...) do{ } while ( false )
#endif

_NtQuerySystemInformation GetNtQuerySystemInformationHandle(void);
_NtQueryObject GetNtQueryObjectHandle(void);
PSYSTEM_HANDLE_INFORMATION GetSystemHandleInfo(_NtQuerySystemInformation NtQuerySystemInformation);
HANDLE DuplicateFileHandle(SYSTEM_HANDLE handle);
POBJECT_NAME_INFORMATION GetFileNameFromHandle(HANDLE handle, _NtQueryObject NtQueryObject);
BOOL ConvertFileName(PWSTR pszFilename);
BOOL StartsWith(wchar_t* pre, wchar_t* str);

int wmain(int argc, wchar_t* argv[])
{
	setlocale(LC_ALL, ".UTF8");
	SEARCH_STATUS SearchStatus = NoSearch;
	wchar_t* SearchString = NULL;

	if (argc == 1) {
		SearchStatus = NoSearch;
	}
	else if (!wcscmp(argv[1], L"-contain")) {
		SearchStatus = SearchContain;
		SearchString = argv[2];
	}
	else if (!wcscmp(argv[1], L"-startswith")) {
		SearchStatus = SearchStarstWith;
		SearchString = argv[2];
	}
	else {
		return(0);
	}
	
	// get NtQuerySystemInformation function from ntdll
	_NtQuerySystemInformation NtQuerySystemInformation = GetNtQuerySystemInformationHandle();
	if (NtQuerySystemInformation == NULL)
	{
		return(-1);
	}
	// get NtQueryObject function from ntdll
	_NtQueryObject NtQueryObject = GetNtQueryObjectHandle();
	if (NtQueryObject == NULL)
	{
		return(-1);
	}

	// get system hadle information
	PSYSTEM_HANDLE_INFORMATION HandleInfo = GetSystemHandleInfo(NtQuerySystemInformation);
	if (HandleInfo == NULL)
	{
		DEBUG_PRINT("error: get system handle info failed.\n");
		return(-1);
	}
	else {
		DEBUG_PRINT("Success: get system handle info.\n");
	}

	// enumerate all handles
	for (ULONG i = 0; i < HandleInfo->HandleCount; i++)
	{
		SYSTEM_HANDLE handle = HandleInfo->Handles[i];
		
		if (handle.ProcessId) {
			HANDLE DupHandle = DuplicateFileHandle(handle);
			POBJECT_NAME_INFORMATION FileNameInfo = NULL;
			PWSTR filename = NULL;
			BOOL ConvertStatus = FALSE;
			if (DupHandle) {
				FileNameInfo = GetFileNameFromHandle(DupHandle, NtQueryObject);
				filename = FileNameInfo->Name.Buffer;
				CloseHandle(DupHandle);
			}
			else {
				continue;
			}
			if (FileNameInfo) {
				ConvertStatus = ConvertFileName(filename);
			}
			else {
				continue;
			}
			if (ConvertStatus) {
				if (SearchStatus == NoSearch) {
					_tprintf(TEXT("File:%s\tPID:%d\n"), filename, handle.ProcessId);
				}
				else if (SearchStatus == SearchContain) {
					if (wcsstr(filename, SearchString)) {
						_tprintf(TEXT("File:%s\tPID:%d\n"), filename, handle.ProcessId);
					}
				}
				else if (SearchStatus == SearchStarstWith) {
					if (StartsWith(SearchString, filename)) {
						_tprintf(TEXT("File:%s\tPID:%d\n"), filename, handle.ProcessId);
					}
				}
			}
			free(FileNameInfo);
		}
	}

	free(HandleInfo);
	return(0);
}

_NtQuerySystemInformation GetNtQuerySystemInformationHandle(void)
{
	/* Import functions manually from NTDLL */
	HMODULE Dllfile = GetModuleHandleA("ntdll.dll");  // try to load ntdll, if return null exit
	if (Dllfile)
	{
		// get NtQuerySystemInformation handle
		_NtQuerySystemInformation NtQuerySystemInformation =
			(_NtQuerySystemInformation)GetProcAddress(Dllfile, "NtQuerySystemInformation");

		if (NtQuerySystemInformation == NULL)
		{
			DEBUG_PRINT("error: get NtQuerySystemInformation function handle failed.\n");
			return(NULL);
		}
		else {
			DEBUG_PRINT("Success: get NtQuerySystemInformation function handle.\n");
			return NtQuerySystemInformation;
		}
	}
	else {
		// load ntdll failed, exit program.
		DEBUG_PRINT("error: ntdll.dll load failed!\n");
		return(NULL);
	}
}

_NtQueryObject GetNtQueryObjectHandle(void)
{
	/* Import functions manually from NTDLL */
	HMODULE Dllfile = GetModuleHandleA("ntdll.dll");  // try to load ntdll, if return null exit
	if (Dllfile)
	{
		// get NtQuerySystemInformation handle
		_NtQueryObject NtQueryObject =
			(_NtQueryObject)GetProcAddress(Dllfile, "NtQueryObject");

		if (NtQueryObject == NULL)
		{
			DEBUG_PRINT("error: get NtQueryObject function handle failed.\n");
			return(NULL);
		}
		else {
			DEBUG_PRINT("Success: get NtQueryObject function handle.\n");
			return NtQueryObject;
		}
		return NtQueryObject;
	}
	else {
		// load ntdll failed, exit program.
		DEBUG_PRINT("error: ntdll.dll load failed!\n");
		return(NULL);
	}
}

PSYSTEM_HANDLE_INFORMATION GetSystemHandleInfo(_NtQuerySystemInformation NtQuerySystemInformation)
{
	// storage system handle info to handleInfo by using NtQuerySystemInformation

	// init status to mismatch length
	NTSTATUS status = STATUS_INFO_LENGTH_MISMATCH;

	// initialize handleInfo mem
	DWORD HandleInfoSize = 0x10000;
	PSYSTEM_HANDLE_INFORMATION HandleInfo = (PSYSTEM_HANDLE_INFORMATION)malloc(HandleInfoSize);
	// try to get system handles
	if (HandleInfo == NULL)
		return(NULL);  // system mem is insufficient

	// if mem length setting is insufficient, double the mem length and realloc, try again
	while ((status = NtQuerySystemInformation(
		SystemHandleInformation,
		HandleInfo,
		HandleInfoSize,
		NULL
		)) == STATUS_INFO_LENGTH_MISMATCH)
	{
		HandleInfoSize *= 2;
		if (HandleInfoSize > 0x10000000)
		{
			// handleInfoSize is too large
			DEBUG_PRINT("error: handleInfoSize is too large\n");
			return(NULL);
		}
		PSYSTEM_HANDLE_INFORMATION temp_p = (PSYSTEM_HANDLE_INFORMATION)realloc(HandleInfo, HandleInfoSize);
		if (temp_p)
			HandleInfo = temp_p;
		else
			return(NULL);  // system mem is insufficient
	}

	// if NtQuerySystemInformation stopped return STATUS_INFO_LENGTH_MISMATCH
	if (!NT_SUCCESS(status))
	{
		free(HandleInfo);
		DEBUG_PRINT("error: NtQuerySystemInformation function failed!\n");
		return(NULL);
	}

	return(HandleInfo);
}

HANDLE DuplicateFileHandle(SYSTEM_HANDLE handle)
{
	HANDLE DupHandle = NULL;
	HANDLE ProcessHandle = NULL;

	/* Open a handle to the process associated with the handle */
	if (!(ProcessHandle = OpenProcess(
		PROCESS_DUP_HANDLE,
		FALSE,
		handle.ProcessId)))
	{
		//  open a handle to the process failed
		DEBUG_PRINT("error: can't open a handle the process: %d\n", handle.ProcessId);
		return(NULL);
	}

	// duplicate the system handle for further get file name, etc.
	if (!DuplicateHandle(
		ProcessHandle,
		(HANDLE)handle.Handle,
		GetCurrentProcess(),
		&DupHandle,
		0,
		TRUE,
		DUPLICATE_SAME_ACCESS))
	{
		// Will fail if not a regular file; just skip it. maybe a mutex lock
		DEBUG_PRINT("error: it's not a regular file.\n");
		CloseHandle(ProcessHandle);
		CloseHandle(DupHandle);
		return(NULL);
	}

	// Note: also this is supposed to hang, hence why we do it in here.
	if (GetFileType(DupHandle) != FILE_TYPE_DISK) {
		SetLastError(0);
		DEBUG_PRINT("error: it's not a FILE_TYPE_DISK handle.\n");
		CloseHandle(ProcessHandle);
		CloseHandle(DupHandle);
		return(NULL);
	}

	CloseHandle(ProcessHandle);
	return(DupHandle);
}


POBJECT_NAME_INFORMATION GetFileNameFromHandle(HANDLE handle, _NtQueryObject NtQueryObject)
{
	DWORD FileNameBufferSize = MAX_PATH; // buffer for file name info
	POBJECT_NAME_INFORMATION FileNameInfo = (POBJECT_NAME_INFORMATION)malloc(FileNameBufferSize);
	NTSTATUS status;
	ULONG attempts = 8;
	// A loop is needed because the I/O subsystem likes to give us the
	// wrong return lengths...
	do {
		status = NtQueryObject(
			handle,
			ObjectNameInformation,
			FileNameInfo,
			FileNameBufferSize,
			&FileNameBufferSize
		);
		if (status == STATUS_BUFFER_OVERFLOW ||
			status == STATUS_INFO_LENGTH_MISMATCH ||
			status == STATUS_BUFFER_TOO_SMALL)
		{
			free(FileNameInfo);
			FileNameInfo = (POBJECT_NAME_INFORMATION)malloc(FileNameBufferSize);
			if (FileNameInfo == NULL) {
				DEBUG_PRINT("error: filename buffer alloc error.\n");
				break;
			}
		}
		else {
			break;
		}
	} while (--attempts);

	if (!NT_SUCCESS(status)) {
		free(FileNameInfo);
		return(NULL);
	}
	else {
		if (FileNameInfo)
			return(FileNameInfo);
		else
			return(NULL);
	}
}

BOOL ConvertFileName(PWSTR pszFilename)
{
	const ULONG BUFSIZE = 512;
	// Translate path with device name to drive letters.
	TCHAR *szTemp = (TCHAR*)malloc(BUFSIZE*sizeof(*szTemp));
	if (szTemp) {
		szTemp[0] = '\0';
	}
	else {
		return(FALSE);
	}
	
	if (GetLogicalDriveStrings(BUFSIZE - 1, szTemp))
	{
		TCHAR szName[MAX_PATH];
		TCHAR szDrive[3] = TEXT(" :");
		BOOL bFound = FALSE;
		TCHAR* p = szTemp;

		do
		{
			// Copy the drive letter to the template string
			*szDrive = *p;

			// Look up each device name
			if (QueryDosDevice(szDrive, szName, MAX_PATH))
			{
				size_t uNameLen = _tcslen(szName);

				if (uNameLen < MAX_PATH)
				{
					bFound = _tcsnicmp(pszFilename, szName, uNameLen) == 0
						&& *(pszFilename + uNameLen) == _T('\\');

					if (bFound)
					{
						// Reconstruct pszFilename using szTempFile
						// Replace device path with DOS path
						TCHAR szTempFile[MAX_PATH];
						StringCchPrintf(szTempFile,
							MAX_PATH,
							TEXT("%s%s"),
							szDrive,
							pszFilename + uNameLen);
						StringCchCopyN(pszFilename, MAX_PATH + 1, szTempFile, _tcslen(szTempFile));
					}
				}
			}

			// Go to the next NULL character.
			while (*p++);
		} while (!bFound && *p); // end of string
	}
	return(TRUE);
}

BOOL StartsWith(wchar_t *pre, wchar_t *str)
{
	return _tcsnicmp(pre, str, _tcslen(pre)) == 0;
}
