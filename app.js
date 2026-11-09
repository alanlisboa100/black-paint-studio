/**
 * App.js - Controlador Principal do Black Paint Studio (Ibis Paint X Edition)
 */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('paint-canvas');
    const overlay = document.getElementById('overlay-canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const overlayCtx = overlay.getContext('2d');
    const container = document.querySelector('.canvas-container');

    // Estado do App
    const state = {
        currentTool: 'brush',
        currentColor: '#00ffcc',
        brushSize: 8,
        brushMaterial: 'gpen',
        brushOpacity: 1,
        glowSize: 15,
        stabilizer: 0,
        symmetryCount: 8,
        taperSize: 0.5,
        rulerType: 'none',
        isDrawing: false,
        startX: 0,
        startY: 0,
        lastX: 0,
        lastY: 0,
        history: [],
        historyIndex: -1,
        maxHistory: 12,
        maxHistoryBytes: 24 * 1024 * 1024,
        restoring: false,
        restoreToken: 0,
        referenceDataUrl: '',
        visionConfigured: false,
        viewZoom: 1,
        viewX: 0,
        viewY: 0,
        showRef: false,
        pointers: new Map()
    };

    // Sistema de Camadas Reais estilo Ibis Paint X
    class Layer {
        constructor(id, name, width, height, background = 'transparent') {
            this.id = id;
            this.name = name;
            this.canvas = document.createElement('canvas');
            this.canvas.width = width;
            this.canvas.height = height;
            this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
            this.visible = true;
            this.opacity = 1;
            this.blendMode = 'source-over';
            this.clipping = false;
            this.alphaLock = false;
            if (background !== 'transparent') {
                this.ctx.fillStyle = background;
                this.ctx.fillRect(0, 0, width, height);
            }
        }
    }

    class LayerManager {
        constructor() {
            this.layers = [];
            this.activeLayerIndex = 0;
            this.nextId = 1;
        }

        init(width, height, background = '#000000') {
            this.layers = [];
            this.nextId = 1;
            const baseLayer = new Layer(this.nextId++, 'Camada de Fundo 1', width, height, background);
            this.layers.push(baseLayer);
            this.activeLayerIndex = 0;
            this.updateUI();
        }

        getActiveLayer() {
            return this.layers[this.activeLayerIndex] || this.layers[0];
        }

        addLayer() {
            if (this.layers.length >= 12) return alert("Limite de 12 camadas para preservar a memória do celular.");
            const width = this.layers[0]?.canvas.width || 1024;
            const height = this.layers[0]?.canvas.height || 1024;
            const newLayer = new Layer(this.nextId++, `Camada ${this.layers.length + 1}`, width, height, 'transparent');
            this.layers.splice(this.activeLayerIndex + 1, 0, newLayer);
            this.activeLayerIndex++;
            this.updateUI();
            saveState();
        }

        duplicateActiveLayer() {
            if (this.layers.length >= 12) return alert("Limite de 12 camadas para preservar a memória do celular.");
            const active = this.getActiveLayer();
            const width = active.canvas.width;
            const height = active.canvas.height;
            const dup = new Layer(this.nextId++, `${active.name} (Cópia)`, width, height, 'transparent');
            dup.ctx.drawImage(active.canvas, 0, 0);
            dup.opacity = active.opacity;
            dup.blendMode = active.blendMode;
            dup.clipping = active.clipping;
            dup.alphaLock = active.alphaLock;
            this.layers.splice(this.activeLayerIndex + 1, 0, dup);
            this.activeLayerIndex++;
            this.updateUI();
            saveState();
        }

        deleteActiveLayer() {
            if (this.layers.length <= 1) {
                alert('O estúdio precisa manter pelo menos uma camada.');
                return;
            }
            this.layers.splice(this.activeLayerIndex, 1);
            this.activeLayerIndex = Math.max(0, this.activeLayerIndex - 1);
            this.updateUI();
            renderLayersToMainCanvas();
            saveState();
        }

        moveLayerUp() {
            if (this.activeLayerIndex >= this.layers.length - 1) return;
            const temp = this.layers[this.activeLayerIndex];
            this.layers[this.activeLayerIndex] = this.layers[this.activeLayerIndex + 1];
            this.layers[this.activeLayerIndex + 1] = temp;
            this.activeLayerIndex++;
            this.updateUI();
            renderLayersToMainCanvas();
            saveState();
        }

        moveLayerDown() {
            if (this.activeLayerIndex <= 0) return;
            const temp = this.layers[this.activeLayerIndex];
            this.layers[this.activeLayerIndex] = this.layers[this.activeLayerIndex - 1];
            this.layers[this.activeLayerIndex - 1] = temp;
            this.activeLayerIndex--;
            this.updateUI();
            renderLayersToMainCanvas();
            saveState();
        }

        resizeLayers(width, height) {
            for (const layer of this.layers) {
                const temp = document.createElement('canvas');
                temp.width = layer.canvas.width;
                temp.height = layer.canvas.height;
                temp.getContext('2d').drawImage(layer.canvas, 0, 0);
                layer.canvas.width = width;
                layer.canvas.height = height;
                layer.ctx = layer.canvas.getContext('2d', { willReadFrequently: true });
                layer.ctx.drawImage(temp, 0, 0, width, height);
            }
        }

        updateUI() {
            const select = document.getElementById('layer-select');
            if (!select) return;
            select.innerHTML = '';
            this.layers.forEach((layer, idx) => {
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = `${layer.name} ${idx === this.activeLayerIndex ? ' (Ativa)' : ''} ${layer.visible ? '' : ' [Oculta]'}`;
                if (idx === this.activeLayerIndex) opt.selected = true;
                select.appendChild(opt);
            });
            const active = this.getActiveLayer();
            const blendSelect = document.getElementById('layer-blend');
            if (blendSelect) blendSelect.value = active.blendMode;
            const opacitySlider = document.getElementById('layer-opacity');
            if (opacitySlider) {
                opacitySlider.value = Math.round(active.opacity * 100);
                document.getElementById('layer-opacity-val').textContent = `${Math.round(active.opacity * 100)}%`;
            }
            const btnClip = document.getElementById('btn-layer-clipping');
            if (btnClip) btnClip.textContent = `✂ Clipping Mask (${active.clipping ? 'ON' : 'OFF'})`;
            const btnLock = document.getElementById('btn-layer-alpha-lock');
            if (btnLock) btnLock.textContent = `🔒 Alpha Lock (${active.alphaLock ? 'ON' : 'OFF'})`;
            const btnVis = document.getElementById('btn-layer-toggle-vis');
            if (btnVis) btnVis.textContent = `👁️ Visível (${active.visible ? 'ON' : 'OFF'})`;
        }
    }

    const layerManager = new LayerManager();
    const brushEngine = new BrushEngine(ctx, overlayCtx);

    // Compositing de Camadas no Canvas Principal
    function renderLayersToMainCanvas() {
        const logicalW = state.logicalWidth;
        const logicalH = state.logicalHeight;
        if (!logicalW || !logicalH) return;

        ctx.save();
        ctx.setTransform(state.pixelRatio, 0, 0, state.pixelRatio, 0, 0);
        ctx.clearRect(0, 0, logicalW, logicalH);


        for (let i = 0; i < layerManager.layers.length; i++) {
            const layer = layerManager.layers[i];
            if (!layer.visible || layer.opacity <= 0) continue;

            ctx.save();
            ctx.globalAlpha = layer.opacity;
            ctx.globalCompositeOperation = layer.blendMode || 'source-over';

            if (layer.clipping && i > 0) {
                // Clipping Mask: Usa os pixels da camada anterior como máscara
                const baseCanvas = layerManager.layers[i - 1].canvas;
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = logicalW;
                tempCanvas.height = logicalH;
                const tempCtx = tempCanvas.getContext('2d');
                
                tempCtx.drawImage(layer.canvas, 0, 0, logicalW, logicalH);
                tempCtx.globalCompositeOperation = 'destination-in';
                tempCtx.drawImage(baseCanvas, 0, 0, logicalW, logicalH);

                ctx.drawImage(tempCanvas, 0, 0, logicalW, logicalH);
            } else {
                ctx.drawImage(layer.canvas, 0, 0, logicalW, logicalH);
            }
            ctx.restore();
        }
        ctx.restore();
    }

    // Inicialização do Canvas com resolução nítida
    function setDocumentSize(width, height, background = '#000000') {
        if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) throw new Error("Dimensões inválidas.");
        const scale = Math.min(1, 1440 / Math.max(width, height));
        const logicalWidth = Math.max(1, Math.round(width * scale));
        const logicalHeight = Math.max(1, Math.round(height * scale));
        const dpr = Math.min(window.devicePixelRatio || 1, 2, 1600 / Math.max(logicalWidth, logicalHeight));
        
        canvas.width = Math.round(logicalWidth * dpr); canvas.height = Math.round(logicalHeight * dpr);
        overlay.width = canvas.width; overlay.height = canvas.height;
        state.logicalWidth = logicalWidth; state.logicalHeight = logicalHeight; state.pixelRatio = dpr;

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0); 
        overlayCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

        layerManager.init(logicalWidth, logicalHeight, background);
        renderLayersToMainCanvas();
        document.getElementById('res-display').textContent = `${Math.round(canvas.width)} x ${Math.round(canvas.height)}`;
        fitCanvasDisplay();
    }

    function initCanvas() {
        const containerRect = container.getBoundingClientRect();
        const size = Math.max(128, Math.floor(Math.min(containerRect.width - 16, containerRect.height - 16, 900)));
        setDocumentSize(size, size);
        saveState();
    }

    // Gerenciamento de Histórico (Undo / Redo) com Camadas
    function saveState() {
        if (state.restoring) return;
        if (state.historyIndex < state.history.length - 1) {
            state.history = state.history.slice(0, state.historyIndex + 1);
        }
        const previousLayers = state.history[state.historyIndex]?.layers || [];
        const snapshotLayers = layerManager.layers.map(layer => {
            const encoded = layer.canvas.toDataURL('image/png');
            const previous = previousLayers.find(item => item.id === layer.id);
            const dataUrl = previous?.dataUrl === encoded ? previous.dataUrl : encoded;
            return {
                id: layer.id,
                name: layer.name,
                dataUrl,
                visible: layer.visible,
                opacity: layer.opacity,
                blendMode: layer.blendMode,
                clipping: layer.clipping,
                alphaLock: layer.alphaLock
            };
        });

        state.history.push({
            layers: snapshotLayers,
            activeLayerIndex: layerManager.activeLayerIndex,
            width: canvas.width,
            height: canvas.height,
            logicalWidth: state.logicalWidth,
            logicalHeight: state.logicalHeight,
            pixelRatio: state.pixelRatio
        });

        const historyBytes = () => {
            const unique = new Set(state.history.flatMap(item => item.layers.map(layer => layer.dataUrl)));
            return [...unique].reduce((sum, value) => sum + value.length * 2, 0);
        };
        while (state.history.length > 2 && (state.history.length > state.maxHistory || historyBytes() > state.maxHistoryBytes)) state.history.shift();
        state.historyIndex = state.history.length - 1;
        if (state.history.length > 1) scheduleRecovery();
    }

    async function restoreState(snapshot) {
        const token = ++state.restoreToken;
        state.restoring = true;
        state.isDrawing = false;
        brushEngine.endStroke();
        try {
            const layers = await Promise.all(snapshot.layers.map(async snap => {
                const image = new Image();
                await new Promise((resolve, reject) => {
                    image.onload = resolve;
                    image.onerror = () => reject(new Error('Camada inválida.'));
                    image.src = snap.dataUrl;
                });
                const layer = new Layer(snap.id, snap.name, snapshot.logicalWidth, snapshot.logicalHeight, 'transparent');
                for (const key of ['visible','opacity','blendMode','clipping','alphaLock']) layer[key] = snap[key];
                layer.ctx.drawImage(image, 0, 0, snapshot.logicalWidth, snapshot.logicalHeight);
                return layer;
            }));
            if (token !== state.restoreToken) return;
            canvas.width = snapshot.width; canvas.height = snapshot.height;
            overlay.width = snapshot.width; overlay.height = snapshot.height;
            state.logicalWidth = snapshot.logicalWidth; state.logicalHeight = snapshot.logicalHeight; state.pixelRatio = snapshot.pixelRatio;
            ctx.setTransform(state.pixelRatio, 0, 0, state.pixelRatio, 0, 0);
            overlayCtx.setTransform(state.pixelRatio, 0, 0, state.pixelRatio, 0, 0);
            layerManager.layers = layers;
            layerManager.nextId = Math.max(...layers.map(layer => layer.id)) + 1;
            layerManager.activeLayerIndex = Math.min(snapshot.activeLayerIndex, layers.length - 1);
            layerManager.updateUI();
            renderLayersToMainCanvas();
            document.getElementById('res-display').textContent = `${canvas.width} x ${canvas.height}`;
            fitCanvasDisplay();
            scheduleRecovery(snapshot);
        } catch (error) { alert(error.message); }
        finally { if (token === state.restoreToken) state.restoring = false; }
    }

    function undo() {
        if (state.historyIndex > 0) {
            state.historyIndex--;
            restoreState(state.history[state.historyIndex]);
        }
    }

    function redo() {
        if (state.historyIndex < state.history.length - 1) {
            state.historyIndex++;
            restoreState(state.history[state.historyIndex]);
        }
    }

    function fitCanvasDisplay() {
        if (!state.logicalWidth || !state.logicalHeight) return;
        const bounds = container.getBoundingClientRect();
        const scale = Math.min((bounds.width - 32) / state.logicalWidth, (bounds.height - 32) / state.logicalHeight);
        if (!Number.isFinite(scale) || scale <= 0) return;
        const width = Math.max(1, Math.floor(state.logicalWidth * scale));
        const height = Math.max(1, Math.floor(state.logicalHeight * scale));
        canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
        overlay.style.width = `${width}px`; overlay.style.height = `${height}px`;
        document.getElementById('canvas-wrapper').style.width = `${width}px`;
        document.getElementById('canvas-wrapper').style.height = `${height}px`;
    }

    function applyView() {
        const wrap = document.getElementById('canvas-wrapper');
        wrap.style.transform = `translate(${state.viewX}px, ${state.viewY}px) scale(${state.viewZoom})`;
        const readout = document.getElementById('zoom-readout');
        if (readout) readout.textContent = `${Math.round(state.viewZoom * 100)}%`;
    }
    function setZoom(next) {
        state.viewZoom = Math.min(6, Math.max(0.35, next));
        applyView();
    }
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => setZoom(state.viewZoom * 1.25));
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => setZoom(state.viewZoom / 1.25));
    document.getElementById('btn-zoom-reset')?.addEventListener('click', () => {
        state.viewZoom = 1; state.viewX = 0; state.viewY = 0; applyView();
    });
    container.addEventListener('wheel', (event) => {
        event.preventDefault();
        setZoom(state.viewZoom * (event.deltaY < 0 ? 1.08 : 1 / 1.08));
    }, { passive: false });

    // Pinch-to-zoom com dois dedos (celular)
    container.addEventListener('pointerdown', (event) => {
        state.pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
        if (state.pointers.size === 2 && state.isDrawing) {
            state.isDrawing = false; brushEngine.endStroke();
            overlayCtx.clearRect(0,0,state.logicalWidth,state.logicalHeight);
            renderLayersToMainCanvas(); saveState();
        }
    }, true);
    container.addEventListener('pointerup', (event) => { state.pointers.delete(event.pointerId); state.pinchStart = null; });
    container.addEventListener('pointercancel', (event) => { state.pointers.delete(event.pointerId); state.pinchStart = null; });
    container.addEventListener('pointermove', (event) => {
        if (!state.pointers.has(event.pointerId)) return;
        state.pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
        if (state.pointers.size !== 2) return;
        const pts = [...state.pointers.values()];
        const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
        const midX = (pts[0].x + pts[1].x) / 2;
        const midY = (pts[0].y + pts[1].y) / 2;
        if (!state.pinchStart) {
            state.pinchStart = { dist, zoom: state.viewZoom, x: state.viewX, y: state.viewY, midX, midY };
            if (state.isDrawing) { state.isDrawing = false; brushEngine.endStroke(); saveState(); }
            overlayCtx.clearRect(0, 0, state.logicalWidth, state.logicalHeight);
            return;
        }
        const scale = dist / Math.max(1, state.pinchStart.dist);
        setZoom(state.pinchStart.zoom * scale);
        state.viewX = state.pinchStart.x + (midX - state.pinchStart.midX);
        state.viewY = state.pinchStart.y + (midY - state.pinchStart.midY);
        applyView();
    });

    document.addEventListener('click', event => {
        if (state.restoring && !['btn-undo', 'btn-redo'].includes(event.target.closest('button')?.id)) {
            event.preventDefault(); event.stopImmediatePropagation();
        }
    }, true);

    // Coordenadas com suporte a Réguas Ibis
    function applyRuler(x, y) {
        if (state.rulerType === 'straight') {
            // Projeta para a reta a partir do ponto inicial
            const dx = x - state.startX;
            const dy = y - state.startY;
            if (Math.abs(dx) > Math.abs(dy)) {
                return { x, y: state.startY };
            } else {
                return { x: state.startX, y };
            }
        } else if (state.rulerType === 'circular') {
            const cx = state.logicalWidth / 2;
            const cy = state.logicalHeight / 2;
            const r = Math.hypot(state.startX - cx, state.startY - cy);
            const angle = Math.atan2(y - cy, x - cx);
            return {
                x: cx + Math.cos(angle) * r,
                y: cy + Math.sin(angle) * r
            };
        }
        return { x, y };
    }

    function getCanvasCoords(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.clientX;
        const clientY = e.clientY;
        const x = (clientX - rect.left) * (state.logicalWidth / rect.width);
        const y = (clientY - rect.top) * (state.logicalHeight / rect.height);
        return applyRuler(x, y);
    }

    // Eventos de Desenho (Pointer Events)
    function handlePointerDown(e) {
        e.preventDefault();
        if (state.restoring) return;
        if (state.pointers.size > 1 || state.pinchStart) return;
        canvas.setPointerCapture?.(e.pointerId);
        state.drawingPointerId = e.pointerId;
        state.isDrawing = true;
        const { x, y } = getCanvasCoords(e);
        state.startX = x;
        state.startY = y;
        state.lastX = x;
        state.lastY = y;
        state.lastPressure = e.pressure > 0 ? e.pressure : 1;
        state.filteredX = x;
        state.filteredY = y;

        const activeLayer = layerManager.getActiveLayer();
        const layerCtx = activeLayer.ctx;

        if (state.currentTool === 'brush') brushEngine.beginStroke(state.brushMaterial, state.brushSize);

        if (state.currentTool === 'fill') {
            PaintGenerators.floodFill(layerCtx, x, y, state.currentColor, state.logicalWidth, state.logicalHeight);
            state.isDrawing = false;
            renderLayersToMainCanvas();
            saveState();
            return;
        }

        if (state.currentTool === 'eyedropper') {
            const dpr = state.pixelRatio;
            try {
                const pixel = ctx.getImageData(Math.max(0, Math.floor(x * dpr)), Math.max(0, Math.floor(y * dpr)), 1, 1).data;
                const hex = `#${[pixel[0], pixel[1], pixel[2]].map(value => value.toString(16).padStart(2, '0')).join('')}`;
                state.currentColor = hex;
                document.getElementById('color-picker').value = hex;
                document.querySelectorAll('.color-swatch').forEach(swatch => swatch.classList.toggle('active', swatch.dataset.color === hex));
            } catch {}
            state.isDrawing = false;
            return;
        }

        if (['brush', 'neon', 'eraser', 'symmetry'].includes(state.currentTool)) {
            drawStep(x, y, x, y, e.pressure > 0 ? e.pressure : 1);
        } else if (state.currentTool === 'matrix') {
            withActiveBrush(() => brushEngine.drawMatrix(x, y, state.currentColor, state.brushSize));
        } else if (state.currentTool === 'particles') {
            withActiveBrush(() => brushEngine.drawParticles(x, y, state.currentColor, state.brushSize));
        } else if (state.currentTool === 'spray') {
            withActiveBrush(() => brushEngine.drawSpray(x, y, state.currentColor, state.brushSize));
        }
        renderLayersToMainCanvas();
    }

    function handlePointerMove(e) {
        if (state.restoring || (state.isDrawing && e.pointerId !== state.drawingPointerId)) return;
        const coalesced = e.getCoalescedEvents?.();
        const samples = coalesced?.length ? coalesced : [e];
        for (const sample of samples) {
            const { x, y } = getCanvasCoords(sample);
            document.getElementById('coords-display').textContent = `X: ${Math.round(x)}, Y: ${Math.round(y)}`;
            if (!state.isDrawing) continue;
            e.preventDefault();

            if (['brush', 'neon', 'eraser', 'symmetry'].includes(state.currentTool)) {
                const alpha = 1 / (1 + state.stabilizer * 0.2);
                state.filteredX += (x - state.filteredX) * alpha;
                state.filteredY += (y - state.filteredY) * alpha;
                drawStep(state.lastX, state.lastY, state.filteredX, state.filteredY, sample.pressure > 0 ? sample.pressure : state.lastPressure);
                state.lastX = state.filteredX;
                state.lastY = state.filteredY;
                state.lastPressure = sample.pressure > 0 ? sample.pressure : state.lastPressure;
            } else if (state.currentTool === 'matrix') {
                withActiveBrush(() => brushEngine.drawMatrix(x, y, state.currentColor, state.brushSize));
            } else if (state.currentTool === 'particles') {
                withActiveBrush(() => brushEngine.drawParticles(x, y, state.currentColor, state.brushSize));
            } else if (state.currentTool === 'spray') {
                withActiveBrush(() => brushEngine.drawSpray(x, y, state.currentColor, state.brushSize));
            } else if (['line', 'rect', 'circle', 'star'].includes(state.currentTool)) {
                overlayCtx.clearRect(0, 0, state.logicalWidth, state.logicalHeight);
                brushEngine.drawShape(overlayCtx, state.currentTool,
                    state.startX, state.startY, x, y, state.currentColor, state.brushSize, state.glowSize);
            }
        }
        if (state.isDrawing) renderLayersToMainCanvas();
    }

    function handlePointerUp(e) {
        if (!state.isDrawing || e.pointerId !== state.drawingPointerId) return;
        state.isDrawing = false;
        overlayCtx.clearRect(0, 0, state.logicalWidth, state.logicalHeight);

        const cancelled = e.type === 'pointercancel' || e.type === 'lostpointercapture';
        const { x, y } = cancelled ? {x:state.lastX,y:state.lastY} : getCanvasCoords(e);
        const activeLayer = layerManager.getActiveLayer();

        if (['brush', 'neon', 'eraser', 'symmetry'].includes(state.currentTool)) {
            const alpha = 1 / (1 + state.stabilizer * 0.28);
            state.filteredX += (x - state.filteredX) * alpha;
            state.filteredY += (y - state.filteredY) * alpha;
            drawStep(state.lastX, state.lastY, state.filteredX, state.filteredY, e.pressure > 0 ? e.pressure : state.lastPressure);
        }
        brushEngine.endStroke();

        if (!cancelled && ['line', 'rect', 'circle', 'star'].includes(state.currentTool)) {
            brushEngine.drawShape(
                activeLayer.ctx, state.currentTool,
                state.startX, state.startY, x, y,
                state.currentColor, state.brushSize, state.glowSize
            );
        }

        renderLayersToMainCanvas();
        saveState();
    }

    function withActiveBrush(draw) {
        const previous = brushEngine.ctx;
        brushEngine.ctx = layerManager.getActiveLayer().ctx;
        try { draw(); } finally { brushEngine.ctx = previous; }
    }

    function drawStep(x0, y0, x1, y1, pressure = 1) {
        const activeLayer = layerManager.getActiveLayer();
        const layerCtx = activeLayer.ctx;

        // Temporariamente direciona o BrushEngine para o contexto da camada ativa
        const oldCtx = brushEngine.ctx;
        brushEngine.ctx = layerCtx;

        if (activeLayer.alphaLock) {
            layerCtx.save();
            layerCtx.globalCompositeOperation = 'source-atop';
        }

        if (activeLayer.alphaLock && state.currentTool === 'eraser') {
            layerCtx.restore(); brushEngine.ctx = oldCtx; return;
        }
        if (state.currentTool === 'brush') {
            brushEngine.drawMaterial(x0, y0, x1, y1, state.currentColor, state.brushSize,
                state.brushMaterial, state.brushOpacity, pressure * (1 - state.taperSize * 0.3));
        } else if (state.currentTool === 'neon') {
            brushEngine.drawNeon(x0, y0, x1, y1, state.currentColor, state.brushSize, state.glowSize);
        } else if (state.currentTool === 'eraser') {
            brushEngine.drawEraser(x0, y0, x1, y1, state.brushSize);
        } else if (state.currentTool === 'symmetry') {
            const cx = state.logicalWidth / 2;
            const cy = state.logicalHeight / 2;
            brushEngine.drawSymmetry(x0, y0, x1, y1, cx, cy, state.currentColor, state.brushSize, state.glowSize, state.symmetryCount);
        }

        if (activeLayer.alphaLock) {
            layerCtx.restore();
        }

        brushEngine.ctx = oldCtx;
    }

    // Listeners do Canvas
    canvas.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);
    canvas.addEventListener('lostpointercapture', handlePointerUp);
    window.addEventListener('pointercancel', handlePointerUp);

    // Controles de Camadas na UI
    document.getElementById('layer-select')?.addEventListener('change', (e) => {
        layerManager.activeLayerIndex = Number(e.target.value);
        layerManager.updateUI();
    });
    document.getElementById('btn-layer-add')?.addEventListener('click', () => layerManager.addLayer());
    document.getElementById('btn-layer-duplicate')?.addEventListener('click', () => layerManager.duplicateActiveLayer());
    document.getElementById('btn-layer-delete')?.addEventListener('click', () => layerManager.deleteActiveLayer());
    document.getElementById('btn-layer-up')?.addEventListener('click', () => layerManager.moveLayerUp());
    document.getElementById('btn-layer-down')?.addEventListener('click', () => layerManager.moveLayerDown());
    document.getElementById('layer-blend')?.addEventListener('change', (e) => {
        const active = layerManager.getActiveLayer();
        active.blendMode = e.target.value;
        renderLayersToMainCanvas();
        saveState();
    });
    document.getElementById('layer-opacity')?.addEventListener('input', (e) => {
        const active = layerManager.getActiveLayer();
        active.opacity = Number(e.target.value) / 100;
        document.getElementById('layer-opacity-val').textContent = `${e.target.value}%`;
        renderLayersToMainCanvas();
    });
    document.getElementById('btn-layer-clipping')?.addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        active.clipping = !active.clipping;
        layerManager.updateUI();
        renderLayersToMainCanvas();
        saveState();
    });
    document.getElementById('btn-layer-alpha-lock')?.addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        active.alphaLock = !active.alphaLock;
        layerManager.updateUI();
        saveState();
    });
    document.getElementById('btn-layer-toggle-vis')?.addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        active.visible = !active.visible;
        layerManager.updateUI();
        renderLayersToMainCanvas();
        saveState();
    });

    document.getElementById('ruler-type')?.addEventListener('change', (e) => {
        state.rulerType = e.target.value;
    });

    document.getElementById('taper-size')?.addEventListener('input', (e) => {
        state.taperSize = Number(e.target.value) / 100;
        document.getElementById('taper-val').textContent = `${e.target.value}%`;
    });

    // Seleção de Ferramentas
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.currentTool = btn.dataset.tool;
            document.getElementById('active-tool-display').textContent = `FERRAMENTA: ${btn.textContent.trim()}`;
        });
    });

    // Controles de Slider
    const sizeInput = document.getElementById('brush-size');
    const glowInput = document.getElementById('glow-size');
    const stabilizerInput = document.getElementById('stabilizer');
    stabilizerInput.addEventListener('input', (e) => {
        state.stabilizer = Number(e.target.value);
        document.getElementById('stabilizer-val').textContent = String(state.stabilizer);
    });
    document.getElementById('symmetry-count').addEventListener('change', (e) => {
        state.symmetryCount = Number(e.target.value);
    });
    sizeInput.addEventListener('input', (e) => {
        state.brushSize = parseInt(e.target.value);
        document.getElementById('size-val').textContent = `${state.brushSize}px`;
    });
    glowInput.addEventListener('input', (e) => {
        state.glowSize = parseInt(e.target.value);
        document.getElementById('glow-val').textContent = state.glowSize;
    });
    document.getElementById('brush-material').addEventListener('change', (e) => {
        state.brushMaterial = e.target.value;
    });
    document.getElementById('brush-opacity').addEventListener('input', (e) => {
        state.brushOpacity = Number(e.target.value) / 100;
        document.getElementById('opacity-val').textContent = `${e.target.value}%`;
    });

    // Presets
    document.getElementById('preset-selector').addEventListener('change', (e) => {
        const presets = {
            A: { color:'#dbeafe', size:3, glow:0 }, B: { color:'#ff007f', size:6, glow:8 },
            C: { color:'#ffb4c8', size:10, glow:2 }, D: { color:'#d8a2ff', size:7, glow:12 },
            E: { color:'#00f0ff', size:4, glow:5 }, F: { color:'#00ffcc', size:12, glow:0 }
        };
        const preset = presets[e.target.value];
        if (!preset) return;
        state.currentColor = preset.color; state.brushSize = preset.size; state.glowSize = preset.glow;
        colorPicker.value = preset.color; sizeInput.value = preset.size; glowInput.value = preset.glow;
        document.getElementById('size-val').textContent = `${preset.size}px`;
        document.getElementById('glow-val').textContent = String(preset.glow);
        document.querySelectorAll('.color-swatch').forEach(s => s.classList.toggle('active', s.dataset.color === preset.color));
    });

    // Paleta de Cores
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            state.currentColor = swatch.dataset.color;
            document.getElementById('color-picker').value = state.currentColor;
        });
    });

    const colorPicker = document.getElementById('color-picker');
    colorPicker.addEventListener('input', (e) => {
        state.currentColor = e.target.value;
        document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
    });

    // Referência fantasma (ghost) para cópia/estudo por cima
    const refGhost = document.getElementById('ref-ghost');
    document.getElementById('btn-toggle-ref')?.addEventListener('click', () => {
        state.showRef = !state.showRef;
        if (refGhost) {
            refGhost.hidden = !state.showRef || !state.referenceDataUrl;
            if (state.referenceDataUrl) refGhost.src = state.referenceDataUrl;
        }
    });

    // Ações (Abrir, Salvar, Geradores, Vision)
    const openImageInput = document.getElementById('open-image-input');
    document.getElementById('btn-open-image').addEventListener('click', () => openImageInput.click());
    openImageInput.addEventListener('change', () => {
        const file = openImageInput.files?.[0];
        if (!file) return;
        if (file.size > 25 * 1024 * 1024) { alert("Imagem excede 25 MB."); openImageInput.value = ""; return; }
        const reader = new FileReader();
        reader.onload = () => {
            const image = new Image();
            image.onload = () => {
                setDocumentSize(image.width, image.height, 'transparent');
                const active = layerManager.getActiveLayer();
                active.ctx.drawImage(image, 0, 0, state.logicalWidth, state.logicalHeight);
                const reference = document.createElement('canvas');
                reference.width = state.logicalWidth; reference.height = state.logicalHeight;
                reference.getContext('2d').drawImage(image,0,0,reference.width,reference.height);
                state.referenceDataUrl = reference.toDataURL('image/png');
                updateVisionButton();
                if (refGhost) { refGhost.src = state.referenceDataUrl; refGhost.hidden = !state.showRef; }
                renderLayersToMainCanvas();
                saveState(); openImageInput.value = '';
            };
            image.onerror = () => { alert('Não foi possível abrir a imagem.'); openImageInput.value = ''; };
            image.src = String(reader.result || '');
        };
        reader.readAsDataURL(file);
    });

    document.getElementById('btn-undo').addEventListener('click', undo);
    document.getElementById('btn-redo').addEventListener('click', redo);
    document.getElementById('btn-clear').addEventListener('click', () => {
        if (confirm('Deseja limpar todo o desenho?')) {
            setDocumentSize(state.logicalWidth, state.logicalHeight, '#000000');
            saveState();
        }
    });

    // Geradores Automáticos
    document.getElementById('btn-gen-city').addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        PaintGenerators.generateCyberCity(active.ctx, state.logicalWidth, state.logicalHeight);
        renderLayersToMainCanvas(); saveState();
    });
    document.getElementById('btn-gen-neural').addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        PaintGenerators.generateNeuralNet(active.ctx, state.logicalWidth, state.logicalHeight);
        renderLayersToMainCanvas(); saveState();
    });
    document.getElementById('btn-gen-fractal').addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        PaintGenerators.generateFractal(active.ctx, state.logicalWidth, state.logicalHeight);
        renderLayersToMainCanvas(); saveState();
    });
    document.getElementById('btn-gen-matrix').addEventListener('click', () => {
        const active = layerManager.getActiveLayer();
        PaintGenerators.generateFullMatrix(active.ctx, state.logicalWidth, state.logicalHeight);
        renderLayersToMainCanvas(); saveState();
    });

    const visionButton=document.getElementById('btn-vision-paint');
    const visionStatus=document.getElementById('vision-status');
    function updateVisionButton() {
        visionButton.disabled=!state.visionConfigured || !state.referenceDataUrl;
        if (!state.referenceDataUrl) visionStatus.textContent='Abra uma imagem de referência para habilitar.';
        else visionStatus.textContent=state.visionConfigured ? 'BlackCore encontrado. Use o modelo configurado ou informe outro.' : 'Referência pronta. Configure o executável BlackCore para analisar.';
    }
    fetch('/api/status').then(response=>response.json()).then(info=>{
        state.visionConfigured=Boolean(info.vision?.available);
        updateVisionButton();
    }).catch(()=>{visionStatus.textContent='Servidor local indisponível.';});

    function planToSvg(plan, viewBoxHeight, width, height) {
        const validColor=value=>typeof value==='string' && (/^#[0-9a-f]{6}$/i.test(value) || value==='none');
        if (!validColor(plan.background) || !Array.isArray(plan.elements)) throw new Error('Plano inválido.');
        const elements=plan.elements.map(item=>`<path d="${item.path}" fill="${item.fill}" stroke="${item.stroke}" stroke-width="${item.strokeWidth||0}" opacity="${item.opacity||0.1}"/>`).join('');
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 1000 ${viewBoxHeight}" preserveAspectRatio="none"><rect width="1000" height="${viewBoxHeight}" fill="${plan.background}"/>${elements}</svg>`;
    }

    visionButton.addEventListener('click',async()=>{
        if (!state.referenceDataUrl) return alert('Abra primeiro a referência.');
        try {
            visionButton.disabled = true;
            visionStatus.textContent = 'Analisando a referência…';
            const response=await fetch('/api/vision/paint',{method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({imageBase64:state.referenceDataUrl,width:state.logicalWidth,height:state.logicalHeight,
                    model:document.getElementById('vision-model').value,style:document.getElementById('vision-style').value,
                    direction:document.getElementById('vision-direction').value})});
            const result=await response.json();
            if(!response.ok || !result.ok) throw new Error(result.error||'Erro ao criar plano.');
            const svg=planToSvg(result,result.viewBoxHeight,state.logicalWidth,state.logicalHeight);
            const url=URL.createObjectURL(new Blob([svg],{type:'image/svg+xml'}));
            const image=new Image();
            await new Promise((r,j)=>{image.onload=r;image.onerror=j;image.src=url;});
            URL.revokeObjectURL(url);
            setDocumentSize(state.logicalWidth,state.logicalHeight,result.background);
            layerManager.getActiveLayer().ctx.drawImage(image,0,0,state.logicalWidth,state.logicalHeight);
            renderLayersToMainCanvas(); saveState();
        } catch(e){alert(e.message);}
        finally { updateVisionButton(); }
    });

    async function loadGeneratedImage(response) {
        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || 'Falha ao gerar imagem.');
        }
        const url = URL.createObjectURL(await response.blob());
        try {
            const image = new Image();
            await new Promise((resolve,reject) => { image.onload=resolve; image.onerror=()=>reject(new Error('PNG do gerador inválido.')); image.src=url; });
            setDocumentSize(image.width,image.height,'transparent');
            layerManager.getActiveLayer().ctx.drawImage(image,0,0,state.logicalWidth,state.logicalHeight);
            renderLayersToMainCanvas(); saveState();
        } finally { URL.revokeObjectURL(url); }
    }

    for (const [kind,id] of [['shrine','btn-study-shrine'],['city','btn-study-city'],['cathedral','btn-study-cathedral'],['house','btn-study-house'],['fruit','btn-study-fruit']]) {
        document.getElementById(id)?.addEventListener('click',async()=>{
            try {
                const response=await fetch(`/api/generate/study?type=${kind}`,{method:'POST'});
                await loadGeneratedImage(response);
            } catch(e){alert(e.message);}
        });
    }

    document.getElementById('btn-misuki-axes')?.addEventListener('click', () => {
        if (!window.MisukiStudio?.drawConstruction) return;
        window.MisukiStudio.drawConstruction(layerManager.getActiveLayer().ctx, state.logicalWidth, state.logicalHeight);
        renderLayersToMainCanvas(); saveState();
    });

    document.getElementById('btn-misuki-generate')?.addEventListener('click', async (e) => {
        const pose=document.getElementById('misuki-pose')?.value||'front';
        try {
            const response=await fetch(`/api/generate/misuki?pose=${encodeURIComponent(pose)}`,{method:'POST'});
            const result=await response.json();
            if (!response.ok || !result.ok) throw new Error(result.error || 'Falha ao gerar Misuki.');
            if (result.mode === 'plan') {
                const svg = planToSvg(result,result.viewBoxHeight,state.logicalWidth,state.logicalHeight);
                await loadGeneratedImage(new Response(new Blob([svg],{type:'image/svg+xml'})));
            } else if(result.imageBase64){
                const image=new Image();
                await new Promise((r,j)=>{image.onload=r;image.onerror=j;image.src=result.imageBase64;});
                setDocumentSize(image.width,image.height,'#111111');
                layerManager.getActiveLayer().ctx.drawImage(image,0,0,state.logicalWidth,state.logicalHeight);
                renderLayersToMainCanvas(); saveState();
                if (result.hint) alert(result.hint);
            } else { alert(result.hint || "Nenhuma imagem foi gerada."); }
        } catch(e){alert(e.message);}
    });

    document.getElementById('btn-gen-pro').addEventListener('click', async () => {
        const button=document.getElementById('btn-gen-pro');button.disabled=true;
        try {
            const style=document.getElementById('portrait-style').value;
            const quality=document.getElementById('portrait-quality').value;
            const expression=document.getElementById('portrait-expression').value;
            const material=document.getElementById('portrait-material').value;
            const response=await fetch(`/api/generate/ink-portrait?style=${encodeURIComponent(style)}&quality=${encodeURIComponent(quality)}&expression=${encodeURIComponent(expression)}&material=${encodeURIComponent(material)}`,{method:'POST'});
            await loadGeneratedImage(response);
        } catch(e){alert(e.message);}
        finally { button.disabled=false; }
    });

    function exportCanvas() {
        const exported = document.createElement('canvas');
        exported.width = state.logicalWidth; exported.height = state.logicalHeight;
        exported.getContext('2d').drawImage(canvas, 0, 0, exported.width, exported.height);
        return exported;
    }
    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob), link = document.createElement('a');
        link.href = url; link.download = filename; link.click();
        setTimeout(() => URL.revokeObjectURL(url), 30000);
    }
    document.getElementById('btn-save-phone').addEventListener('click', async () => {
        const button = document.getElementById('btn-save-phone'); button.disabled = true;
        const exported = exportCanvas();
        const dataUrl = exported.toDataURL('image/png');
        const filename = `black_paint_${Date.now()}.png`;
        try {
            const response = await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename,imageBase64:dataUrl}) });
            const result = await response.json();
            if (!response.ok || !result.ok) throw new Error(result.error || 'Falha ao salvar.');
            alert(`PNG salvo: ${result.path}`);
        } catch {
            exported.toBlob(blob => { if (blob) downloadBlob(blob, filename); }, 'image/png');
            alert('Download enviado ao navegador. Confira a pasta Downloads.');
        } finally { button.disabled = false; }
    });
    document.getElementById('btn-gpu-finish')?.addEventListener('click', () => {
        try {
            if (!window.PaintGPU?.applyFinish) return;
            const active = layerManager.getActiveLayer();
            const finished = window.PaintGPU.applyFinish(active.canvas, {grain:0.03,sharpen:0.24});
            active.ctx.clearRect(0, 0, state.logicalWidth, state.logicalHeight);
            active.ctx.drawImage(finished, 0, 0, state.logicalWidth, state.logicalHeight);
            renderLayersToMainCanvas(); saveState();
        } catch (error) { alert(error.message); }
    });

    let recoveryTimer;
    let recoveryRevision = 0;
    function scheduleRecovery(snapshot = state.history[state.historyIndex]) {
        if (!snapshot) return;
        clearTimeout(recoveryTimer);
        const revision = ++recoveryRevision;
        recoveryTimer = setTimeout(() => {
            if (revision === recoveryRevision) window.PaintProject.store(snapshot).catch(() => {
                document.getElementById('res-display').title = 'Recuperação automática indisponível. Salve o projeto.';
            });
        }, 900);
    }
    document.getElementById('btn-save-project').addEventListener('click', () => {
        const snapshot = state.history[state.historyIndex];
        if (snapshot) downloadBlob(new Blob([JSON.stringify({format:'black-paint-project',version:1,snapshot})], {type:'application/json'}), `black_paint_${Date.now()}.bpaint`);
    });
    const projectInput = document.getElementById('open-project-input');
    document.getElementById('btn-open-project').addEventListener('click', () => projectInput.click());
    projectInput.addEventListener('change', async () => {
        const file = projectInput.files?.[0];
        try {
            if (!file) return;
            if (file.size > 32 * 1024 * 1024) throw new Error('Projeto excede 32 MB.');
            const snapshot = window.PaintProject.validate(JSON.parse(await file.text()));
            await restoreState(snapshot); saveState();
        } catch (error) { alert(error.message); }
        finally { projectInput.value = ''; }
    });
    document.getElementById('btn-recover-project').addEventListener('click', async () => {
        try {
            const saved = await window.PaintProject.read();
            if (!saved) return alert('Nenhum projeto recuperável neste navegador.');
            const snapshot = window.PaintProject.validate({format:'black-paint-project',version:1,snapshot:saved});
            await restoreState(snapshot); saveState();
        } catch (error) { alert(error.message); }
    });

    document.getElementById('modal-close').addEventListener('click', () => {
        document.getElementById('modal').classList.add('hidden');
    });

    window.addEventListener('keydown', (e) => {
        if (e.target.closest('input,textarea,select')) return;
        if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
        else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.shiftKey && e.key === 'Z'))) { e.preventDefault(); redo(); }
    });

    window.addEventListener('blur', () => {
        if (state.isDrawing) { state.isDrawing=false; brushEngine.endStroke(); renderLayersToMainCanvas(); saveState(); }
        state.pointers.clear(); state.pinchStart=null; overlayCtx.clearRect(0,0,state.logicalWidth,state.logicalHeight);
    });
    // Inicialização
    initCanvas();
    window.addEventListener('resize', fitCanvasDisplay);
});
