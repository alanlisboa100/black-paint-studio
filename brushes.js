/**
 * Brushes.js - Motores de Pincéis Especiais para Black Paint Studio
 */

const MatrixChars = "0123456789ABCDEFｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ";

class BrushEngine {
    constructor(ctx, overlayCtx) {
        this.ctx = ctx;
        this.overlayCtx = overlayCtx;
        this.particles = [];
        this.activeStroke = null;
    }

    beginStroke(material, size) {
        const count = Math.max(5, Math.min(38, Math.ceil(size * 0.72)));
        let seed = (Date.now() ^ Math.floor(Math.random() * 0xffffffff)) >>> 0;
        const random = () => {
            seed = (seed * 1664525 + 1013904223) >>> 0;
            return seed / 0x100000000;
        };
        this.activeStroke = {
            material,
            bristles: Array.from({ length: count }, (_, i) => ({
                lane: count === 1 ? 0 : (i / (count - 1) - 0.5) * (0.9 + random() * 0.06),
                width: 0.34 + random() * 0.5,
                alpha: 0.72 + random() * 0.28,
                tint: Math.round((random() - 0.5) * 12),
                skip: material === 'oil-dry' && random() < 0.26
            }))
        };
    }

    endStroke() {
        this.activeStroke = null;
    }

    // Pincel Básico
    drawBasic(x0, y0, x1, y1, color, size) {
        this.ctx.save();
        this.ctx.strokeStyle = color;
        this.ctx.fillStyle = color;
        this.ctx.lineWidth = size;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.shadowBlur = 0;

        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.stroke();
        this.ctx.restore();
    }

    // Materiais de pintura raster. As variantes são aplicadas ao traço livre
    // do editor; cada uma conserva o alpha do canvas e não altera o documento.
    drawMaterial(x0, y0, x1, y1, color, size, material = 'round', opacity = 1, pressure = 1) {
        const ctx = this.ctx;
        const dx = x1 - x0, dy = y1 - y0;
        const distance = Math.hypot(dx, dy);
        const angle = Math.atan2(dy || 0.001, dx || 0.001);
        const nx = -Math.sin(angle), ny = Math.cos(angle);
        const p = Math.max(0.12, Math.min(1, Number(pressure) || 1));
        const width = Math.max(0.65, size * (0.24 + 0.76 * p));
        const rgba = this._rgba(color);
        const jitter = (value, amount) => Math.max(0, Math.min(255, Math.round(value + (Math.random() * 2 - 1) * amount)));
        const stroke = (x0s, y0s, x1s, y1s, w, alpha, tint = 0, cap = 'round') => {
            ctx.strokeStyle = `rgba(${jitter(rgba[0], tint)},${jitter(rgba[1], tint)},${jitter(rgba[2], tint)},${Math.max(0, Math.min(1, alpha))})`;
            ctx.lineWidth = Math.max(0.55, w); ctx.lineCap = cap; ctx.lineJoin = 'round';
            ctx.beginPath(); ctx.moveTo(x0s, y0s); ctx.lineTo(x1s, y1s); ctx.stroke();
        };
        ctx.save();
        if (ctx.globalCompositeOperation !== 'source-atop') ctx.globalCompositeOperation = 'source-over';
        switch (material) {
        case 'oil':
        case 'oil-dry':
        case 'impasto': {
            if (!this.activeStroke || this.activeStroke.material !== material) this.beginStroke(material, size);
            const bristles = this.activeStroke.bristles;
            const dry = material === 'oil-dry';
            const impasto = material === 'impasto';
            for (const bristle of bristles) {
                if (bristle.skip) continue;
                const offset = bristle.lane * width;
                const strandWidth = Math.max(.55, width / bristles.length * bristle.width * (impasto ? 1.45 : 1.85));
                const alpha = opacity * p * (dry ? .34 : impasto ? .62 : .42) * bristle.alpha;
                stroke(x0 + nx*offset, y0 + ny*offset, x1 + nx*offset, y1 + ny*offset,
                       strandWidth, alpha, bristle.tint + (impasto ? 11 : 0));
            }
            if (impasto) {
                stroke(x0, y0, x1, y1, Math.max(1, width*.12), opacity*p*.3, 19);
            }
            break;
        }
        case 'watercolor': {
            const passes = 5;
            ctx.shadowColor = color; ctx.shadowBlur = width * .18;
            for (let i = passes; i >= 1; i--) {
                const spread = width * (.12 + i * .065);
                stroke(x0 + (Math.random()-.5)*spread, y0 + (Math.random()-.5)*spread,
                    x1 + (Math.random()-.5)*spread, y1 + (Math.random()-.5)*spread,
                    width * (1 + i*.09), opacity*p*(.035 + .018*i), 3);
            }
            stroke(x0,y0,x1,y1,width*.52,opacity*p*.18,0);
            break;
        }
        case 'gouache':
        case 'acrylic':
            stroke(x0,y0,x1,y1,width,opacity*p*(material === 'gouache' ? .82 : .96), material === 'gouache' ? 5 : 2);
            if (width > 5) stroke(x0+nx*width*.13,y0+ny*width*.13,x1+nx*width*.13,y1+ny*width*.13,width*.12,opacity*p*.28,20);
            break;
        case 'pencil':
            for (let i=0;i<3;i++) {
                const off=(Math.random()-.5)*Math.min(2.2,width*.16);
                stroke(x0+nx*off,y0+ny*off,x1+nx*off,y1+ny*off,Math.max(.65,width*.19),opacity*p*.38,12,'butt');
            }
            break;
        case 'charcoal':
            for (let i=0;i<8;i++) {
                const off=(Math.random()-.5)*width*.75;
                const start=Math.random()*.22, end=.72+Math.random()*.28;
                stroke(x0+dx*start+nx*off,y0+dy*start+ny*off,x0+dx*end+nx*off,y0+dy*end+ny*off,
                       Math.max(.7,width*.13),opacity*p*(.12+Math.random()*.16),24,'butt');
            }
            break;
        case 'pastel':
            stroke(x0,y0,x1,y1,width,opacity*p*.48,18);
            for (let i=0;i<Math.min(18,Math.ceil(width));i++) {
                const along=Math.random(), off=(Math.random()-.5)*width;
                ctx.fillStyle=`rgba(${jitter(rgba[0],8)},${jitter(rgba[1],8)},${jitter(rgba[2],8)},${opacity*p*.38})`;
                ctx.beginPath(); ctx.arc(x0+dx*along+nx*off,y0+dy*along+ny*off,Math.max(.5,width*.035),0,Math.PI*2); ctx.fill();
            }
            break;
        case 'airbrush': {
            const radius=Math.max(1,width*.72);
            const gradient=ctx.createRadialGradient(x1,y1,0,x1,y1,radius);
            gradient.addColorStop(0,`rgba(${rgba[0]},${rgba[1]},${rgba[2]},${opacity*p*.20})`);
            gradient.addColorStop(1,`rgba(${rgba[0]},${rgba[1]},${rgba[2]},0)`);
            ctx.fillStyle=gradient; ctx.beginPath(); ctx.arc(x1,y1,radius,0,Math.PI*2); ctx.fill();
            break;
        }
        case 'smudge': {
            let picked=rgba;
            try {
                const ratio=ctx.getTransform?.().a || 1;
                const sx=Math.max(0,Math.round((x0-size/2)*ratio));
                const sy=Math.max(0,Math.round((y0-size/2)*ratio));
                const side=Math.max(1,Math.min(18,Math.round(size*ratio*.22)));
                const data=ctx.getImageData(sx,sy,side,side).data;
                let r=0,g=0,b=0,n=0;
                for(let i=0;i<data.length;i+=4) if(data[i+3]>16){r+=data[i];g+=data[i+1];b+=data[i+2];n++;}
                if(n) picked=[Math.round((r/n+rgba[0])/2),Math.round((g/n+rgba[1])/2),Math.round((b/n+rgba[2])/2)];
            } catch {}
            stroke(x0,y0,x1,y1,width*.86,opacity*p*.48,0);
            // Lay a translucent sampled color onto the dragged region.
            ctx.strokeStyle=`rgba(${picked[0]},${picked[1]},${picked[2]},${opacity*p*.38})`;
            ctx.lineWidth=Math.max(1,width*.62);ctx.lineCap='round';ctx.beginPath();ctx.moveTo(x0,y0);ctx.lineTo(x1,y1);ctx.stroke();
            break;
        }
        case 'marker':
            stroke(x0,y0,x1,y1,width,opacity*p*.68,0,'square');
            break;
        case 'ink':
        case 'gpen':
        case 'dip-pen-hard':
        case 'dip-pen-soft': {
            const isSoft = material === 'dip-pen-soft';
            const taperFactor = Math.max(0.2, p);
            const inkWidth = Math.max(0.6, width * taperFactor);
            ctx.shadowBlur = isSoft ? inkWidth * 0.25 : 0;
            ctx.shadowColor = color;
            stroke(x0, y0, x1, y1, inkWidth, opacity, 0, 'round');
            break;
        }
        case 'felt-tip':
            stroke(x0, y0, x1, y1, Math.max(1, width), opacity * 0.92, 0, 'square');
            break;
        case 'airbrush-trapezoid': {
            const radius = Math.max(2, width * 0.9);
            const gradient = ctx.createRadialGradient(x1, y1, 0, x1, y1, radius);
            gradient.addColorStop(0, `rgba(${rgba[0]},${rgba[1]},${rgba[2]},${opacity * p * 0.35})`);
            gradient.addColorStop(0.5, `rgba(${rgba[0]},${rgba[1]},${rgba[2]},${opacity * p * 0.15})`);
            gradient.addColorStop(1, `rgba(${rgba[0]},${rgba[1]},${rgba[2]},0)`);
            ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(x1, y1, radius, 0, Math.PI * 2); ctx.fill();
            break;
        }
        case 'watercolor-mix': {
            const passes = 6;
            ctx.shadowColor = color; ctx.shadowBlur = width * 0.25;
            for (let i = passes; i >= 1; i--) {
                const spread = width * (0.1 + i * 0.05);
                stroke(x0 + (Math.random() - 0.5) * spread, y0 + (Math.random() - 0.5) * spread,
                    x1 + (Math.random() - 0.5) * spread, y1 + (Math.random() - 0.5) * spread,
                    width * (0.8 + i * 0.12), opacity * p * (0.04 + 0.02 * i), 4);
            }
            stroke(x0, y0, x1, y1, width * 0.6, opacity * p * 0.22, 0);
            break;
        }
        case 'pencil-graphite':
            for (let i = 0; i < 4; i++) {
                const off = (Math.random() - 0.5) * Math.min(3, width * 0.2);
                stroke(x0 + nx * off, y0 + ny * off, x1 + nx * off, y1 + ny * off, Math.max(0.6, width * 0.22), opacity * p * 0.45, 15, 'butt');
            }
            break;
        default:
            stroke(x0,y0,x1,y1,width,opacity,0,'round');
        }
        ctx.restore();
    }

    _rgba(color) {
        const hex = String(color || '#000000').replace('#','');
        if (/^[0-9a-f]{3}$/i.test(hex)) return hex.split('').map(c=>parseInt(c+c,16));
        if (/^[0-9a-f]{6}$/i.test(hex)) return [parseInt(hex.slice(0,2),16),parseInt(hex.slice(2,4),16),parseInt(hex.slice(4,6),16)];
        return [0,0,0];
    }

    // Pincel de Mistura / Smudge (Blend de Cores)
    drawSmudge(x0, y0, x1, y1, size) {
        this.ctx.save();
        const dist = Math.hypot(x1 - x0, y1 - y0) || 1;
        const steps = Math.max(1, Math.floor(dist / (size * 0.3)));
        
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const curX = x0 + (x1 - x0) * t;
            const curY = y0 + (y1 - y0) * t;
            
            // Amostra a área anterior e espalha com desfoque
            try {
                const sampleSize = Math.max(4, Math.floor(size * 0.8));
                const sx = Math.max(0, curX - sampleSize / 2);
                const sy = Math.max(0, curY - sampleSize / 2);
                
                this.ctx.globalAlpha = 0.35;
                this.ctx.drawImage(this.ctx.canvas, sx, sy, sampleSize, sampleSize, sx - 1, sy - 1, sampleSize + 2, sampleSize + 2);
            } catch (e) {}
        }
        this.ctx.restore();
    }

    // Pincel Caligráfico / Ink
    drawCalligraphy(x0, y0, x1, y1, color, size) {
        this.ctx.save();
        this.ctx.fillStyle = color;
        this.ctx.strokeStyle = color;
        const dist = Math.hypot(x1 - x0, y1 - y0) || 1;
        const speed = Math.min(10, dist);
        const dynamicSize = Math.max(2, size * (1 - speed * 0.06));
        
        this.ctx.lineWidth = dynamicSize;
        this.ctx.lineCap = 'square';
        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.stroke();
        this.ctx.restore();
    }

    // Pincel Neon com Glow
    drawNeon(x0, y0, x1, y1, color, size, glow) {
        this.ctx.save();
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = size;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.shadowColor = color;
        this.ctx.shadowBlur = glow || 15;

        // Passada central brilhante
        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.stroke();

        // Passada interna branca para efeito de filamento
        if (size > 4) {
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = Math.max(1, size * 0.3);
            this.ctx.shadowBlur = glow * 0.5;
            this.ctx.stroke();
        }
        this.ctx.restore();
    }

    // Pincel Matrix Rain (deixa rastro de glifos orientais/binários)
    drawMatrix(x, y, color, size) {
        this.ctx.save();
        this.ctx.font = `${Math.max(12, size * 1.8)}px monospace`;
        this.ctx.fillStyle = color;
        this.ctx.shadowColor = color;
        this.ctx.shadowBlur = 10;
        
        const count = Math.max(1, Math.floor(size / 6));
        for (let i = 0; i < count; i++) {
            const char = MatrixChars[Math.floor(Math.random() * MatrixChars.length)];
            const offsetX = (Math.random() - 0.5) * size * 2;
            const offsetY = (Math.random() - 0.5) * size * 2;
            this.ctx.fillText(char, x + offsetX, y + offsetY);
        }
        this.ctx.restore();
    }

    // Pincel de Partículas Estelares
    drawParticles(x, y, color, size) {
        const count = Math.floor(size * 1.5) + 3;
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const dist = Math.random() * size * 1.8;
            const px = x + Math.cos(angle) * dist;
            const py = y + Math.sin(angle) * dist;
            const radius = Math.random() * (size * 0.25) + 1;

            this.ctx.save();
            this.ctx.fillStyle = color;
            this.ctx.shadowColor = color;
            this.ctx.shadowBlur = 8;
            this.ctx.beginPath();
            this.ctx.arc(px, py, radius, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        }
    }

    // Caleidoscópio / Simetria Radial 8x
    drawSymmetry(x0, y0, x1, y1, cx, cy, color, size, glow, count = 8) {
        const safeCount = Math.max(2, Math.min(24, Math.round(count)));
        const angles = Array.from({ length:safeCount }, (_, i) => i * Math.PI * 2 / safeCount);
        
        this.ctx.save();
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = size;
        this.ctx.lineCap = 'round';
        this.ctx.shadowColor = color;
        this.ctx.shadowBlur = glow;

        angles.forEach(angle => {
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);

            const rx0 = (x0 - cx) * cos - (y0 - cy) * sin + cx;
            const ry0 = (x0 - cx) * sin + (y0 - cy) * cos + cy;
            const rx1 = (x1 - cx) * cos - (y1 - cy) * sin + cx;
            const ry1 = (x1 - cx) * sin + (y1 - cy) * cos + cy;

            this.ctx.beginPath();
            this.ctx.moveTo(rx0, ry0);
            this.ctx.lineTo(rx1, ry1);
            this.ctx.stroke();
        });
        this.ctx.restore();
    }

    // Spray / Aerógrafo
    drawSpray(x, y, color, size) {
        this.ctx.save();
        this.ctx.fillStyle = color;
        const density = size * 3;
        for (let i = 0; i < density; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = Math.random() * size * 1.5;
            const px = x + Math.cos(angle) * radius;
            const py = y + Math.sin(angle) * radius;
            
            this.ctx.fillRect(px, py, 1.5, 1.5);
        }
        this.ctx.restore();
    }

    // Borracha
    drawEraser(x0, y0, x1, y1, size) {
        this.ctx.save();
        this.ctx.globalCompositeOperation = 'destination-out';
        this.ctx.lineWidth = size * 1.5;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.stroke();
        this.ctx.restore();
    }

    // Formas Geométricas (desenhadas no overlay ou direto)
    drawShape(ctx, shape, x0, y0, x1, y1, color, size, glow, fill = false) {
        ctx.save();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = size;
        ctx.shadowColor = color;
        ctx.shadowBlur = glow;

        ctx.beginPath();
        if (shape === 'line') {
            ctx.moveTo(x0, y0);
            ctx.lineTo(x1, y1);
        } else if (shape === 'rect') {
            const w = x1 - x0;
            const h = y1 - y0;
            if (fill) ctx.fillRect(x0, y0, w, h);
            else ctx.strokeRect(x0, y0, w, h);
            ctx.restore();
            return;
        } else if (shape === 'circle') {
            const radius = Math.hypot(x1 - x0, y1 - y0);
            ctx.arc(x0, y0, radius, 0, Math.PI * 2);
        } else if (shape === 'star') {
            const radius = Math.hypot(x1 - x0, y1 - y0);
            const spikes = 5;
            let rot = Math.PI / 2 * 3;
            let step = Math.PI / spikes;

            ctx.moveTo(x0, y0 - radius);
            for (let i = 0; i < spikes; i++) {
                let x = x0 + Math.cos(rot) * radius;
                let y = y0 + Math.sin(rot) * radius;
                ctx.lineTo(x, y);
                rot += step;

                x = x0 + Math.cos(rot) * (radius * 0.4);
                y = y0 + Math.sin(rot) * (radius * 0.4);
                ctx.lineTo(x, y);
                rot += step;
            }
            ctx.lineTo(x0, y0 - radius);
            ctx.closePath();
        }

        if (fill) ctx.fill();
        else ctx.stroke();
        ctx.restore();
    }
}
