import json,subprocess,os,sys
from PIL import Image,ImageDraw,ImageFont
M={'FOREST':'forest','LIBRARY':'library','WAREHOUSE':'plant2','TOWER':'tower','CHAPEL':'chapel','SINKING':'water','GREENACRES':'02greenacres','RASH':'rash','MACHINE':'machine','STAGEX':'stage5wip','WHITEOUT':'whiteout','EX_LYCAEUM':'lycaeum','COOP':'coop','SPAZIE':'space','CARLOCART':'carlocart','LABORRATORY':'laborratory','EX_WESTWOODS':'westwoods','BATCOUNTRY':'forest_batcountry','ASTRALSTAIR':'astralstair','EX_MAZERELLA':'mazerella','TOWERBRIDGE':'towerbridge','DEVILROOM':'devilroom'}
R='/home/claude/luckeys-lab.github.io';items=json.load(open(R+'/data/vs/items.json'))
N=json.load(open('/tmp/cards/cards/base/stage_names.json'))
os.makedirs('/home/claude/map/out',exist_ok=True)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
SKIP=('PlayerStart','MRC','BatDragonSpawn','GEM','Deco','Window','Wind','NoShadow','HardBounds','TRAINCOORDS','center','AccelPosition','GoalPosition','ColossusTarget','Wall1','DarkassoTrigger','TELEPORT','RelicPosition','Spawning')
NOISE=('Tile_','Eye','Drowner','Door','Lever','DancerDeadEnd','LYCA_DOOR')
LBL={'CFF':'COFFIN','Coffin':'COFFIN'}
def icon(t):
  it=items.get(t)
  if it and it.get('i') and os.path.exists(R+it['i']):return Image.open(R+it['i']).convert('RGBA').resize((28,28),Image.NEAREST)
def mark(D,M_,x,y,o,i=0):
  ic=icon(o['t'])
  if ic:M_.alpha_composite(ic,(int(x-14),int(y-14)))
  else:D.text((x-14,y-8),LBL.get(o['t'],o['t'])[:7],fill=(255,255,255),font=f,stroke_width=2,stroke_fill=(0,0,0))
  if o['ch'] and float(o['ch'])<1:D.text((x+6,y+6),f"{int(float(o['ch'])*100)}%",fill=(255,230,120),font=f,stroke_width=2,stroke_fill=(0,0,0))
summary={}
for key,b in M.items():
  if key in sys.argv[1:] or len(sys.argv)==1:
    if not os.path.exists(f'/tmp/{b}.png.json'):subprocess.run(['python3','-I','/home/claude/map/rend.py',b,f'/tmp/{b}.png'],capture_output=True)
    if not os.path.exists(f'/tmp/{b}_L.json'):subprocess.run(['python3','-I','/home/claude/map/stage.py',b],capture_output=True)
  if not os.path.exists(f'/tmp/{b}_L.json'):summary[key]='FAIL';continue
  L=[o for o in json.load(open(f'/tmp/{b}_L.json')) if not o['n'].startswith('Object_') and o['t'] not in SKIP and not o['t'].startswith(NOISE)]
  FAR=[o for o in L if abs(o['xm'])>20 or abs(o['ym'])>20];L=[o for o in L if o not in FAR]
  st=[o for o in json.load(open(f'/tmp/{b}_L.json')) if o['t']=='PlayerStart']
  BG=Image.open(f'/tmp/{b}.png').convert('RGBA');G=json.load(open(f'/tmp/{b}.png.json'))
  tp=lambda o:(((o['px']/100/0.32)-G['x0'])*G['P'],((G['y1']+1)+o['py']/100/0.32)*G['P'])
  tiled=any(o['xm'] or o['ym'] for o in L)
  if tiled:
    xs=[o['xm'] for o in L]+[0];ys=[o['ym'] for o in L]+[0];x0,x1,y0,y1=min(xs)-1,max(xs)+1,min(ys)-1,max(ys)+1;C=72
    bg=BG.resize((C,int(C*BG.height/BG.width)),Image.LANCZOS);CH=bg.height
    img=Image.new('RGBA',((x1-x0+1)*C,(y1-y0+1)*CH));D=ImageDraw.Draw(img)
    for gx in range(x0,x1+1):
      for gy in range(y0,y1+1):img.paste(bg,((gx-x0)*C,(y1-gy)*CH));D.rectangle(((gx-x0)*C,(y1-gy)*CH,(gx-x0)*C+C-1,(y1-gy)*CH+CH-1),outline=(0,0,0,90))
    px,py=(0-x0)*C,(y1-0)*CH;D.rectangle((px+2,py+2,px+C-3,py+CH-3),outline=(255,215,0),width=3)
    cnt={}
    for o in L:
      k=(o['xm'],o['ym']);i=cnt.get(k,0);cnt[k]=i+1;px,py=(k[0]-x0)*C,(y1-k[1])*CH
      mark(D,img,px+18+(i%2)*34,py+20+(i//2)*26,o)
  else:
    s=min(1.0,1600/max(BG.size));img=BG.resize((int(BG.width*s),int(BG.height*s)),Image.LANCZOS);D=ImageDraw.Draw(img)
    for o in st:x,y=tp(o);D.ellipse((x*s-12,y*s-12,x*s+12,y*s+12),outline=(255,215,0),width=4)
    for o in L:x,y=tp(o);mark(D,img,x*s,y*s,o)
  if max(img.size)>1400:s2=1400/max(img.size);img=img.resize((int(img.width*s2),int(img.height*s2)),Image.LANCZOS)
  img.save(f'/home/claude/map/out/{key}.png')
  summary[key]={'n':N.get(key,{}).get('ko',{}).get('stageName',key),'tiled':tiled,'items':len(L),'size':img.size,'types':sorted({o['t'] for o in L}),'far':[(o['t'],o['xm'],o['ym']) for o in FAR]}
json.dump(summary,open('/home/claude/map/out/summary.json','w'),ensure_ascii=False,indent=0)
for k,v in summary.items():print(k,v if v=='FAIL' else (v['n'],v['tiled'],v['items'],v['size'],v['types'][:14]))
