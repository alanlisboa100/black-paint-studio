/** Editable projects and local crash recovery. No network or keys. */
(function(root) {
    const blends = new Set(['source-over','multiply','screen','overlay','darken','lighten','color-dodge','color-burn','hard-light','soft-light','difference','exclusion','hue','saturation','color','luminosity']);
    function validate(project) {
        const s = project?.snapshot;
        if (project?.format !== 'black-paint-project' || project.version !== 1 || !s ||
            !Number.isInteger(s.logicalWidth) || !Number.isInteger(s.logicalHeight) ||
            s.logicalWidth < 1 || s.logicalHeight < 1 || Math.max(s.logicalWidth,s.logicalHeight) > 1440 ||
            !Number.isFinite(s.pixelRatio) || s.pixelRatio < .1 || s.pixelRatio > 2 ||
            s.width !== Math.round(s.logicalWidth*s.pixelRatio) || s.height !== Math.round(s.logicalHeight*s.pixelRatio) ||
            !Array.isArray(s.layers) || s.layers.length < 1 || s.layers.length > 12 ||
            !Number.isInteger(s.activeLayerIndex) || s.activeLayerIndex < 0 || s.activeLayerIndex >= s.layers.length) throw new Error('Projeto inválido ou dimensões acima do limite.');
        let bytes = 0;
        const ids = new Set();
        for (const l of s.layers) {
            if (!Number.isSafeInteger(l.id) || l.id < 1 || ids.has(l.id) || typeof l.name !== 'string' || l.name.length > 200 ||
                typeof l.dataUrl !== 'string' || !/^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(l.dataUrl) ||
                !Number.isFinite(l.opacity) || l.opacity < 0 || l.opacity > 1 || !blends.has(l.blendMode) ||
                !['visible','clipping','alphaLock'].every(key => typeof l[key] === 'boolean')) throw new Error('Camada inválida no projeto.');
            ids.add(l.id); bytes += l.dataUrl.length;
        }
        if (bytes > 32*1024*1024) throw new Error('Projeto excede 32 MB.');
        return s;
    }
    let database;
    function db() {
        if (!database) database = new Promise((resolve,reject) => {
            const request = indexedDB.open('black-paint-studio',1);
            request.onupgradeneeded = () => request.result.createObjectStore('recovery');
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
        return database;
    }
    async function store(snapshot) {
        const database = await db();
        return new Promise((resolve,reject) => {
            const tx = database.transaction('recovery','readwrite');
            tx.objectStore('recovery').put(snapshot,'last');
            tx.oncomplete = resolve; tx.onerror = () => reject(tx.error); tx.onabort = () => reject(tx.error);
        });
    }
    async function read() {
        const database = await db();
        return new Promise((resolve,reject) => {
            const request = database.transaction('recovery').objectStore('recovery').get('last');
            request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error);
        });
    }
    root.PaintProject = {validate,store,read};
})(typeof window === 'undefined' ? globalThis : window);
