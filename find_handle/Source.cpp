#include <stdio.h>
#include <windows.h>
#include "Source.h"
#include <locale.h>
#include <tchar.h>
#include <string.h>
#include <psapi.h>
#include <strsafe.h>

#define VERBOSE 1

_NtQuerySystemInformation get_NtQuerySystemInformation_handle(void);
_NtQueryObject get_NtQueryObject_handle(void);
PSYSTEM_HANDLE_INFORMATION get_system_handle_info(_NtQuerySystemInformation NtQuerySystemInformation);
HANDLE DuplicateFileHandle(SYSTEM_HANDLE handle);
PWSTR GetFileNameFromHandle(HANDLE handle, _NtQueryObject NtQueryObject);
BOOL ConvertFileName(PWSTR pszFilename);

int wmain()
{
	setlocale(LC_CTYPE, "");
	// get NtQuerySystemInformation function from ntdll
	_NtQuerySystemInformation NtQuerySystemInformation = get_NtQuerySystemInformation_handle();
	if (NtQuerySystemInformation == NULL)
	{
		return(-1);
	}
	// get NtQueryObject function from ntdll
	_NtQueryObject NtQueryObject = get_NtQueryObject_handle();
	if (NtQueryObject == NULL)
	{
		return(-1);
	}

	// get system hadle information
	PSYSTEM_HANDLE_INFORMATION handleInfo = get_system_handle_info(NtQuerySystemInformation);
	if (handleInfo == NULL)
	{
		printf("error: get system handle info failed.\n");
		return(-1);
	}
	else {
		if (VERBOSE)
		{
			printf("Success: get system handle info.\n");
		}
	}

	// enumerate all handles
	for (ULONG i = 0; i < handleInfo->HandleCount; i++)
	{
		SYSTEM_HANDLE handle = handleInfo->Handles[i];
		

		if (handle.ProcessId == 21924) {
			HANDLE dupHandle = DuplicateFileHandle(handle);
			PWSTR filename = NULL;
			BOOL status = FALSE;
			if (dupHandle) {
				filename = GetFileNameFromHandle(dupHandle, NtQueryObject);
			}
			else {
				continue;
			}
			if (filename) {
				status = ConvertFileName(filename);
			}
			else {
				continue;
			}
			if (filename) {
				continue;
			}
		}
	}

	return(0);
}

_NtQuerySystemInformation get_NtQuerySystemInformation_handle(void)
{
	/* Import functions manually from NTDLL */
	HMODULE dll_file = GetModuleHandleA("ntdll.dll");  // try to load ntdll, if return null exit
	if (dll_file)
	{
		// get NtQuerySystemInformation handle
		_NtQuerySystemInformation NtQuerySystemInformation =
			(_NtQuerySystemInformation)GetProcAddress(dll_file, "NtQuerySystemInformation");

		if (NtQuerySystemInformation == NULL)
		{
			printf("error: get NtQuerySystemInformation function handle failed.\n");
			return(NULL);
		}
		else {
			if (VERBOSE)
			{
				printf("Success: get NtQuerySystemInformation function handle.\n");
				return NtQuerySystemInformation;
			}
		}
	}
	else {
		// load ntdll failed, exit program.
		printf("error: ntdll.dll load failed!\n");
		return(NULL);
	}
}

_NtQueryObject get_NtQueryObject_handle(void)
{
	/* Import functions manually from NTDLL */
	HMODULE dll_file = GetModuleHandleA("ntdll.dll");  // try to load ntdll, if return null exit
	if (dll_file)
	{
		// get NtQuerySystemInformation handle
		_NtQueryObject NtQueryObject =
			(_NtQueryObject)GetProcAddress(dll_file, "NtQueryObject");

		if (NtQueryObject == NULL)
		{
			printf("error: get NtQueryObject function handle failed.\n");
			return(NULL);
		}
		else {
			if (VERBOSE)
			{
				printf("Success: get NtQueryObject function handle.\n");
				return NtQueryObject;
			}
		}
		return NtQueryObject;
	}
	else {
		// load ntdll failed, exit program.
		printf("error: ntdll.dll load failed!\n");
		return(NULL);
	}
}

PSYSTEM_HANDLE_INFORMATION get_system_handle_info(_NtQuerySystemInformation NtQuerySystemInformation)
{
	// storage system handle info to handleInfo by using NtQuerySystemInformation

	// init status to mismatch length
	NTSTATUS status = STATUS_INFO_LENGTH_MISMATCH;

	// initialize handleInfo mem
	DWORD handleInfoSize = 0x10000;
	PSYSTEM_HANDLE_INFORMATION handleInfo = (PSYSTEM_HANDLE_INFORMATION)malloc(handleInfoSize);
	// try to get system handles
	if (handleInfo == NULL)
		return(NULL);  // system mem is insufficient

	// if mem length setting is insufficient, double the mem length and realloc, try again
	while ((status = NtQuerySystemInformation(
		SystemHandleInformation,
		handleInfo,
		handleInfoSize,
		NULL
		)) == STATUS_INFO_LENGTH_MISMATCH)
	{
		handleInfoSize *= 2;
		if (handleInfoSize > 0x10000000)
		{
			// handleInfoSize is too large
			printf("error: handleInfoSize is too large\n");
			return(NULL);
		}
		PSYSTEM_HANDLE_INFORMATION temp_p = (PSYSTEM_HANDLE_INFORMATION)realloc(handleInfo, handleInfoSize);
		if (temp_p)
			handleInfo = temp_p;
		else
			return(NULL);  // system mem is insufficient
	}

	// if NtQuerySystemInformation stopped return STATUS_INFO_LENGTH_MISMATCH
	if (!NT_SUCCESS(status))
	{
		free(handleInfo);
		printf("error: NtQuerySystemInformation function failed!\n");
		return(NULL);
	}

	return(handleInfo);
}

HANDLE DuplicateFileHandle(SYSTEM_HANDLE handle)
{
	HANDLE dupHandle = NULL;
	HANDLE processHandle = NULL;
	

	/* Open a handle to the process associated with the handle */
	if (!(processHandle = OpenProcess(
		PROCESS_DUP_HANDLE,
		FALSE,
		handle.ProcessId)))
	{
		//  open a handle to the process failed
		// printf("error: can't open a handle the process: %d\n", handle.ProcessId);
		return(NULL);
	}

	// duplicate the system handle for further get file name, etc.
	if (!DuplicateHandle(
		processHandle,
		(HANDLE)handle.Handle,
		GetCurrentProcess(),
		&dupHandle,
		0,
		TRUE,
		DUPLICATE_SAME_ACCESS))
	{
		// Will fail if not a regular file; just skip it. maybe a mutex lock
		CloseHandle(processHandle);
		CloseHandle(dupHandle);
		return(NULL);
	}

	// Note: also this is supposed to hang, hence why we do it in here.
	if (GetFileType(dupHandle) != FILE_TYPE_DISK) {
		SetLastError(0);
		// printf("error: it's not a regular file.\n");
		return(NULL);
	}
	return(dupHandle);
}


PWSTR GetFileNameFromHandle(HANDLE handle, _NtQueryObject NtQueryObject)
{
	DWORD fileName_bufferSize = MAX_PATH; // buffer for file name info
	POBJECT_NAME_INFORMATION fileNameInfo = (POBJECT_NAME_INFORMATION)malloc(fileName_bufferSize);
	NTSTATUS status;
	ULONG attempts = 8;
	// A loop is needed because the I/O subsystem likes to give us the
	// wrong return lengths...
	do {
		status = NtQueryObject(
			handle,
			ObjectNameInformation,
			fileNameInfo,
			fileName_bufferSize,
			&fileName_bufferSize
		);
		if (status == STATUS_BUFFER_OVERFLOW ||
			status == STATUS_INFO_LENGTH_MISMATCH ||
			status == STATUS_BUFFER_TOO_SMALL)
		{
			free(fileNameInfo);
			fileNameInfo = (POBJECT_NAME_INFORMATION)malloc(fileName_bufferSize);
			if (fileNameInfo == NULL) {
				printf("error: filename buffer alloc error.\n");
				break;
			}
		}
		else {
			break;
		}
	} while (--attempts);

	if (!NT_SUCCESS(status)) {
		free(fileNameInfo);
		fileNameInfo = NULL;
		return(NULL);
	}
	else {
		if (fileNameInfo) {
			return(fileNameInfo->Name.Buffer);
		}
		else
		{
			return(NULL);
		}
	}
}

BOOL ConvertFileName(PWSTR pszFilename)
{
	BOOL bSuccess = FALSE;
	ULONG BUFSIZE = 512;
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
	bSuccess = TRUE;

	_tprintf(TEXT("File name is %s\n"), pszFilename);
	return(bSuccess);
}
