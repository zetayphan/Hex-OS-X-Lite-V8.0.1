#!/usr/bin/env python3
"""HEX OS source fabric: inspect/extract all five source projects."""
from pathlib import Path
import argparse,importlib.util,base64,zlib
ROOT=Path(__file__).resolve().parents[1]
def assets():
 for p in sorted((ROOT/'system'/'fabric').glob('fabric_*.py')):
  spec=importlib.util.spec_from_file_location(p.stem,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  for name,blob in mod.ASSETS.items():yield name,zlib.decompress(base64.b85decode(blob))
def extract(dest=None):
 dest=Path(dest or ROOT/'workspace'/'recovered_projects').resolve();dest.mkdir(parents=True,exist_ok=True)
 count=0
 for name,data in assets():
  target=(dest/name).resolve()
  if not target.is_relative_to(dest):raise ValueError('unsafe path')
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);count+=1
 return count,dest

# The original engines are bundled as compressed source, rather than shipped as
# independent files. Restore on demand to a private runtime cache.
ENGINE_HINTS = {
 'nexus': ('HEX_NEXUS_X',),
 'research': ('Hex_Unified_Research_Lab',),
 'studio': ('Hex_Studio_Pro',),
 'terminal': ('Hex_Terminal_Pro',),
 'omniverse': ('Hex_Omniverse',),
}
def resolve_engine_source(module, filename):
 if module not in ENGINE_HINTS or '/' in filename or '..' in filename:
  raise ValueError('unsupported engine source')
 dest=ROOT/'workspace'/'engine_cache'/module
 target=dest/filename
 if target.is_file():return target
 # Restore all files from the selected project to preserve sibling imports.
 count=0
 for name,data in assets():
  if not any(name.startswith(h) for h in ENGINE_HINTS[module]):continue
  parts=Path(name).parts
  # Locate a source file and place its siblings into a flat runtime module folder.
  if parts[-1].endswith(('.py','.json','.txt','.md')):
   path=dest/parts[-1]
   path.parent.mkdir(parents=True,exist_ok=True)
   if not path.exists():path.write_bytes(data)
   count+=1
 if not target.is_file():raise ValueError(f'engine {module}/{filename} not included in source fabric')
 return target

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['list','extract']);ap.add_argument('--dest');args=ap.parse_args()
 if args.command=='list':
  for n,_ in assets():print(n)
 else:
  count,path=extract(args.dest);print(f'Extracted {count} files into {path}')
