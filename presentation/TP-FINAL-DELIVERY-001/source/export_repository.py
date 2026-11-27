"""Export the exact tracked bytes at the product revision, independent of autocrlf."""
import io
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

pack=Path(__file__).resolve().parents[1]
repo=pack.parents[1]
revision=subprocess.check_output(["git","rev-parse","cf448f3"],cwd=repo).strip()
tree=subprocess.check_output(["git","ls-tree","-rz",revision.decode()],cwd=repo)
entries=[]
for line in tree.rstrip(b"\0").split(b"\0"):
    header,name=line.split(b"\t",1)
    mode,kind,oid=header.split()
    assert kind==b"blob"
    entries.append((name.decode(),oid,int(mode,8)))
objects=subprocess.run(["git","cat-file","--batch"],cwd=repo,input=b"".join(oid+b"\n" for _,oid,_ in entries),capture_output=True,check=True)
data=io.BytesIO(objects.stdout)
archive=pack/"02_PROJECT_DOCUMENTS/repository/TestPilot-AI_cf448f3.zip"
with ZipFile(archive,"w",ZIP_DEFLATED,compresslevel=6) as out:
    out.comment=revision
    for name,oid,mode in entries:
        returned,kind,size=data.readline().split()
        assert returned==oid and kind==b"blob"
        entry=ZipInfo("TestPilot-AI/"+name,date_time=(2026,11,27,0,0,0))
        entry.create_system=3
        entry.external_attr=mode<<16
        out.writestr(entry,data.read(int(size)),compress_type=ZIP_DEFLATED,compresslevel=6)
        assert data.read(1)==b"\n"
assert data.read()==b""
