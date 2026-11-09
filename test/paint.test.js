import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.join(__dirname, '..');

test('Black Paint Studio - Arquivos Essenciais Existem', () => {
    const requiredFiles = ['index.html', 'style.css', 'app.js', 'brushes.js', 'filters.js', 'gpu.js', 'server.js', 'academy.js', 'academy-data.js', 'academy-guides.js', 'misuki.json', 'misuki.js', 'render_stroke_portrait.py', 'render_misuki_construct.py', 'render_painted_character.py', 'render_natural_character.py', 'package.json'];
    for (const file of requiredFiles) {
        assert.ok(fs.existsSync(path.join(projectRoot, file)), `Arquivo essencial ausente: ${file}`);
    }
});

test('Academia reúne 20+ aulas práticas originais com exercícios por etapas', () => {
    const source=fs.readFileSync(path.join(projectRoot,'academy-data.js'),'utf8');
    const sandbox={window:{}};
    vm.runInNewContext(source,sandbox);
    vm.runInNewContext(fs.readFileSync(path.join(projectRoot,'academy-guides.js'),'utf8'),sandbox);
    const lessons=sandbox.window.PaintAcademyCourses;
    assert.ok(lessons.length>=20);
    assert.equal(new Set(lessons.map(lesson=>lesson.id)).size,lessons.length);
    assert.ok(lessons.some(lesson=>/casa|prédio/i.test(lesson.title)));
    assert.ok(lessons.some(lesson=>/personagem|rosto|mãos/i.test(lesson.title)));
    assert.ok(lessons.every(lesson=>lesson.steps.length>=4&&lesson.goal&&lesson.setup.material));
    assert.ok(lessons.every(lesson=>lesson.practice&&lesson.checks.length===3&&lesson.pitfall&&sandbox.window.PaintAcademyReferences[lesson.referenceId]));
});

test('BrushEngine desenha exatamente a quantidade de eixos de simetria escolhida', () => {
    const source = fs.readFileSync(path.join(projectRoot, 'brushes.js'), 'utf8');
    const sandbox = { Math, globalThis:null };
    sandbox.globalThis = sandbox;
    vm.runInNewContext(`${source}\nglobalThis.BrushEngine = BrushEngine;`, sandbox);
    const strokes = [];
    let current = null;
    const ctx = {
        save(){}, restore(){}, beginPath(){ current=[]; strokes.push(current); },
        moveTo(x,y){ current.push([x,y]); }, lineTo(x,y){ current.push([x,y]); }, stroke(){},
    };
    const engine = new sandbox.BrushEngine(ctx, ctx);
    engine.drawSymmetry(60, 50, 70, 50, 50, 50, '#fff', 2, 0, 6);
    assert.equal(strokes.length, 6);
    assert.ok(strokes.every(points => points.length === 2));
});

test('BrushEngine pinta óleo com cerdas e a interface lista os materiais suportados', () => {
    const source = fs.readFileSync(path.join(projectRoot, 'brushes.js'), 'utf8');
    const sandbox = { Math, globalThis:null };
    sandbox.globalThis = sandbox;
    vm.runInNewContext(`${source}\nglobalThis.BrushEngine = BrushEngine;`, sandbox);
    let strokes = 0;
    const ctx = { save(){}, restore(){}, beginPath(){}, moveTo(){}, lineTo(){}, stroke(){strokes++;} };
    new sandbox.BrushEngine(ctx, ctx).drawMaterial(1, 2, 30, 24, '#c03050', 18, 'oil', 1, .8);
    assert.ok(strokes >= 5, 'óleo deve depositar várias cerdas em paralelo');
    const html = fs.readFileSync(path.join(projectRoot, 'index.html'), 'utf8');
    for (const medium of ['oil-dry','impasto','watercolor','gouache','acrylic','pastel','charcoal','pencil','ink','marker','airbrush','smudge']) {
        assert.ok(html.includes(`value="${medium}"`), `material ausente: ${medium}`);
    }
});

test('Pincel a óleo mantém as mesmas cerdas ao longo do gesto', () => {
    const source = fs.readFileSync(path.join(projectRoot, 'brushes.js'), 'utf8');
    const sandbox = { Math, globalThis:null };
    sandbox.globalThis = sandbox;
    vm.runInNewContext(source + '\nglobalThis.BrushEngine = BrushEngine;', sandbox);
    const lines = [];
    let point;
    const ctx = {
        save(){}, restore(){}, beginPath(){}, moveTo(x,y){point=[x,y];},
        lineTo(x,y){lines.push([point,[x,y]]);}, stroke(){}
    };
    const engine = new sandbox.BrushEngine(ctx, ctx);
    engine.beginStroke('oil', 24);
    engine.drawMaterial(10, 50, 40, 50, '#c03050', 24, 'oil', 1, 1);
    const firstOffsets = lines.map(line => line[0][1] - 50);
    lines.length = 0;
    engine.drawMaterial(40, 50, 70, 50, '#c03050', 24, 'oil', 1, 1);
    const nextOffsets = lines.map(line => line[0][1] - 50);
    assert.deepEqual(nextOffsets, firstOffsets, 'as cerdas não devem saltar entre quadros do mesmo gesto');
    engine.endStroke();
});

test('Balde de tinta preenche tons antialias vizinhos sem atravessar a borda', () => {
    const source = fs.readFileSync(path.join(projectRoot, 'filters.js'), 'utf8');
    const sandbox = { Math, Uint8ClampedArray, Int32Array, document:{
        createElement(){ return { style:{}, remove(){} }; },
        body:{ appendChild(){}, removeChild(){} },
    }, window:{ getComputedStyle(){ return { color:'rgb(255, 0, 0)' }; } }, globalThis:null };
    sandbox.globalThis=sandbox;
    vm.runInNewContext(`${source}\nglobalThis.PaintGenerators = PaintGenerators;`,sandbox);
    const pixels=new Uint8ClampedArray([
        10,10,10,255, 11,10,10,255, 90,90,90,255,
        10,10,10,255, 12,10,10,255, 90,90,90,255,
    ]);
    const ctx={getImageData(){return {data:pixels};},putImageData(img){this.result=img.data;}};
    sandbox.PaintGenerators.floodFill(ctx,0,0,'#ff0000',3,2);
    assert.equal(ctx.result[0],255); assert.equal(ctx.result[4],255);
    assert.equal(ctx.result[12],255); assert.equal(ctx.result[16],255);
    assert.equal(ctx.result[8],90); assert.equal(ctx.result[20],90);
});

test('Black Paint Studio - Servidor HTTP e Endpoint de Status', async () => {
    const { server } = await import('../server.js');
    
    await new Promise((resolve) => server.listen(3399, '127.0.0.1', resolve));

    try {
        const responseData = await new Promise((resolve, reject) => {
            http.get('http://127.0.0.1:3399/api/status', (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve({ status: res.statusCode, data: JSON.parse(data) }));
            }).on('error', reject);
        });

        assert.equal(responseData.status, 200);
        assert.equal(responseData.data.ok, true);
        assert.equal(responseData.data.name, 'Black Paint Studio');
        const expectedVersion = JSON.parse(fs.readFileSync(path.join(projectRoot, 'package.json'), 'utf8')).version;
        assert.equal(responseData.data.version, expectedVersion, 'a versão do servidor deve bater com o package.json');
        assert.ok(responseData.data.misuki.available);
        const misuki = await new Promise((resolve, reject) => {
            http.get('http://127.0.0.1:3399/api/misuki?pose=profile', (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(data) }));
            }).on('error', reject);
        });
        assert.equal(misuki.status, 200);
        assert.equal(misuki.body.ok, true);
        assert.ok(misuki.body.prompt.includes('Misuki'));
    } finally {
        await new Promise((resolve) => server.close(resolve));
    }
});

test('PaintGPU detecta API e não quebra sem WebGL', () => {
    const source = fs.readFileSync(path.join(projectRoot, 'gpu.js'), 'utf8');
    const sandbox = {
        window: {},
        document: { createElement() { return { getContext() { return null; } }; } },
        WebGL2RenderingContext: function WebGL2RenderingContext() {}
    };
    sandbox.window = sandbox;
    vm.runInNewContext(source, sandbox);
    const info = sandbox.window.PaintGPU.detect();
    assert.equal(info.available, false);
    assert.equal(typeof sandbox.window.PaintGPU.applyFinish, 'function');
});

test('Bíblia da Misuki monta prompt estável e a academia tem a trilha', () => {
    const card = JSON.parse(fs.readFileSync(path.join(projectRoot, 'misuki.json'), 'utf8'));
    assert.equal(card.name, 'Misuki');
    assert.ok(card.promptCore.includes('BLACKCORE'));
    assert.ok(card.promptCore.includes('red eyes'));
    assert.ok(card.promptCore.includes('horns'));
    assert.ok(card.poses.front && card.poses.profile);
    const source = fs.readFileSync(path.join(projectRoot, 'misuki.js'), 'utf8');
    const sandbox = { window: {} };
    vm.runInNewContext(source, sandbox);
    const prompt = sandbox.window.MisukiStudio.buildPrompt(card, 'profile');
    assert.ok(prompt.includes('perfil') || prompt.includes('Misuki'));
    const academySource = fs.readFileSync(path.join(projectRoot, 'academy-data.js'), 'utf8');
    const guides = fs.readFileSync(path.join(projectRoot, 'academy-guides.js'), 'utf8');
    const academyBox = { window: {} };
    vm.runInNewContext(academySource, academyBox);
    vm.runInNewContext(guides, academyBox);
    const misukiLessons = academyBox.window.PaintAcademyCourses.filter(lesson => lesson.track === 'Misuki');
    assert.ok(misukiLessons.length >= 6);
    assert.ok(misukiLessons.every(lesson => lesson.checks.length === 3 && lesson.referenceId === 'misuki'));
});

test('Servidor não entrega scripts Python nem a pasta de testes', async () => {
    const { server } = await import('../server.js');
    await new Promise((resolve) => server.listen(3396, '127.0.0.1', resolve));
    try {
        for (const pathName of ['/paint_cli.py', '/test/paint.test.js', '/render_natural_character.py']) {
            const status = await new Promise((resolve, reject) => {
                http.get(`http://127.0.0.1:3396${pathName}`, (res) => {
                    res.resume();
                    res.on('end', () => resolve(res.statusCode));
                }).on('error', reject);
            });
            assert.equal(status, 404, pathName);
        }
    } finally {
        await new Promise((resolve) => server.close(resolve));
    }
});

test('Black Paint Studio - Servidor Serve index.html', async () => {
    const { server } = await import('../server.js');
    
    await new Promise((resolve) => server.listen(3398, '127.0.0.1', resolve));

    try {
        const responseData = await new Promise((resolve, reject) => {
            http.get('http://127.0.0.1:3398/', (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve({ status: res.statusCode, data }));
            }).on('error', reject);
        });

        assert.equal(responseData.status, 200);
        assert.ok(responseData.data.includes('BLACK PAINT STUDIO'));
    } finally {
        await new Promise((resolve) => server.close(resolve));
    }
});

test('Black Paint Studio - Endpoint gera PNG colorido localmente', async () => {
    const { server } = await import('../server.js');
    await new Promise((resolve) => server.listen(3396, '127.0.0.1', resolve));
    try {
        const result = await new Promise((resolve, reject) => {
            const req=http.request({hostname:'127.0.0.1',port:3396,path:'/api/generate/ink-portrait?style=color',method:'POST'},res=>{
                const chunks=[];
                res.on('data',chunk=>chunks.push(chunk));
                res.on('end',()=>resolve({status:res.statusCode,type:res.headers['content-type'],body:Buffer.concat(chunks)}));
            });
            req.on('error',reject); req.end();
        });
        assert.equal(result.status,200);
        assert.equal(result.type,'image/png');
        assert.equal(result.body.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
        assert.equal(result.body.readUInt32BE(16),900);
        assert.equal(result.body.readUInt32BE(20),1200);
        assert.equal(result.body.subarray(-8).toString('hex'),'49454e44ae426082');
    } finally {
        await new Promise((resolve) => server.close(resolve));
    }
});

test('Estudo do santuário é gerado pelo motor Python CPU e devolvido como PNG', async () => {
    const { server } = await import('../server.js');
    await new Promise((resolve) => server.listen(3395,'127.0.0.1',resolve));
    try {
        const result=await new Promise((resolve,reject)=>{
            const req=http.request({hostname:'127.0.0.1',port:3395,path:'/api/generate/study?type=shrine',method:'POST'},res=>{
                const chunks=[];res.on('data',chunk=>chunks.push(chunk));
                res.on('end',()=>resolve({status:res.statusCode,type:res.headers['content-type'],body:Buffer.concat(chunks)}));
            }); req.on('error',reject);req.end();
        });
        assert.equal(result.status,200); assert.equal(result.type,'image/png');
        assert.equal(result.body.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
        assert.equal(result.body.subarray(-8).toString('hex'),'49454e44ae426082');
    } finally { await new Promise(resolve=>server.close(resolve)); }
});

test('Casa e frutas podem ser geradas pelos novos botões do editor', async () => {
    const { server } = await import('../server.js');
    await new Promise(resolve=>server.listen(3393,'127.0.0.1',resolve));
    try {
        for (const kind of ['house','fruit']) {
            const result=await new Promise((resolve,reject)=>{
                const req=http.request({hostname:'127.0.0.1',port:3393,path:`/api/generate/study?type=${kind}`,method:'POST'},res=>{
                    const chunks=[];res.on('data',chunk=>chunks.push(chunk));
                    res.on('end',()=>resolve({status:res.statusCode,body:Buffer.concat(chunks)}));
                }); req.on('error',reject);req.end();
            });
            assert.equal(result.status,200,kind);
            assert.equal(result.body.readUInt32BE(16),900);
            assert.equal(result.body.readUInt32BE(20),1200);
            assert.equal(result.body.subarray(-8).toString('hex'),'49454e44ae426082');
        }
    } finally { await new Promise(resolve=>server.close(resolve)); }
});

test('Visão por referência delega ao BlackCore sem chave própria', async () => {
    const { server } = await import('../server.js');
    const tempDir=fs.mkdtempSync(path.join(os.tmpdir(),'paint-blackcore-test-'));
    const binary=path.join(tempDir,'blackcore');
    const log=path.join(tempDir,'argv.json');
    const oldBinary=process.env.BLACKCORE_BIN, oldLog=process.env.BLACKCORE_TEST_LOG;
    const oldFetch=globalThis.fetch;
    const elements=Array.from({length:8},(_,i)=>({
        path:`M ${20+i} 20 C 40 10 60 10 80 20 Z`,fill:'#112233',stroke:'#ffffff',strokeWidth:2,opacity:.8,brush:'oil'
    }));
    fs.writeFileSync(binary,`#!/usr/bin/env node\nconst fs=require('node:fs');\nconst args=process.argv.slice(2);\nconst image=args[args.indexOf('--image')+1];\nfs.writeFileSync(process.env.BLACKCORE_TEST_LOG,JSON.stringify({args,imageExists:fs.existsSync(image),imageMode:(fs.statSync(image).mode & 0o777)}));\nconsole.log('BlackCore response:');\nconsole.log(${JSON.stringify(JSON.stringify({title:'Estudo',background:'#000000',elements}))});\n`);
    fs.chmodSync(binary,0o755);
    process.env.BLACKCORE_BIN=binary;
    process.env.BLACKCORE_TEST_LOG=log;
    globalThis.fetch=async()=>{ throw new Error('Paint must not call Google directly'); };
    await new Promise(resolve=>server.listen(3394,'127.0.0.1',resolve));
    try {
        const payload=JSON.stringify({imageBase64:`data:image/png;base64,${Buffer.from('89504e470d0a1a0a','hex').toString('base64')}`,
            width:900,height:1350,model:'gemini-3.8-flash',style:'oil'});
        const result=await new Promise((resolve,reject)=>{
            const req=http.request({hostname:'127.0.0.1',port:3394,path:'/api/vision/paint',method:'POST',headers:{'Content-Type':'application/json'}},res=>{
                const chunks=[];res.on('data',chunk=>chunks.push(chunk));
                res.on('end',()=>resolve({status:res.statusCode,body:Buffer.concat(chunks).toString()}));
            });
            req.on('error',reject);req.end(payload);
        });
        assert.equal(result.status,200);
        const data=JSON.parse(result.body);
        assert.equal(data.model,'gemini-3.8-flash');
        assert.equal(data.elements.length,8);
        assert.equal(data.viewBoxHeight,1500);
        const delegated=JSON.parse(fs.readFileSync(log,'utf8'));
        assert.equal(delegated.args[delegated.args.indexOf('--provider')+1],'google');
        assert.equal(delegated.args[delegated.args.indexOf('--model')+1],'gemini-3.8-flash');
        assert.ok(delegated.args.includes('--no-session'));
        assert.equal(delegated.imageExists,true);
        assert.equal(delegated.imageMode,0o600);
        assert.ok(delegated.args[delegated.args.indexOf('--image')+1].endsWith('.png'));
    } finally {
        globalThis.fetch=oldFetch;
        if(oldBinary===undefined) delete process.env.BLACKCORE_BIN; else process.env.BLACKCORE_BIN=oldBinary;
        if(oldLog===undefined) delete process.env.BLACKCORE_TEST_LOG; else process.env.BLACKCORE_TEST_LOG=oldLog;
        fs.rmSync(tempDir,{recursive:true,force:true});
        await new Promise(resolve=>server.close(resolve));
    }
});

test('Black Paint Studio - Bloqueia traversal e rejeita uploads inválidos', async () => {
    const { server } = await import('../server.js');
    await new Promise((resolve) => server.listen(3397, '127.0.0.1', resolve));
    try {
        const request = (pathname, options = {}) => new Promise((resolve, reject) => {
            const req = http.request({ hostname:'127.0.0.1', port:3397, path:pathname, method:options.method || 'GET', headers:options.headers || {} }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve({ status:res.statusCode, data, headers:res.headers }));
            });
            req.on('error', reject);
            if (options.body) req.write(options.body);
            req.end();
        });
        const traversal = await request('/%2e%2e%2fpackage.json');
        assert.equal(traversal.status, 403);
        const upload = await request('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ filename:'test.png', imageBase64:'data:image/jpeg;base64,AAAA' }) });
        assert.equal(upload.status, 400);
        assert.equal(JSON.parse(upload.data).ok, false);
        const truncated = await request('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ filename:'broken.png', imageBase64:`data:image/png;base64,${Buffer.from('89504e470d0a1a0a','hex').toString('base64')}` }) });
        assert.equal(truncated.status, 400);
        const status = await request('/api/status');
        assert.equal(status.headers['x-content-type-options'], 'nosniff');
    } finally {
        await new Promise((resolve) => server.close(resolve));
    }
});
