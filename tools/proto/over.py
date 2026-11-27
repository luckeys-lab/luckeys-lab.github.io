import json
from PIL import Image,ImageDraw,ImageFont
R='/home/claude/luckeys-lab.github.io';items=json.load(open(R+'/data/vs/items.json'))
L=json.load(open('/tmp/forest_L.json'))
xs=[o['xm'] for o in L]+[0];ys=[o['ym'] for o in L]+[0]
x0,x1,y0,y1=min(xs)-1,max(xs)+1,min(ys)-1,max(ys)+1;C=72
bg=Image.open('/tmp/forest.png').convert('RGBA').resize((C,C),Image.LANCZOS)
W,H=(x1-x0+1)*C,(y1-y0+1)*C;M=Image.new('RGBA',(W,H));D=ImageDraw.Draw(M)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
for gx in range(x0,x1+1):
  for gy in range(y0,y1+1):
    px,py=(gx-x0)*C,(y1-gy)*C;M.paste(bg,(px,py));D.rectangle((px,py,px+C-1,py+C-1),outline=(0,0,0,90))
def cell(gx,gy):return (gx-x0)*C,(y1-gy)*C
px,py=cell(0,0);D.rectangle((px+2,py+2,px+C-3,py+C-3),outline=(255,215,0),width=4);D.text((px+8,py+4),'START',fill=(255,215,0),font=f,stroke_width=2,stroke_fill=(0,0,0))
cnt={}
for o in L:
  if o['t'] in('PlayerStart','MRC','BatDragonSpawn'):continue
  k=(o['xm'],o['ym']);i=cnt.get(k,0);cnt[k]=i+1;px,py=cell(*k)
  it=items.get(o['t']);ic=None
  if it and it.get('i'):ic=Image.open(R+it['i']).convert('RGBA').resize((32,32),Image.NEAREST)
  if o['t']=='CFF':ic=None;o['t']='COFFIN'
  ox,oy=px+4+(i%2)*34,py+20+(i//2)*26
  if ic:M.alpha_composite(ic,(ox,oy))
  else:D.text((ox,oy),o['t'][:4],fill=(255,255,255),font=f,stroke_width=2,stroke_fill=(0,0,0))
  if o['ch'] and float(o['ch'])<1:D.text((ox+14,oy+20),f"{int(float(o['ch'])*100)}%",fill=(255,230,120),font=f,stroke_width=2,stroke_fill=(0,0,0))
M.save('/home/claude/map/forest_over.png');print(M.size)
