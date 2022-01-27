#include <stdio.h>
#include <windows.h>
#include "Source.h"

#define VERBOSE 1

_NtQuerySystemInformation get_NtQuerySystemInformation_handle(void);
PSYSTEM_HANDLE_INFORMATION get_system_handle_info(_NtQuerySystemInformation NtQuerySystemInformation);

int wmain()
{
	// get NtQuerySystemInformation function from ntdll
	_NtQuerySystemInformation NtQuerySystemInformation = get_NtQuerySystemInformation_handle();
	if (NtQuerySystemInformation == NULL)
	{
		printf("get NtQuerySystemInformation function handle failed.\n");
		return(-1);
	}
	else {
		if (VERBOSE)
		{
			printf("Success get NtQuerySystemInformation function handle.\n");
		}
	}

	// get system hadle information
	PSYSTEM_HANDLE_INFORMATION handleInfo = get_system_handle_info(NtQuerySystemInformation);
	if (handleInfo == NULL)
	{
		printf("get system handle info failed.\n");
		return(-1);
	}
	else {
		if (VERBOSE)
		{
			printf("Success get system handle info.\n");
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
		return NtQuerySystemInformation;
	}
	else {
		// load ntdll failed, exit program.
		printf("ntdll.dll load failed!\n");
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
	if (handleInfo)
		NTSTATUS status = NtQuerySystemInformation(SystemHandleInformation, handleInfo, handleInfoSize, &handleInfoSize);
	else
		return(NULL);  // system mem is insufficient

	// if mem length setting is insufficient, realloc and try again
	while (status == STATUS_INFO_LENGTH_MISMATCH)
	{
		PSYSTEM_HANDLE_INFORMATION temp_p = (PSYSTEM_HANDLE_INFORMATION)realloc(handleInfo, handleInfoSize);
		if (temp_p)
		{
			handleInfo = temp_p;
			status = NtQuerySystemInformation(SystemHandleInformation, handleInfo, handleInfoSize, &handleInfoSize);
		}
		else
		{
			return(NULL);  // system mem is insufficient
		}
	}

	// if NtQuerySystemInformation stopped return STATUS_INFO_LENGTH_MISMATCH
	if (!NT_SUCCESS(status))
	{
		printf("NtQuerySystemInformation failed!\n");
		return(NULL);
	}

	return(handleInfo);
}