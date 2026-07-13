from __future__ import annotations
import hashlib, json
from typing import Any
class PipelineCache:
    def __init__(self)->None: self._data: dict[str,dict[str,Any]]={}
    def build_key(self,*,stage_name:str,stage_version:str,payload:dict[str,Any])->str:
        serialized=json.dumps(payload,sort_keys=True,default=str,separators=(',',':'))
        return f"{stage_name}:{stage_version}:{hashlib.sha256(serialized.encode()).hexdigest()}"
    def get(self,key:str)->dict[str,Any]|None:
        value=self._data.get(key); return None if value is None else dict(value)
    def set(self,key:str,value:dict[str,Any])->None: self._data[key]=dict(value)
    def clear(self)->None: self._data.clear()
    def size(self)->int: return len(self._data)
