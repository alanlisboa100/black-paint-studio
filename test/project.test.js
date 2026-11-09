import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import {server} from '../server.js';
const scope = {};
vm.runInNewContext(fs.readFileSync(new URL('../project_io.js',import.meta.url),'utf8'),scope);
const snapshot = {logicalWidth:128,logicalHeight:128,pixelRatio:1,width:128,height:128,activeLayerIndex:0,layers:[{id:1,name:'Base',dataUrl:'data:image/png;base64,AAAA',visible:true,opacity:1,blendMode:'source-over',clipping:false,alphaLock:false}]};
test('Projetos rejeitam tamanhos exagerados e camadas ambíguas', () => {
    const valid = {format:'black-paint-project',version:1,snapshot};
    assert.equal(scope.PaintProject.validate(valid),snapshot);
    assert.throws(() => scope.PaintProject.validate({...valid,snapshot:{...snapshot,width:1}}));
    assert.throws(() => scope.PaintProject.validate({...valid,snapshot:{...snapshot,layers:[snapshot.layers[0],snapshot.layers[0]]}}));
    assert.throws(() => scope.PaintProject.validate({...valid,snapshot:{...snapshot,layers:[{...snapshot.layers[0],dataUrl:'https://evil.test/image.png'}]}}));
});
test('Servidor bloqueia origem externa e salva sem sobrescrever', async () => {
    const folder=fs.mkdtempSync(path.join(os.tmpdir(),'paint-save-test-'));
    const old=process.env.PAINT_OUTPUT_DIR;process.env.PAINT_OUTPUT_DIR=folder;
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const port=server.address().port;
    const request=(payload,headers={})=>new Promise((resolve,reject)=>{
        const req=http.request({host:'127.0.0.1',port,path:'/api/save',method:'POST',headers:{'Content-Type':'application/json',...headers}},res=>{
            let data='';res.on('data',chunk=>data+=chunk);res.on('end',()=>resolve({status:res.statusCode,body:JSON.parse(data)}));
        });req.on('error',reject);req.end(JSON.stringify(payload));
    });
    try {
        assert.equal((await request({}, {Origin:'https://outside.test'})).status,403);
        assert.equal((await request({}, {Host:'outside.test:'+port})).status,403);
        assert.equal((await request(null)).status,400);
        const png=fs.readFileSync(new URL('../demo_clip_style_cpu.png',import.meta.url));
        const payload={filename:'same.jpg',imageBase64:'data:image/png;base64,'+png.toString('base64')};
        const first=await request(payload),second=await request(payload);
        assert.equal(first.status,200);assert.equal(second.status,200);assert.notEqual(first.body.path,second.body.path);
        assert.match(first.body.filename,/\.png$/);assert.deepEqual(fs.readFileSync(first.body.path),png);
        assert.deepEqual(fs.readFileSync(second.body.path),png);
    } finally {
        await new Promise(resolve=>server.close(resolve));fs.rmSync(folder,{recursive:true,force:true});
        if(old===undefined)delete process.env.PAINT_OUTPUT_DIR;else process.env.PAINT_OUTPUT_DIR=old;
    }
});
test('Balde termina quando a nova cor fica dentro da tolerância', () => {
    const scope={Uint8ClampedArray,Uint8Array,Int32Array,document:{createElement:()=>({style:{}}),body:{appendChild(){},removeChild(){}}},window:{getComputedStyle:()=>({color:'rgb(12, 10, 10)'})}};
    vm.runInNewContext(fs.readFileSync(new URL('../filters.js',import.meta.url),'utf8')+'\nglobalThis.Generators=PaintGenerators',scope);
    const pixels=new Uint8ClampedArray(4*4*4);for(let i=0;i<pixels.length;i+=4)pixels.set([10,10,10,255],i);
    scope.Generators.floodFill({getImageData:()=>({data:pixels}),putImageData(){}},0,0,'#0c0a0a',4,4);
    assert.ok(Array.from(pixels).every((value,index)=>value===[12,10,10,255][index%4]));
});

test('Misuki natural gera PNG leve e rejeita qualidade inválida', async () => {
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const port=server.address().port;
    const request=quality=>new Promise((resolve,reject)=>{
        const req=http.request({host:'127.0.0.1',port,path:'/api/generate/ink-portrait?style=misuki-natural&quality='+quality,method:'POST'},res=>{
            const chunks=[];res.on('data',chunk=>chunks.push(chunk));
            res.on('end',()=>resolve({status:res.statusCode,body:Buffer.concat(chunks)}));
        });req.on('error',reject);req.end();
    });
    try {
        assert.equal((await request('invalid')).status,400);
        assert.equal((await request('economy&expression=invalid')).status,400);
        assert.equal((await request('economy&material=invalid')).status,400);
        const result=await request('economy&expression=happy&material=satin');
        assert.equal(result.status,200);
        assert.equal(result.body.subarray(1,4).toString(),'PNG');
        assert.equal(result.body.readUInt32BE(16),720);
        assert.equal(result.body.readUInt32BE(20),960);
    } finally { await new Promise(resolve=>server.close(resolve)); }
});
