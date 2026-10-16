import json,re,math
from pathlib import Path
from collections import Counter
raw=json.loads(Path('../list-full.json').read_text())[0]
exclude={3,16,17,18,44,52,87,94,95,101,122,124,135,136,162,210,217,380,381,382,541,559,642,652,656,657,658,659,660,661,670,671,681,765}
rules={
'coffee':r'咖啡|珈琲|café|cafe|coffee|roastery|roasting|kaffe',
'dessert':r'霜淇淋|ice cream|侍茶|甜|冰|雪糕|蛋糕|千層|麻糬|烘焙|餅店|bakery|bakers|baking|dessert|cookie|gelato|froyo|菓子|蛋撻|布蕾|優格|yogurt|肉桂捲|可麗餅|鬆餅|銅鑼燒|鯛燒|華夫餅|奶茶|茶飲|茶莊|抹茶|matcha|churros|bakehouse|麵包',
'breakfast':r'早午餐|早餐|brunch|brekkie|breakfast|蛋餅|豆漿|吐司|三明治|sandwich|bagels',
'noodles':r'麵|麺|拉麵|米線|螺螄粉|螺螄|酸辣粉|河粉|米粉|noodle|ramen|白湯|小螺波|製麵|面線',
'japanese':r'日式|日本|日料|壽司|鮨|居酒屋|燒鳥|yakitori|拉麵|壽喜|和食|咖哩|咖喱|curry|kurry|カレー|御好燒|豬排|章魚燒|鰻|torigin|torisho|と米|和牛|五之神|油組',
'korean':r'韓|korea|seoul|gimbap|친구|김|돼지|감자|醬蟹|豬小嘻|燒酒烤烤|紫菜包飯',
'western':r'義式|義大利|法式|西班牙|美式|漢堡|burger|披薩|比薩|批薩|pizza|pizzeria|pasta|牛排|steak|tapas|薄餅|葡萄牙|墨式|澳洲|老墨',
'hotpot':r'鍋|火煱|羊肉爐|串串|麻辣燙|hotpot|hot pot|骨堡',
'bbq':r'烤肉|燒肉|串燒|燒鳥|炭烤|炙燒|bbq|燒烤|烤烤|炭火|烤上隱|yakitori|grill|五花肉',
'asian':r'泰式|泰國|越泰|印度|越南|南洋|河粉|laksa|thai|indian|delhi|kebap|印度|印渡|鷹嘴豆|hummus',
'bar':r'餐酒|酒吧|小酒館|bistro|\bbar\b|gastropub|酒食|lounge|生啤|brauhaus|bräu|釀酒',
'veggie':r'蔬食|素食|全素|素椒|不葷|樹食|veggie',
'other':r'餐廳|餐室|食堂|小餐館|restaurant|diner|eatery|私廚|鐵板|teppanyaki|烤魚|酸菜魚|洋食|沙拉',
'local':r'肉圓|小吃|夜市|牛肉湯|肉燥飯|滷肉飯|米糕|油飯|茶餐廳|港式|飲茶|煲仔|腸粉|餃|蚵仔|湯包|抄手|魷魚|地瓜球|蔥.*餅|龍鳳腿|虱目魚|割包|刈包|雞排|鹽酥|麻油雞|滷味|潤餅|肉羹|涼麵|生煎|肉包|排骨|便當|餐盒|燒臘|豬扒|台式|臺式|台菜|台灣|古早味|大排檔'}
manual={2:['western'],10:['japanese','bbq'],11:['dessert'],15:['japanese'],20:['dessert'],28:['dessert'],30:['dessert'],40:['other'],43:['dessert'],46:['japanese'],53:['dessert'],54:['dessert'],58:['western'],61:['dessert'],64:['western'],71:['other'],74:['dessert'],88:['breakfast'],92:['other'],104:['western'],107:['breakfast'],112:['other'],114:['breakfast'],115:['japanese'],118:['dessert'],123:['breakfast'],126:['dessert'],130:['local'],131:['local'],132:['local'],133:['local'],137:['japanese'],138:['western'],147:['western'],163:['dessert'],168:['local'],169:['local'],170:['dessert'],171:['dessert'],172:['dessert'],175:['local'],180:['local'],189:['japanese'],196:['local'],206:['dessert'],207:['bbq','japanese'],208:['dessert'],213:['local'],219:['asian','noodles'],220:['asian','noodles'],230:['veggie','japanese'],237:['local','noodles'],244:['other'],249:['japanese'],253:['japanese'],260:['korean','bbq'],271:['local'],277:['japanese'],280:['dessert'],281:['dessert'],282:['japanese'],288:['japanese'],301:['japanese','bbq'],310:['dessert'],311:['korean'],315:['local'],324:['bbq'],326:['local'],335:['dessert'],345:['japanese','noodles'],346:['dessert'],347:['dessert'],350:['local'],367:['hotpot'],369:['dessert'],370:['dessert'],374:['korean'],375:['dessert'],379:['japanese','noodles'],389:['noodles'],399:['local'],401:['dessert'],414:['dessert'],417:['dessert'],418:['dessert'],424:['western'],425:['western'],429:['breakfast'],430:['noodles'],431:['asian'],436:['dessert'],439:['dessert'],444:['japanese','noodles'],457:['korean'],465:['dessert'],470:['dessert'],479:['dessert'],481:['breakfast','western'],486:['dessert'],487:['dessert'],491:['coffee'],497:['japanese'],503:['breakfast'],504:['breakfast'],508:['dessert'],510:['breakfast'],511:['coffee'],515:['dessert'],518:['dessert'],520:['dessert'],529:['breakfast'],533:['dessert'],537:['korean'],542:['hotpot'],543:['korean','hotpot'],551:['other'],553:['japanese'],556:['dessert'],557:['dessert'],563:['breakfast'],566:['dessert'],570:['local'],573:['bbq'],576:['local','bbq'],578:['dessert'],582:['western'],583:['dessert'],584:['korean'],591:['dessert'],594:['breakfast'],599:['dessert'],600:['dessert'],601:['dessert'],602:['other'],608:['dessert'],609:['dessert'],613:['dessert'],614:['dessert'],615:['dessert'],616:['breakfast'],619:['asian'],621:['coffee'],622:['dessert'],624:['dessert'],628:['asian','bar'],631:['local'],635:['western'],637:['dessert'],638:['local'],639:['other'],640:['dessert'],641:['local'],643:['local'],647:['western'],648:['breakfast'],650:['western'],651:['western'],653:['western'],654:['dessert'],655:['dessert'],662:['dessert'],665:['western'],666:['western'],667:['western'],668:['dessert'],669:['dessert'],672:['western','bar'],673:['western','bar'],674:['dessert'],675:['western','bar'],677:['asian'],678:['asian'],679:['dessert'],680:['coffee','dessert'],682:['western'],690:['coffee'],692:['coffee'],694:['bbq','bar'],700:['noodles'],704:['other'],706:['other'],710:['korean'],711:['dessert'],731:['korean'],738:['local','bar'],739:['other'],740:['local'],742:['noodles'],744:['other'],747:['japanese'],751:['japanese'],753:['dessert'],756:['japanese'],759:['western'],763:['japanese'],764:['dessert'],766:['dessert'],767:['dessert'],768:['japanese','dessert'],771:['asian','noodles'],775:['local'],776:['hotpot'],777:['hotpot','korean'],778:['dessert'],780:['veggie'],781:['local','noodles'],783:['hotpot','korean'],787:['asian','noodles'],788:['hotpot','korean']}
items=[]
for i,x in enumerate(raw[8]):
 detail=x[1];lat,lon=detail[5][2:4];assert math.isfinite(lat) and -90<=lat<=90 and math.isfinite(lon) and -180<=lon<=180
 name=x[2];tags=manual.get(i) or [k for k,v in rules.items() if re.search(v,name[:120],re.I)]
 if i in exclude:tags=['excluded']
 if not tags:tags=['uncategorized']
 cid=str(int(detail[6][1])%(1<<64));items.append(dict(id=cid,name=name,address=detail[4] or detail[2] or '',lat=lat,lon=lon,categories=tags,url='https://www.google.com/maps?cid='+cid))
assert len(items)==raw[12]==789
out={'listName':'想去的地點','owner':'Pei','importedAt':'2026-10-16','total':len(items),'places':items}
Path('dist/data/places.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print('imported',len(items),'unique',len({x['id'] for x in items}));print(Counter(c for x in items for c in x['categories']));print('uncertain',[(i,x['name']) for i,x in enumerate(items) if x['categories']==['uncategorized']])
