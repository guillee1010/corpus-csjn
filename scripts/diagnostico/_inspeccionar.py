lines = open('paginas/LibroVol329.1.md', encoding='utf-8').readlines()
out = ''.join(f'{i+1:5d}  {ln}' for i, ln in enumerate(lines[38:210]))
open('inspeccion_329_p5.txt','w',encoding='utf-8').write(out)
