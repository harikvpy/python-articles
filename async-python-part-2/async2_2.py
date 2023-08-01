# async2_2.py
import dis

def gtask2():
    yield 10

def gtask1():
    yield from gtask2()

async def atask2():
    pass

async def atask1():
    await atask2()

print('gtask1 disassembly:-')
dis.dis(gtask1)

print('atask1 disassembly:-')
dis.dis(atask1)
