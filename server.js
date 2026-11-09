/** Local Black Paint Studio server. */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PORT = Number.parseInt(process.env.PORT || '3333', 10);
// Keep the studio private to this phone unless the user explicitly opts into LAN access.
const HOST = process.env.HOST || '127.0.0.1';
const MAX_BODY_BYTES = 20 * 1024 * 1024;
let portraitGenerationBusy = false;
let studyGenerationBusy = false;
let visionPaintingBusy = false;
let lastVisionRequestAt = 0;
let localRenderBusy = false;
const PLAN_SCHEMA = 'Retorne SOMENTE JSON, sem markdown: {"title":"título","background":"#RRGGBB","viewBoxHeight":1200,"elements":[{"path":"M ... Z","fill":"#RRGGBB ou none","stroke":"#RRGGBB ou none","strokeWidth":1,"opacity":1,"brush":"oil"}]}. Todos os elementos exigem esses seis campos. brush: oil, wash, ink ou flat. Sem URLs ou comandos externos.';
const APP_VERSION = '2.3.0';
const MISUKI_POSES = new Set(['front','three-quarter','profile','smile','full']);
const PUBLIC_FILES = new Set([
  'index.html','style.css','app.js','brushes.js','filters.js',
  'academy.js','academy-data.js','academy-guides.js','presets.json',
  'misuki.json','misuki.js','gpu.js','project_io.js','demo_clip_style_cpu.png'
]);
const MIME_TYPES = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'application/javascript; charset=utf-8', '.json':'application/json; charset=utf-8', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml' };

function getTargetGalleryDir() {
  const configured = process.env.PAINT_OUTPUT_DIR;
  if (configured) { const dir = path.resolve(configured); fs.mkdirSync(dir,{recursive:true}); fs.accessSync(dir,fs.constants.W_OK); return dir; }
  const androidDownload = '/storage/emulated/0/Download';
  try { if (fs.existsSync(androidDownload)) { fs.accessSync(androidDownload, fs.constants.W_OK); return androidDownload; } } catch {}
  const localGallery = path.join(__dirname, 'gallery');
  fs.mkdirSync(localGallery, { recursive: true });
  return localGallery;
}
function json(res, status, payload) {
  res.writeHead(status, { 'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store' });
  res.end(JSON.stringify(payload));
}
function sendError(res, status, message) { json(res, status, { ok:false, error:message }); }
function loadMisukiCard() {
  return JSON.parse(fs.readFileSync(path.join(__dirname, 'misuki.json'), 'utf8'));
}
function buildMisukiPrompt(card, pose) {
  const key = MISUKI_POSES.has(pose) ? pose : 'front';
  const chosen = card.poses?.[key] || card.poses.front;
  return `${PLAN_SCHEMA} Crie 35 a 100 caminhos SVG no viewBox 0 0 1000 1200, em etapas de fundo, silhueta, anatomia, cabelo, roupa, olhos, luz. ${card.promptCore}. Pose: ${chosen}. ${card.promptFinish}. Avoid: ${card.negative}.`;
}
function findBlackcoreBinary() {
  const requested=process.env.BLACKCORE_BIN || 'blackcore';
  const candidates=requested.includes(path.sep) ? [requested] : String(process.env.PATH||'').split(path.delimiter).map(dir=>path.join(dir,requested));
  for(const candidate of candidates) { try { fs.accessSync(candidate,fs.constants.X_OK); return path.resolve(candidate); } catch {} }
  return null;
}
function execFileAsync(file,args,options) {
  return new Promise((resolve,reject)=>execFile(file,args,options,(error,stdout,stderr)=>error?reject(Object.assign(error,{stdout,stderr})):resolve({stdout,stderr})));
}
function runLocalRender(file, args, options, callback) {
  if (localRenderBusy) { queueMicrotask(() => callback(Object.assign(new Error('busy'), {code:'RENDER_BUSY'}))); return; }
  localRenderBusy = true;
  return execFile(file, args, {...options, cwd:__dirname}, (error, stdout, stderr) => {
    localRenderBusy = false;
    callback(error, stdout, stderr);
  });
}
function parseJsonObject(output) {
  const text=String(output||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');
  const start=text.indexOf('{'); if(start<0) throw new Error('missing-json');
  let depth=0,inString=false,escaped=false;
  for(let i=start;i<text.length;i++) { const c=text[i]; if(inString){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')inString=false;continue;} if(c==='"')inString=true;else if(c==='{')depth++;else if(c==='}'&&--depth===0)return JSON.parse(text.slice(start,i+1)); }
  throw new Error('incomplete-json');
}
function validPaintPlan(plan) {
  const hex = value => typeof value === 'string' && (/^#[0-9a-f]{6}$/i.test(value) || value === 'none');
  const validPath = value => {
    if (typeof value !== 'string' || value.length > 7000 || !/^[MmLlHhVvCcSsQqTtZz0-9eE+.,\-\s]+$/.test(value)) return false;
    const numbers=value.match(/[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g) || [];
    return numbers.length>=4 && numbers.every(part=>Number.isFinite(Number(part)) && Math.abs(Number(part))<=5000);
  };
  if (!plan || typeof plan !== 'object' || !hex(plan.background) || !Array.isArray(plan.elements) || plan.elements.length < 8 || plan.elements.length > 240) return false;
  return plan.elements.every(item => item && validPath(item.path) &&
    hex(item.fill) && hex(item.stroke) && Number.isFinite(item.strokeWidth) && item.strokeWidth >= 0 && item.strokeWidth <= 64 &&
    Number.isFinite(item.opacity) && item.opacity >= 0.04 && item.opacity <= 1 &&
    ['oil','wash','ink','flat'].includes(item.brush));
}
function imageMimeAndBytes(dataUrl) {
  const match = typeof dataUrl === 'string' && dataUrl.match(/^data:(image\/(?:png|jpeg|webp));base64,([A-Za-z0-9+/=\r\n]+)$/);
  if (!match) return null;
  const base64 = match[2].replace(/\s/g, '');
  if (base64.length > 16 * 1024 * 1024) return null;
  const bytes = Buffer.from(base64, 'base64');
  if (!bytes.length || bytes.length > 12 * 1024 * 1024) return null;
  const valid = match[1] === 'image/png' ? bytes.subarray(0,8).toString('hex') === '89504e470d0a1a0a' :
    match[1] === 'image/jpeg' ? bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff :
    bytes.toString('ascii',0,4) === 'RIFF' && bytes.toString('ascii',8,12) === 'WEBP';
  return valid ? { mime:match[1], base64 } : null;
}
function readBody(req, res) {
  return new Promise((resolve, reject) => {
    const chunks=[]; let size=0; let tooLarge=false;
    req.on('data', chunk => {
      if (tooLarge) return;
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        tooLarge=true; chunks.length=0; return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => {
      if (tooLarge) { sendError(res, 413, 'O envio excede o limite de 20 MB.'); reject(new Error('body-too-large')); return; }
      resolve(Buffer.concat(chunks).toString('utf8'));
    });
    req.on('error', err => reject(err));
    req.on('aborted', () => reject(new Error('request-aborted')));
  });
}

function isCompletePng(buffer) {
  if (buffer.length < 45 || buffer.subarray(0,8).toString('hex') !== '89504e470d0a1a0a') return false;
  if (buffer.readUInt32BE(8) !== 13 || buffer.toString('ascii',12,16) !== 'IHDR') return false;
  const width=buffer.readUInt32BE(16), height=buffer.readUInt32BE(20);
  if (!width || !height || width > 8192 || height > 8192 || width*height > 40_000_000) return false;
  let offset=8, foundEnd=false;
  while (offset+12 <= buffer.length) {
    const length=buffer.readUInt32BE(offset), type=buffer.toString('ascii',offset+4,offset+8);
    if (length > buffer.length-offset-12) return false;
    offset += length+12;
    if (type === 'IEND') { foundEnd=true; break; }
  }
  return foundEnd && offset === buffer.length;
}

const server = http.createServer(async (req, res) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Content-Security-Policy', "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'");
  const rawHost = req.headers.host || '';
  const expectedPort = server.address()?.port || PORT;
  const allowedHosts = new Set([`127.0.0.1:${expectedPort}`,`localhost:${expectedPort}`,`[::1]:${expectedPort}`,`${HOST}:${expectedPort}`]);
  if (HOST === '0.0.0.0' || HOST === '::') {
    for (const interfaces of Object.values(os.networkInterfaces())) for (const entry of interfaces || []) allowedHosts.add(`${entry.family === 'IPv6' ? `[${entry.address}]` : entry.address}:${expectedPort}`);
  }
  if (!allowedHosts.has(rawHost)) return sendError(res,403,'Host não autorizado. Use o endereço local do Paint.');
  if (req.headers.origin && req.headers.origin !== `http://${rawHost}`) return sendError(res,403,'Origem não autorizada.');
  if (req.headers['sec-fetch-site'] === 'cross-site') return sendError(res,403,'Origem não autorizada.');
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch { return sendError(res, 400, 'Endereço inválido.'); }
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
  if (pathname === '/api/status' && req.method === 'GET') return json(res, 200, {
    ok:true, name:'Black Paint Studio', version:APP_VERSION, port:PORT, host:HOST,
    vision:{ available:Boolean(findBlackcoreBinary()), provider:'BlackCore Google' },
    misuki:{ available:true, poses:[...MISUKI_POSES] }
  });
  if (pathname === '/api/misuki' && req.method === 'GET') {
    try {
      const card = loadMisukiCard();
      const pose = new URL(req.url,'http://localhost').searchParams.get('pose') || 'front';
      return json(res, 200, { ok:true, card, pose: MISUKI_POSES.has(pose)?pose:'front', prompt:buildMisukiPrompt(card, pose) });
    } catch {
      return sendError(res, 500, 'Não achei a bíblia da Misuki.');
    }
  }
  if (pathname === '/api/vision/paint' && req.method === 'POST') {
    if (visionPaintingBusy) return sendError(res, 429, 'A análise visual já está em andamento. Aguarde terminar.');
    const blackcore=findBlackcoreBinary();
    if (!blackcore) return sendError(res, 503, 'Não encontrei o comando blackcore. Inicie o Paint pelo BlackCore ou defina BLACKCORE_BIN com o caminho do executável BlackCore.');
    const now=Date.now();
    if (now-lastVisionRequestAt < 15000) return sendError(res, 429, 'Aguarde 15 segundos antes de iniciar outra criação.');
    let body;
    try {
      const raw=await readBody(req,res);
      if (res.headersSent) return;
      body=JSON.parse(raw);
    } catch (err) {
      if (res.headersSent || err.message === 'body-too-large') return;
      return sendError(res, 400, 'Não consegui ler os dados da referência.');
    }
    if (visionPaintingBusy) return sendError(res, 429, 'A análise visual já está em andamento. Aguarde terminar.');
    const image=imageMimeAndBytes(body?.imageBase64);
    const width=Number(body?.width), height=Number(body?.height);
    if (!image) return sendError(res, 400, 'Envie uma referência PNG, JPG ou WebP válida.');
    if (!Number.isInteger(width) || !Number.isInteger(height) || width<128 || height<128 || width>1440 || height>2400 || width*height>2_000_000)
      return sendError(res, 400, 'Dimensões da tela inválidas.');
    const selectedModel=typeof body.model === 'string' ? body.model : '';
    const model = selectedModel.trim() || process.env.BLACKCORE_MODEL || '';
    if (model && !/^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,99}$/.test(model)) return sendError(res,400,'Identificador do modelo inválido.');
    const styles={oil:'pintura a óleo digital feita com pinceladas visíveis, bordas variadas e mistura cromática controlada',
      watercolor:'aquarela em camadas transparentes, bordas suaves e reservas de papel',
      gouache:'guache opaco com massas de cor bem construídas e detalhes desenhados à mão',
      'anime-ink':'ilustração anime com lineart orgânica, espessura de linha variável e pintura cel-shading detalhada'};
    const style=styles[body.style] ? body.style : 'oil';
    const direction=typeof body.direction === 'string' ? body.direction.trim().slice(0,500) : '';
    const viewBoxHeight=Math.max(350,Math.min(2200,Math.round(1000*height/width)));
    const prompt=`${PLAN_SCHEMA} Use a imagem como referência sem reproduzir, embutir ou transformar os pixels originais. Crie uma NOVA ilustração independente, com o mesmo assunto principal e composição reconhecível, no estilo: ${styles[style]}. Orientação adicional do usuário: ${direction || 'preserve a identidade visual e os detalhes marcantes da referência'}.
Retorne um plano com 35 a 100 caminhos SVG, todos em coordenadas viewBox 0 0 1000 ${viewBoxHeight}. Crie primeiro fundo e grandes massas; depois silhueta e anatomia proporcionais; depois cabelo/roupa/objetos com curvas orgânicas, detalhes finos, sombras coloridas, luz e acentos finais. Varie tamanho, curvatura, sobreposição, cor e espessura como uma pessoa pintando; evite simetria perfeita, blocos geométricos genéricos, contorno preto uniforme e manchas aleatórias. Dê atenção especial às mãos, rosto e detalhes pequenos visíveis. Cada caminho deve ser uma forma ou pincelada útil, não ruído decorativo. Use somente comandos SVG M L H V C S Q T Z e números; coordenadas dentro do viewBox com margem máxima de 40. Cores somente #RRGGBB ou none. Nunca use URLs, scripts, filtros, imagens incorporadas ou texto. Elementos em ordem de pintura, do fundo para frente. Para pinceladas de óleo, misture formas preenchidas e traços de largura variável; para lineart, use traços finos orgânicos.`;
    visionPaintingBusy=true; lastVisionRequestAt=now;
    let tempDir;
    try {
      tempDir=await fs.promises.mkdtemp(path.join(os.tmpdir(),'black-paint-reference-'));
      const extension=image.mime==='image/png'?'.png':image.mime==='image/webp'?'.webp':'.jpg';
      const imagePath=path.join(tempDir,`reference${extension}`);
      await fs.promises.writeFile(imagePath,Buffer.from(image.base64,'base64'),{flag:'wx',mode:0o600});
      const {stdout}=await execFileAsync(blackcore,['--print',prompt,'--provider','google',...(model ? ['--model',model] : []),'--image',imagePath,'--no-session'],
        {cwd:__dirname,timeout:180000,maxBuffer:4*1024*1024,encoding:'utf8',windowsHide:true});
      let plan;
      try { plan=parseJsonObject(stdout); } catch { return sendError(res,502,'O BlackCore não devolveu um plano de pintura válido. Tente novamente ou escolha outro modelo.'); }
      if (!validPaintPlan(plan)) return sendError(res,502,'O plano do modelo tinha formas inválidas ou insuficientes; a tela foi preservada. Tente novamente com outro modelo.');
      return json(res,200,{ok:true,model,title:String(plan.title||'Pintura por referência').slice(0,100),background:plan.background,elements:plan.elements,viewBoxHeight});
    } catch (err) {
      if (err.code==='ETIMEDOUT' || err.killed) return sendError(res,504,'A análise demorou demais. Tente novamente com um modelo Flash.');
      if (err.code==='ENOENT') return sendError(res,503,'O executável BlackCore não está disponível para o servidor do Paint.');
      return sendError(res,502,'O BlackCore não conseguiu analisar a referência. Confira o provider Google, a conexão e os modelos configurados nele.');
    } finally { visionPaintingBusy=false; if(tempDir) await fs.promises.rm(tempDir,{recursive:true,force:true}).catch(()=>{}); }
  }
  if (pathname === '/api/generate/ink-portrait' && req.method === 'POST') {
    if (portraitGenerationBusy) return sendError(res, 429, 'Já estou renderizando um retrato. Tente novamente em instantes.');
    const requestedStyle=new URL(req.url,'http://localhost').searchParams.get('style') || 'color';
    const style=requestedStyle === 'oil' ? 'color' : requestedStyle;
    if (!['ink','color','natural','stroke','ibis','cel','misuki-natural'].includes(style)) return sendError(res, 400, 'Escolha color, ink, natural, stroke, ibis, cel ou misuki-natural.');
    portraitGenerationBusy = true;
    const output = path.join(os.tmpdir(), `black-paint-portrait-${randomUUID()}.png`);
    const python = process.env.PYTHON || 'python3';
    const renderer = style === 'misuki-natural' ? 'render_misuki_portrait.py'
      : style === 'stroke' ? 'render_stroke_portrait.py'
      : style === 'natural' ? 'render_natural_character.py'
      : (style === 'ibis' || style === 'cel') ? 'render_ibis_anime.py'
      : style === 'color' ? 'render_painted_character.py'
      : 'render_ink_character.py';
    const quality = new URL(req.url,'http://localhost').searchParams.get('quality') || 'standard';
    if (!['economy','standard'].includes(quality)) { portraitGenerationBusy=false; return sendError(res,400,'Qualidade inválida.'); }
    const portraitQuery=new URL(req.url,'http://localhost').searchParams;
    const expression=portraitQuery.get('expression') || 'neutral';
    const material=portraitQuery.get('material') || 'velvet';
    if (!['neutral','soft','happy','sad','angry','surprised'].includes(expression) || !['velvet','satin'].includes(material)) {
      portraitGenerationBusy=false;return sendError(res,400,'Expressão ou tecido inválido.');
    }
    const rendererArgs = style === 'misuki-natural' ? ['--width',quality === 'economy' ? '720' : '900','--quality',quality,'--output',output]
      : style === 'stroke' ? ['--variant', 'natural', '--output', output] : style === 'ink' ? ['--style', 'ink', '--output', output] : ['--output', output];
    if(style === 'misuki-natural')rendererArgs.push('--expression',expression,'--settings',path.join(__dirname,'presets',material+'.json'));
    return runLocalRender(python, [path.join(__dirname, renderer), ...rendererArgs],
      { timeout:90000, maxBuffer:1024*1024 }, async (err) => {
        portraitGenerationBusy = false;
        if (err) {
          if (err.code === 'RENDER_BUSY') return sendError(res,429,'Outro desenho local está em execução. Aguarde.');
          await fs.promises.unlink(output).catch(() => {});
          return sendError(res, 500, 'Não consegui renderizar. Confira se o Pillow está instalado no Termux.');
        }
        try {
          const png = await fs.promises.readFile(output);
          await fs.promises.unlink(output).catch(() => {});
          res.writeHead(200, { 'Content-Type':'image/png', 'Content-Length':png.length, 'Cache-Control':'no-store' });
          return res.end(png);
        } catch {
          await fs.promises.unlink(output).catch(() => {});
          return sendError(res, 500, 'A imagem foi renderizada, mas não consegui carregá-la.');
        }
      });
  }
  if (pathname === '/api/generate/study' && req.method === 'POST') {
    if (studyGenerationBusy) return sendError(res, 429, 'Já estou pintando um estudo. Aguarde um instante.');
    const type=new URL(req.url,'http://localhost').searchParams.get('type') || '';
    const filenames={shrine:'01_santuario_da_lua.png',city:'02_avenida_neon_chuvosa.png',cathedral:'03_catedral_do_eclipse.png',house:'04_casa_no_jardim.png',fruit:'05_natureza_morta_frutas.png'};
    if (!Object.hasOwn(filenames,type)) return sendError(res, 400, 'Escolha shrine, city, cathedral, house ou fruit.');
    studyGenerationBusy=true;
    const tempDir=path.join(os.tmpdir(),`black-paint-study-${randomUUID()}`);
    const output=path.join(tempDir,filenames[type]);
    const python=process.env.PYTHON || 'python3';
    return runLocalRender(python,[path.join(__dirname,'render_study_examples.py'),'--study',type,'--output-dir',tempDir],
      {timeout:60000,maxBuffer:1024*1024},async err=>{
        studyGenerationBusy=false;
        if (err) { if (err.code === 'RENDER_BUSY') return sendError(res,429,'Outro desenho local está em execução. Aguarde.'); await fs.promises.rm(tempDir,{recursive:true,force:true}).catch(()=>{}); return sendError(res,500,'Não consegui renderizar esse estudo local. Verifique o Pillow no Termux.'); }
        try {
          const png=await fs.promises.readFile(output);
          await fs.promises.rm(tempDir,{recursive:true,force:true}).catch(()=>{});
          res.writeHead(200,{'Content-Type':'image/png','Content-Length':png.length,'Cache-Control':'no-store'});
          return res.end(png);
        } catch {
          await fs.promises.rm(tempDir,{recursive:true,force:true}).catch(()=>{});
          return sendError(res,500,'O desenho foi gerado, mas não consegui abrir o PNG.');
        }
      });
  }
  if (pathname === '/api/generate/misuki' && req.method === 'POST') {
    let card;
    try { card = loadMisukiCard(); } catch { return sendError(res, 500, 'Bíblia da Misuki ausente.'); }
    const pose = new URL(req.url, 'http://localhost').searchParams.get('pose') || 'front';
    const prompt = buildMisukiPrompt(card, pose);
    const blackcore = findBlackcoreBinary();
    if (blackcore && process.env.MISUKI_FORCE_LOCAL !== '1') {
      if (visionPaintingBusy) return sendError(res, 429, 'A geração visual já está em andamento.');
      visionPaintingBusy = true;
      try {
        const { stdout } = await execFileAsync(blackcore, ['--print', prompt, '--provider', 'google', '--no-session'],
          { cwd: __dirname, timeout: 180000, maxBuffer: 4 * 1024 * 1024, encoding: 'utf8', windowsHide: true });
        let plan;
        try { plan = parseJsonObject(stdout); } catch { plan = null; }
        if (plan && validPaintPlan(plan)) {
          return json(res, 200, { ok: true, mode: 'plan', prompt, pose, background: plan.background, elements: plan.elements, viewBoxHeight: Math.max(350, Math.min(2200, Number(plan.viewBoxHeight) || 1200)), title: String(plan.title || 'Misuki').slice(0, 100) });
        }
      } catch {
        // Cai no estudo local; o prompt segue válido.
      } finally {
        visionPaintingBusy = false;
      }
    }
    const output = path.join(os.tmpdir(), `black-paint-misuki-${randomUUID()}.png`);
    const python = process.env.PYTHON || 'python3';
    return runLocalRender(python, [path.join(__dirname, 'render_misuki_portrait.py'), '--output', output],
      { timeout: 45000, maxBuffer: 1024 * 1024 }, async (err) => {
        if (err) {
          if (err.code === 'RENDER_BUSY') return sendError(res,429,'Outro desenho local está em execução. Aguarde.');
          await fs.promises.unlink(output).catch(() => {});
          return json(res, 200, { ok: true, mode: 'prompt-only', prompt, pose, hint: 'BlackCore e o estudo local falharam. Copie o prompt para o gerador.' });
        }
        try {
          const png = await fs.promises.readFile(output);
          await fs.promises.unlink(output).catch(() => {});
          return json(res, 200, { ok: true, mode: 'local-study', prompt, pose, imageBase64: `data:image/png;base64,${png.toString('base64')}`, hint:'Retrato natural procedural frontal. A pose solicitada depende do plano visual do BlackCore.' });
        } catch {
          await fs.promises.unlink(output).catch(() => {});
          return json(res, 200, { ok: true, mode: 'prompt-only', prompt, pose, hint: 'Estudo renderizado, mas o PNG não abriu.' });
        }
      });
  }
  if (pathname === '/api/save' && req.method === 'POST') {
    try {
      const raw = await readBody(req, res);
      if (res.headersSent) return;
      let data;
      try { data = JSON.parse(raw); } catch { return sendError(res, 400, 'JSON inválido.'); }
      const match = data && typeof data.imageBase64 === 'string' && data.imageBase64.match(/^data:image\/png;base64,([A-Za-z0-9+/=\r\n]+)$/);
      if (!match) return sendError(res, 400, 'Envie uma imagem PNG válida.');
      const buffer = Buffer.from(match[1], 'base64');
      if (!isCompletePng(buffer)) return sendError(res, 400, 'O arquivo enviado está incompleto ou não é um PNG válido.');
      const requestedName = typeof data.filename === 'string' ? data.filename : '';
      let safeName = path.basename(requestedName).replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 90) || `black_paint_${Date.now()}.png`;
      if (!/\.png$/i.test(safeName)) safeName += '.png';
      const outDir = getTargetGalleryDir();
      let outPath = path.join(outDir,safeName);
      for (let attempt=0; ; attempt++) {
        try { await fs.promises.writeFile(outPath,buffer,{flag:'wx',mode:0o600}); break; }
        catch (error) { if (error.code !== 'EEXIST' || attempt >= 5) throw error; safeName = `${path.parse(safeName).name.slice(0,70)}_${randomUUID().slice(0,8)}.png`; outPath = path.join(outDir,safeName); }
      }
      if (process.platform === 'android' || fs.existsSync('/data/data/com.termux/files/usr/bin/termux-media-scan')) {
        execFile('termux-media-scan', [outPath], { timeout:3000 }, () => {});
      }
      return json(res, 200, { ok:true, filename:safeName, path:outPath, sizeBytes:buffer.length });
    } catch (err) {
      if (res.headersSent || err.message === 'body-too-large') return;
      return sendError(res, 500, 'Não foi possível salvar a imagem.');
    }
  }
  if (req.method !== 'GET' && req.method !== 'HEAD') return sendError(res, 405, 'Método não permitido.');
  const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
  if (relative.includes('..') || relative.includes('\0')) return sendError(res, 403, 'Acesso negado.');
  if (relative.includes('/') || !PUBLIC_FILES.has(relative)) return sendError(res, 404, 'Arquivo não encontrado.');
  const filePath = path.resolve(__dirname, relative);
  if (filePath !== path.join(__dirname, relative)) return sendError(res, 403, 'Acesso negado.');
  try {
    const content = await fs.promises.readFile(filePath);
    res.writeHead(200, { 'Content-Type':MIME_TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream', 'Cache-Control':'no-cache' });
    return req.method === 'HEAD' ? res.end() : res.end(content);
  } catch (err) {
    if (err.code === 'ENOENT' || err.code === 'ENOTDIR') return sendError(res, 404, 'Arquivo não encontrado.');
    return sendError(res, 500, 'Erro ao ler o arquivo.');
  }
});

server.requestTimeout = 300000;
server.headersTimeout = 20000;

export { server, PORT, HOST, APP_VERSION, PUBLIC_FILES };
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  server.on('error', error => { console.error(error.code === 'EADDRINUSE' ? `Porta ${PORT} ocupada. Use PORT=3334 ou pare a instância anterior.` : error.message); process.exitCode=1; });
  server.listen(PORT, HOST, () => console.log(`Black Paint Studio ativo em http://localhost:${PORT}`));
}
