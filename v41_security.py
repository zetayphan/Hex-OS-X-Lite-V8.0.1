"""V41 local-only static-file isolation and browser hardening."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
HEADERS={'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self' 'unsafe-inline' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'",'Cross-Origin-Resource-Policy':'same-origin'}
ALLOWED_EXT={'.html','.js','.css','.png','.jpg','.jpeg','.svg','.ico','.webp','.woff','.woff2','.json'}
def allowed_static(path):
 p=unquote(urlsplit(path).path)
 if '\\' in p or '\x00' in p:return False
 parts=Path(p).parts
 return len(parts)>=3 and parts[1]=='web' and '..' not in parts and Path(p).suffix.lower() in ALLOWED_EXT and not any(x.startswith('.') for x in parts)
def public_path(root,path):
 p=unquote(urlsplit(path).path).lstrip('/')
 candidate=(root/p).resolve()
 public=(root/'web').resolve()
 if not allowed_static('/'+p) or not candidate.is_relative_to(public):return str(root/'__blocked__')
 return str(candidate)
def status():return {'version':'41.0','bind':'127.0.0.1','public_static_root':'/web/','private_source_blocked':True,'security_headers':list(HEADERS),'note':'Local-only development server; no authentication for remote exposure'}
