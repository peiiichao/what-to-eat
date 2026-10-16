import json,math
from pathlib import Path
raw=json.loads(Path('../list2-full.json').read_text())[0]
cats={0:['japanese'],1:['noodles','local'],2:['western'],3:['noodles','japanese'],4:['japanese'],5:['local'],6:['western'],7:['uncategorized'],8:['local'],9:['other']}
path=Path('dist/data/places.json');out=json.loads(path.read_text())
out['places']=[p for p in out['places'] if p.get('list')!='Cathay']
for p in out['places']:p.setdefault('list','想去的地點')
for i,x in enumerate(raw[8]):
 d=x[1];lat,lon=d[5][2:4];assert math.isfinite(lat) and math.isfinite(lon)
 cid=str(int(d[6][1])%(1<<64))
 out['places'].append(dict(id=cid,name=x[2],address=d[4] or d[2] or '',lat=lat,lon=lon,categories=cats[i],url='https://www.google.com/maps?cid='+cid,list='Cathay'))
out['total']=len(out['places']);out['lists']=['想去的地點','Cathay']
assert len({p['id'] for p in out['places']})==out['total']
path.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')));print(out['total'])
