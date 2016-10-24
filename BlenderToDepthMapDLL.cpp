// BlenderToDepthMapDLL.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "BlenderToDepthMapDLL.h"

#define BUF_SIZE 4194304
TCHAR szName[] = TEXT("Local\\MyFileMappingObject");
TCHAR szMsg[] = TEXT("Message from first process.");

#pragma comment(lib, "user32.lib")

struct Harambe {
	PVOID BufferLoc;
	HANDLE hMapFile;
	int BufferX;
	int BufferY;
};

void* CreateDepthBufMapFile(int BufferX, int BufferY)
{
	static Harambe DataStruct;
	void *pBuf;

	DataStruct.hMapFile = CreateFileMapping(
		INVALID_HANDLE_VALUE,    // use paging file
		NULL,                    // default security
		PAGE_READWRITE,          // read/write access
		0,                       // maximum object size (high-order DWORD)
		BUF_SIZE,                // maximum object size (low-order DWORD)
		szName);                 // name of mapping object

	if (DataStruct.hMapFile == NULL)
	{
		_tprintf(TEXT("Could not create file mapping object (%d).\n"),
			GetLastError());
		return 0;
	}
	pBuf = MapViewOfFile(DataStruct.hMapFile,   // handle to map object
		FILE_MAP_ALL_ACCESS, // read/write permission
		0,
		0,
		BUF_SIZE);

	if (pBuf == NULL)
	{
		_tprintf(TEXT("Could not map view of file (%d).\n"),
			GetLastError());

		CloseHandle(DataStruct.hMapFile);

		return 0;
	}
	//return 0;

	DataStruct.BufferX = BufferX;
	DataStruct.BufferY = BufferY;
	DataStruct.BufferLoc = pBuf;
	return &DataStruct;
}

int GetBufferX(void* InDS) {
	Harambe *HDS = (Harambe*)InDS;
	return HDS->BufferX;
}

int GetBufferY(void* InDS) {
	Harambe *HDS = (Harambe*)InDS;
	return HDS->BufferY;
}

int WriteDepthMapBufFile(void* InDataStruct, void* PtrInputBuf, int BufLen) {
	Harambe *HarDataStruct = (Harambe*)InDataStruct;
	float *InputBuf = (float*)PtrInputBuf;

	CopyMemory(HarDataStruct->BufferLoc, InputBuf, (BufLen * sizeof(float)));

	//_getch();
	return 0;
}

int UnmapDepthBufFile(void* UnmapFileStruct) {
	Harambe *HarUnmapFileStruct = (Harambe*)UnmapFileStruct;
	UnmapViewOfFile(HarUnmapFileStruct->BufferLoc);

	CloseHandle(HarUnmapFileStruct->hMapFile);

	return 47;
}

void* OpenDepthBufMapFileToRead()
{
	static Harambe DataStruct;
	void *pBuf;

	DataStruct.hMapFile = OpenFileMapping(
		FILE_MAP_ALL_ACCESS,   // read/write access
		FALSE,                 // do not inherit the name
		szName);               // name of mapping object

	if (DataStruct.hMapFile == NULL)
	{
		_tprintf(TEXT("Could not open file mapping object (%d).\n"),
			GetLastError());
		return 0;
	}

	pBuf = MapViewOfFile(DataStruct.hMapFile, // handle to map object
		FILE_MAP_ALL_ACCESS,  // read/write permission
		0,
		0,
		BUF_SIZE);

	if (pBuf == NULL)
	{
		_tprintf(TEXT("Could not map view of file (%d).\n"),
			GetLastError());

		CloseHandle(DataStruct.hMapFile);

		return 0;
	}

	DataStruct.BufferLoc = pBuf;
	return &DataStruct;
	//MessageBox(NULL, pBuf, TEXT("Process2"), MB_OK);
}

void* ReadDepthMapBufFile(void* InDataStruct) {
	Harambe *HarDataStruct = (Harambe*)InDataStruct;

	return (void*)HarDataStruct->BufferLoc;
}